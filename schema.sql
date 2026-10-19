-- TableTime Restaurant Reservation System
-- Database Schema for SQLite

PRAGMA foreign_keys = ON;

-- Restaurants Table
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cuisine TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    opening_time TEXT NOT NULL,
    closing_time TEXT NOT NULL,
    price_range TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK(capacity > 0)
);

-- Reservations Table
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_ref TEXT NOT NULL UNIQUE,
    restaurant_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    reservation_date TEXT NOT NULL,
    reservation_time TEXT NOT NULL,
    guest_count INTEGER NOT NULL CHECK(guest_count > 0),
    special_requests TEXT DEFAULT '',
    status TEXT NOT NULL CHECK(status IN ('Confirmed', 'Cancelled')) DEFAULT 'Confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants (id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_reservations_ref ON reservations(booking_ref);
CREATE INDEX IF NOT EXISTS idx_reservations_lookup ON reservations(booking_ref, email);
CREATE INDEX IF NOT EXISTS idx_reservations_slot ON reservations(restaurant_id, reservation_date, reservation_time, status);
