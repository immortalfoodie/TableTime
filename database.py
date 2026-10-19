"""
database.py - SQLite database management for TableTime Restaurant Reservation System.
Handles schema initialization, idempotent seeding, queries with parameterized statements,
and transaction-safe reservation creation to prevent overbooking.
"""

import os
import sqlite3
import random
import string
from datetime import datetime, date, timedelta

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "tabletime.db")


def get_db_path():
    """Returns the database file path from environment or default."""
    return os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH)


def get_db_connection(db_path=None):
    """
    Creates and returns a SQLite connection with Row factory and foreign keys enabled.
    """
    path = db_path or get_db_path()
    conn = sqlite3.connect(path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=None):
    """
    Initializes database tables from schema.sql and seeds initial restaurants.
    Safe to call multiple times (idempotent).
    """
    path = db_path or get_db_path()
    schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")

    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db_connection(path)
    try:
        conn.executescript(schema_sql)
        from seed_data import seed_database
        seed_database(conn)
    finally:
        conn.close()


def generate_time_slots(opening_time_str, closing_time_str, interval_minutes=30):
    """
    Generates time slots (HH:MM) between opening and closing time.
    Last bookable slot is interval_minutes before closing.
    """
    try:
        open_time = datetime.strptime(opening_time_str, "%H:%M")
        close_time = datetime.strptime(closing_time_str, "%H:%M")
    except ValueError:
        return []

    # If closing is past midnight or same day
    if close_time <= open_time:
        close_time += timedelta(days=1)

    slots = []
    current = open_time
    # Stop before closing time so guests have time to dine
    cutoff = close_time - timedelta(minutes=interval_minutes)

    while current <= cutoff:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=interval_minutes)

    return slots


