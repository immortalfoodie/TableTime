"""
test_app.py - Automated test suite for TableTime Restaurant Reservation System.
Tests all 10 specified test cases covering successful flows, input validation,
boundary conditions, capacity limits, cancellation, and data persistence.
"""

import os
import tempfile
import unittest
from datetime import date, timedelta
import sqlite3

# Set test database path before importing app/database modules
test_db_fd, test_db_path = tempfile.mkstemp(suffix=".db")
os.close(test_db_fd)
os.environ["DATABASE_PATH"] = test_db_path

from app import app
from database import (
    init_db,
    get_db_connection,
    get_all_restaurants,
    create_reservation,
    get_reservation_by_ref,
    cancel_reservation
)


class TableTimeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SECRET_KEY"] = "test-secret-key-tabletime"

    def setUp(self):
        # Reset and seed database for each test
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        init_db(test_db_path)
        self.client = app.test_client()

    def tearDown(self):
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except PermissionError:
                pass

    def get_csrf_token(self):
        """Helper to set and return a valid CSRF token in the test client's session."""
        token = "test-csrf-token-1234"
        with self.client.session_transaction() as sess:
            sess["_csrf_token"] = token
        return token

    # -------------------------------------------------------------
    # Test 1: Restaurant listing loads successfully
    # -------------------------------------------------------------
    def test_01_restaurant_listing_loads(self):
        """Verify that the /restaurants endpoint loads with HTTP 200 and displays seeded restaurants."""
        response = self.client.get("/restaurants")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Browse Restaurants", response.data)
        self.assertIn(b"The Bombay Canteen", response.data)
        self.assertIn(b"Trishna", response.data)
        self.assertIn(b"Bastian", response.data)

    # -------------------------------------------------------------
    # Test 2: Restaurant search returns matching restaurants
    # -------------------------------------------------------------
    def test_02_restaurant_search_returns_matching(self):
        """Verify search filtering by name and cuisine returns matching restaurants only."""
        # Search for 'Canteen'
        res = self.client.get("/restaurants?search=Canteen")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"The Bombay Canteen", res.data)
        self.assertNotIn(b"Trishna", res.data)

        # Filter by cuisine 'Coastal'
        res_cuisine = self.client.get("/restaurants?cuisine=Coastal")
        self.assertEqual(res_cuisine.status_code, 200)
        self.assertIn(b"Trishna", res_cuisine.data)
        self.assertNotIn(b"Cafe Madras", res_cuisine.data)

    # -------------------------------------------------------------
    # Test 3: Valid reservation is created and stored
    # -------------------------------------------------------------
    def test_03_valid_reservation_creation(self):
        """Verify submitting valid details creates reservation in SQLite and redirects to confirmation."""
        csrf = self.get_csrf_token()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        post_data = {
            "csrf_token": csrf,
            "customer_name": "Rohan Sharma",
            "email": "rohan.sharma@example.com",
            "phone": "+91 9876543210",
            "reservation_date": tomorrow,
            "reservation_time": "13:00",
            "guest_count": "4",
            "special_requests": "Window seat preferred"
        }

        response = self.client.post("/book/1", data=post_data, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith("/confirmation/TT-"))

        # Check in database
        conn = get_db_connection(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations WHERE email = ?", ("rohan.sharma@example.com",))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row["customer_name"], "Rohan Sharma")
        self.assertEqual(row["guest_count"], 4)
        self.assertEqual(row["status"], "Confirmed")

    # -------------------------------------------------------------
    # Test 4: Reservation with missing required fields is rejected
    # -------------------------------------------------------------
    def test_04_missing_required_fields_rejected(self):
        """Verify missing customer name or email prevents reservation and displays validation error."""
        csrf = self.get_csrf_token()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        # Missing customer_name
        post_data = {
            "csrf_token": csrf,
            "customer_name": "",
            "email": "test@example.com",
            "phone": "9876543210",
            "reservation_date": tomorrow,
            "reservation_time": "12:00",
            "guest_count": "2"
        }
        res = self.client.post("/book/1", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Customer name is required", res.data)

        # Verify no reservation saved
        conn = get_db_connection(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reservations")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 0)

    # -------------------------------------------------------------
    # Test 5: Past reservation date is rejected
    # -------------------------------------------------------------
    def test_05_past_reservation_date_rejected(self):
        """Verify date in the past is rejected with explicit validation message."""
        csrf = self.get_csrf_token()
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        post_data = {
            "csrf_token": csrf,
            "customer_name": "Pooja Mehta",
            "email": "pooja@example.com",
            "phone": "9876543210",
            "reservation_date": yesterday,
            "reservation_time": "13:00",
            "guest_count": "2"
        }
        res = self.client.post("/book/1", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Reservation date cannot be in the past", res.data)

    # -------------------------------------------------------------
    # Test 6: Booking lookup succeeds with matching details
    # -------------------------------------------------------------
    def test_06_booking_lookup_success(self):
        """Verify looking up a reservation with matching reference and email displays details."""
        tomorrow = (date.today() + timedelta(days=2)).isoformat()
        success, booking_ref = create_reservation(
            restaurant_id=1,
            customer_name="Ananya Sen",
            email="ananya.sen@example.com",
            phone="9123456780",
            reservation_date=tomorrow,
            reservation_time="19:00",
            guest_count=2,
            db_path=test_db_path
        )
        self.assertTrue(success)

        csrf = self.get_csrf_token()
        res = self.client.post("/find-booking", data={
            "csrf_token": csrf,
            "booking_ref": booking_ref,
            "email": "ananya.sen@example.com"
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn(booking_ref.encode(), res.data)
        self.assertIn(b"Ananya Sen", res.data)
        self.assertIn(b"Confirmed", res.data)

    # -------------------------------------------------------------
    # Test 7: Booking lookup fails with incorrect details
    # -------------------------------------------------------------
    def test_07_booking_lookup_fails_incorrect_details(self):
        """Verify looking up with nonexistent reference or mismatched email returns helpful error."""
        csrf = self.get_csrf_token()
        res = self.client.post("/find-booking", data={
            "csrf_token": csrf,
            "booking_ref": "TT-NONEXIST",
            "email": "wrong@example.com"
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn(b"No matching reservation found", res.data)

    # -------------------------------------------------------------
    # Test 8: Reservation cancellation updates its status
    # -------------------------------------------------------------
    def test_08_reservation_cancellation_updates_status(self):
        """Verify cancelling an active reservation updates status to 'Cancelled' in SQLite."""
        tomorrow = (date.today() + timedelta(days=3)).isoformat()
        success, booking_ref = create_reservation(
            restaurant_id=2,
            customer_name="Karan Verma",
            email="karan.verma@example.com",
            phone="9876500000",
            reservation_date=tomorrow,
            reservation_time="20:00",
            guest_count=3,
            db_path=test_db_path
        )
        self.assertTrue(success)

        csrf = self.get_csrf_token()
        res = self.client.post(f"/cancel-booking/{booking_ref}", data={
            "csrf_token": csrf,
            "email": "karan.verma@example.com"
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn(b"successfully cancelled", res.data)

        # Verify in database
        res_record = get_reservation_by_ref(booking_ref, db_path=test_db_path)
        self.assertEqual(res_record["status"], "Cancelled")

    # -------------------------------------------------------------
    # Test 9: Unavailable or over-capacity booking is rejected
    # -------------------------------------------------------------
    def test_09_over_capacity_booking_rejected(self):
        """Verify booking that exceeds restaurant capacity for a slot is rejected and transaction rolls back."""
        conn = get_db_connection(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, capacity FROM restaurants WHERE name = 'Cafe Madras'")
        rest = cursor.fetchone()
        conn.close()

        rest_id = rest["id"]
        capacity = rest["capacity"]  # 32

        tomorrow = (date.today() + timedelta(days=4)).isoformat()
        slot_time = "14:00"

        # Book first batch taking up all but 2 seats: capacity - 2
        success1, ref1 = create_reservation(
            restaurant_id=rest_id,
            customer_name="Group Booking A",
            email="group.a@example.com",
            phone="9871111111",
            reservation_date=tomorrow,
            reservation_time=slot_time,
            guest_count=capacity - 2,
            db_path=test_db_path
        )
        self.assertTrue(success1)

        # Attempt to book 5 guests when only 2 seats remain
        csrf = self.get_csrf_token()
        post_data = {
            "csrf_token": csrf,
            "customer_name": "Group Booking B",
            "email": "group.b@example.com",
            "phone": "9872222222",
            "reservation_date": tomorrow,
            "reservation_time": slot_time,
            "guest_count": "5"
        }
        res = self.client.post(f"/book/{rest_id}", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Insufficient capacity", res.data)

        # Verify group B was NOT inserted into database
        conn = get_db_connection(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reservations WHERE email = 'group.b@example.com'")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 0)

    # -------------------------------------------------------------
    # Test 10: Data remains available after application restart
    # -------------------------------------------------------------
    def test_10_data_persistence_across_restart(self):
        """Verify data saved to SQLite database persists across connection resets/restarts."""
        tomorrow = (date.today() + timedelta(days=5)).isoformat()
        success, booking_ref = create_reservation(
            restaurant_id=1,
            customer_name="Persistence Test User",
            email="persist@example.com",
            phone="9876543299",
            reservation_date=tomorrow,
            reservation_time="18:00",
            guest_count=2,
            db_path=test_db_path
        )
        self.assertTrue(success)

        # Simulate complete restart by opening a new independent connection directly
        fresh_conn = sqlite3.connect(test_db_path)
        fresh_conn.row_factory = sqlite3.Row
        cursor = fresh_conn.cursor()
        cursor.execute("SELECT * FROM reservations WHERE booking_ref = ?", (booking_ref,))
        row = cursor.fetchone()
        fresh_conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row["customer_name"], "Persistence Test User")
        self.assertEqual(row["status"], "Confirmed")


if __name__ == "__main__":
    unittest.main()