def get_all_restaurants(search_query=None, cuisine_filter=None, db_path=None):
    """
    Fetches restaurants matching optional search query (name/location/cuisine)
    and optional cuisine filter.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM restaurants WHERE 1=1"
        params = []

        if cuisine_filter and cuisine_filter.strip() and cuisine_filter.strip().lower() != "all":
            query += " AND cuisine LIKE ?"
            params.append(f"%{cuisine_filter.strip()}%")

        if search_query and search_query.strip():
            sq = f"%{search_query.strip()}%"
            query += " AND (name LIKE ? OR cuisine LIKE ? OR location LIKE ?)"
            params.extend([sq, sq, sq])

        query += " ORDER BY name ASC"
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()


def get_restaurant_by_id(restaurant_id, db_path=None):
    """Fetches a single restaurant by primary key ID."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM restaurants WHERE id = ?", (restaurant_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_all_cuisines(db_path=None):
    """Returns a sorted list of unique primary cuisines for filtering."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT cuisine FROM restaurants ORDER BY cuisine ASC")
        rows = cursor.fetchall()
        cuisines = set()
        for row in rows:
            # Split if multiple listed (e.g. 'North Indian & Mughlai')
            parts = [c.strip() for c in row["cuisine"].replace("&", ",").split(",")]
            for p in parts:
                if p:
                    cuisines.add(p)
        return sorted(list(cuisines))
    finally:
        conn.close()


def generate_unique_booking_ref(conn):
    """
    Generates a unique, user-friendly booking reference like 'TT-74B92C'.
    Guaranteed unique in the database.
    """
    chars = string.ascii_uppercase + string.digits
    for _ in range(100):
        code = "".join(random.choice(chars) for _ in range(6))
        ref = f"TT-{code}"
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM reservations WHERE booking_ref = ?", (ref,))
        if not cursor.fetchone():
            return ref
    # Fallback with timestamp
    return f"TT-{int(datetime.now().timestamp())}"


def check_slot_capacity(restaurant_id, reservation_date, reservation_time, db_path=None):
    """
    Returns (remaining_capacity, total_capacity) for a given restaurant slot.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT capacity FROM restaurants WHERE id = ?", (restaurant_id,))
        row = cursor.fetchone()
        if not row:
            return 0, 0
        total_capacity = row["capacity"]

        cursor.execute(
            """
            SELECT COALESCE(SUM(guest_count), 0)
            FROM reservations
            WHERE restaurant_id = ?
              AND reservation_date = ?
              AND reservation_time = ?
              AND status = 'Confirmed'
            """,
            (restaurant_id, reservation_date, reservation_time)
        )
        booked = cursor.fetchone()[0]
        remaining = max(0, total_capacity - booked)
        return remaining, total_capacity
    finally:
        conn.close()


def create_reservation(
    restaurant_id,
    customer_name,
    email,
    phone,
    reservation_date,
    reservation_time,
    guest_count,
    special_requests="",
    db_path=None
):
    """
    Transaction-safe reservation creation with concurrency check.
    Uses 'BEGIN IMMEDIATE' to lock the database during capacity check and insertion.
    Returns (True, booking_ref) on success, or (False, error_message) on failure.
    """
    conn = get_db_connection(db_path)
    try:
        # SQLite transaction lock to prevent race conditions during booking
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()

        # 1. Verify restaurant exists
        cursor.execute("SELECT capacity, opening_time, closing_time FROM restaurants WHERE id = ?", (restaurant_id,))
        rest = cursor.fetchone()
        if not rest:
            conn.rollback()
            return False, "Selected restaurant does not exist."

        total_capacity = rest["capacity"]

        # 2. Check current booked guests
        cursor.execute(
            """
            SELECT COALESCE(SUM(guest_count), 0)
            FROM reservations
            WHERE restaurant_id = ?
              AND reservation_date = ?
              AND reservation_time = ?
              AND status = 'Confirmed'
            """,
            (restaurant_id, reservation_date, reservation_time)
        )
        already_booked = cursor.fetchone()[0]
        remaining = total_capacity - already_booked

        if guest_count > remaining:
            conn.rollback()
            if remaining <= 0:
                return False, f"Sorry, this time slot is completely booked. Total capacity: {total_capacity} guests."
            return False, f"Insufficient capacity for {guest_count} guests. Only {remaining} seat(s) remaining for this time slot."

        # 3. Generate unique booking reference
        booking_ref = generate_unique_booking_ref(conn)

        # 4. Insert reservation
        cursor.execute(
            """
            INSERT INTO reservations (
                booking_ref, restaurant_id, customer_name, email, phone,
                reservation_date, reservation_time, guest_count, special_requests, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed')
            """,
            (
                booking_ref,
                restaurant_id,
                customer_name.strip(),
                email.strip().lower(),
                phone.strip(),
                reservation_date,
                reservation_time,
                guest_count,
                special_requests.strip() if special_requests else ""
            )
        )

        conn.commit()
        return True, booking_ref
    except Exception as e:
        conn.rollback()
        return False, f"Database error occurred: {str(e)}"
    finally:
        conn.close()


def get_reservation_by_ref(booking_ref, db_path=None):
    """
    Fetches full reservation details including restaurant info by booking reference.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.*,
                   res.name AS restaurant_name,
                   res.cuisine,
                   res.location,
                   res.price_range
            FROM reservations r
            JOIN restaurants res ON r.restaurant_id = res.id
            WHERE r.booking_ref = ?
            """,
            (booking_ref.strip().upper(),)
        )
        return cursor.fetchone()
    finally:
        conn.close()


def lookup_reservation(booking_ref, email, db_path=None):
    """
    Finds a reservation matching both booking reference AND customer email.
    Case-insensitive on both reference and email.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.*,
                   res.name AS restaurant_name,
                   res.cuisine,
                   res.location,
                   res.price_range
            FROM reservations r
            JOIN restaurants res ON r.restaurant_id = res.id
            WHERE UPPER(r.booking_ref) = UPPER(?)
              AND LOWER(r.email) = LOWER(?)
            """,
            (booking_ref.strip(), email.strip())
        )
        return cursor.fetchone()
    finally:
        conn.close()


def cancel_reservation(booking_ref, db_path=None):
    """
    Cancels an active confirmed reservation.
    Returns (True, "Reservation cancelled successfully.") or (False, reason).
    """
    conn = get_db_connection(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM reservations WHERE UPPER(booking_ref) = UPPER(?)", (booking_ref.strip(),))
        row = cursor.fetchone()

        if not row:
            conn.rollback()
            return False, "Reservation not found."

        if row["status"] == "Cancelled":
            conn.rollback()
            return False, "This reservation has already been cancelled."

        cursor.execute(
            "UPDATE reservations SET status = 'Cancelled' WHERE UPPER(booking_ref) = UPPER(?)",
            (booking_ref.strip(),)
        )
        conn.commit()
        return True, "Reservation cancelled successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Failed to cancel reservation: {str(e)}"
    finally:
        conn.close()
