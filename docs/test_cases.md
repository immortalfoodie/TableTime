# Software Testing Documentation & Test Cases
## Restaurant Reservation System &mdash; TableTime Mumbai

**Academic Course:** Third-Year BE Artificial Intelligence and Data Science  
**Subject:** Software Engineering Mini-Project  
**Testing Framework:** Python `unittest` & `pytest`  
**Execution Environment:** Python 3.12.10 on Windows (Local SQLite)  
**Execution Date:** October 2026  
**Total Test Cases:** 10 | **Passed:** 10 | **Failed:** 0 | **Pending:** 0  

---

## 1. Test Strategy & Overview

The test suite is located in [`tests/test_app.py`](../tests/test_app.py) and executes against an isolated, temporary SQLite database to ensure idempotency and test independence. The suite validates:
1. End-to-end user navigation flows (browsing, searching, reservation creation, confirmation pass receipt, lookup, and cancellation).
2. Server-side validation rules (mandatory fields, email syntax, negative party sizes, past dates).
3. Transactional concurrency control (enforcing slot capacities via `BEGIN IMMEDIATE` and rolling back overbooked attempts).
4. Data persistence across connection closures and application restarts.

---

## 2. Test Execution Matrix

| Test ID | Module / Feature | Test Condition | Expected Result | Actual Result | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | Restaurant Discovery | Load restaurant listing page (`GET /restaurants`) | HTTP 200, renders seeded Mumbai restaurants (The Bombay Canteen, Trishna, Bastian). | HTTP 200 returned, page rendered "The Bombay Canteen", "Trishna", "Bastian", etc. | **PASS** |
| **TC-02** | Search & Filtering | Search by name `?search=Canteen` & filter by cuisine `?cuisine=Coastal` | Correct subset of restaurants returned without false matches. | Returned only matching restaurants ("The Bombay Canteen" for search; "Trishna" for Coastal cuisine). | **PASS** |
| **TC-03** | Reservation Creation | Submit valid booking form (`POST /book/1`) | HTTP 302 redirect to `/confirmation/TT-...`, record stored in SQLite with status `Confirmed`. | Redirected to confirmation URL with generated booking reference, record confirmed in database. | **PASS** |
| **TC-04** | Form Validation (Required Fields) | Submit booking form with empty customer name or email | Form submission rejected, error flash message displayed, 0 records added to SQLite. | HTTP 200 returned with "Customer name is required" alert; database row count remained 0. | **PASS** |
| **TC-05** | Form Validation (Past Date) | Submit booking with reservation date in the past | Past date rejected with explicit user-friendly error message. | HTTP 200 returned with "Reservation date cannot be in the past" alert; database unchanged. | **PASS** |
| **TC-06** | Booking Lookup (Positive) | Look up booking using valid reference and matching customer email (`POST /find-booking`) | Displays full reservation summary with status `Confirmed` and cancellation trigger. | Found record displayed reference, customer name, date, time, and active cancellation button. | **PASS** |
| **TC-07** | Booking Lookup (Negative) | Look up booking with nonexistent reference or wrong email | Error message displayed; no private details exposed. | Displayed "No matching reservation found. Please check your booking reference and email address." | **PASS** |
| **TC-08** | Reservation Cancellation | Cancel an active confirmed reservation (`POST /cancel-booking/<ref>`) | Status updated to `Cancelled` in SQLite; capacity released. | Success message displayed; status changed to `Cancelled` in database. | **PASS** |
| **TC-09** | Concurrency & Capacity Limits | Attempt to book more seats than available for a specific time slot at Cafe Madras | Transaction rolls back, overbooking blocked, capacity error displayed. | Rejected with "Insufficient capacity... Only 2 seat(s) remaining for this time slot"; 0 overbooked rows inserted. | **PASS** |
| **TC-10** | Database Persistence | Access created reservation after closing and reopening SQLite connection | Reservation record persists completely with all original attributes. | Fresh connection successfully retrieved reservation record with status `Confirmed`. | **PASS** |

---

## 3. Detailed Test Case Specifications

### Test Case TC-01: Restaurant Listing Page Loads
- **Test Condition:** Verify catalog availability for public users.
- **Input / Steps:** Send `GET /restaurants`.
- **Expected Outcome:** HTTP 200 status code; HTML contains "Browse Restaurants" heading and at least 5 restaurant cards.
- **Actual Outcome:** HTTP 200; 8 Mumbai restaurants displayed with cuisines, operational hours, and capacities.
- **Pass / Fail:** **PASS**

### Test Case TC-02: Restaurant Search and Filtering
- **Test Condition:** Query parameter filtering on restaurant name and cuisine.
- **Input / Steps:**
  1. `GET /restaurants?search=Canteen`
  2. `GET /restaurants?cuisine=Coastal`
- **Expected Outcome:** Step 1 matches only "The Bombay Canteen"; Step 2 matches only "Trishna".
- **Actual Outcome:** Accurate filtering; non-matching restaurants excluded.
- **Pass / Fail:** **PASS**

### Test Case TC-03: Valid Reservation Creation
- **Test Condition:** Successful end-to-end booking submission.
- **Input / Steps:** `POST /book/1` with name="Rohan Sharma", email="rohan.sharma@example.com", phone="+91 9876543210", date=Tomorrow, time="13:00", guests=4, CSRF token.
- **Expected Outcome:** HTTP 302 redirect to `/confirmation/TT-XXXXXX`; database table `reservations` has 1 row with status='Confirmed'.
- **Actual Outcome:** Redirected to `/confirmation/TT-...`; SQLite verified 1 row inserted with status='Confirmed'.
- **Pass / Fail:** **PASS**

### Test Case TC-04: Missing Required Fields Rejection
- **Test Condition:** Server-side validation of mandatory inputs.
- **Input / Steps:** `POST /book/1` with empty `customer_name=""`.
- **Expected Outcome:** HTTP 200 (re-render form); error message "Customer name is required" displayed; no row in database.
- **Actual Outcome:** Re-rendered form with error flash message; database reservation count remained 0.
- **Pass / Fail:** **PASS**

### Test Case TC-05: Past Date Rejection
- **Test Condition:** Date validation rejecting historical dates.
- **Input / Steps:** `POST /book/1` with `reservation_date = yesterday`.
- **Expected Outcome:** Submission rejected with error message "Reservation date cannot be in the past".
- **Actual Outcome:** Re-rendered form displaying "Reservation date cannot be in the past. Please choose today or a future date."
- **Pass / Fail:** **PASS**

### Test Case TC-06: Booking Lookup with Matching Credentials
- **Test Condition:** Dual-key authentication for viewing reservations.
- **Input / Steps:** Seed reservation; send `POST /find-booking` with valid `booking_ref` and registered `email`.
- **Expected Outcome:** Page displays customer details, restaurant name, slot, and status='Confirmed'.
- **Actual Outcome:** Full details rendered accurately with active "Cancel Reservation" action.
- **Pass / Fail:** **PASS**

### Test Case TC-07: Booking Lookup with Mismatched Credentials
- **Test Condition:** Privacy protection when reference or email is incorrect.
- **Input / Steps:** `POST /find-booking` with reference="TT-NONEXIST" and email="wrong@example.com".
- **Expected Outcome:** Error message displayed; no reservation details shown.
- **Actual Outcome:** Displayed "No matching reservation found. Please check your booking reference and email address."
- **Pass / Fail:** **PASS**

### Test Case TC-08: Active Reservation Cancellation
- **Test Condition:** State transition from `Confirmed` to `Cancelled`.
- **Input / Steps:** Seed confirmed booking; submit `POST /cancel-booking/<booking_ref>` with verified email and CSRF token.
- **Expected Outcome:** Status updated to `Cancelled` in SQLite; feedback message displayed to user.
- **Actual Outcome:** Database verified status='Cancelled'; user informed with success alert.
- **Pass / Fail:** **PASS**

### Test Case TC-09: Over-Capacity / Slot Full Rejection
- **Test Condition:** Prevention of overbooking via database transaction locking (`BEGIN IMMEDIATE`).
- **Input / Steps:** Reserve `capacity - 2` seats at Cafe Madras (Capacity: 32). Then submit request for 5 seats for the same date and time.
- **Expected Outcome:** Second request rejected; error "Insufficient capacity... Only 2 seat(s) remaining"; transaction rolled back.
- **Actual Outcome:** Error message displayed; overbooked record rejected; database preserved integrity.
- **Pass / Fail:** **PASS**

### Test Case TC-10: Persistence Across Application Restarts
- **Test Condition:** Verify durability of SQLite database transactions across process termination.
- **Input / Steps:** Insert confirmed reservation; close database connection; open new independent connection and query record.
- **Expected Outcome:** Row retrieved intact with all original attributes.
- **Actual Outcome:** Record retrieved successfully with exact matching reference, guest count, and status.
- **Pass / Fail:** **PASS**

---

## 4. Test Execution Summary

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2
rootdir: C:\Users\Yash Naik\Downloads\restaurantUI

tests/test_app.py::TableTimeTestCase::test_01_restaurant_listing_loads PASSED [ 10%]
tests/test_app.py::TableTimeTestCase::test_02_restaurant_search_returns_matching PASSED [ 20%]
tests/test_app.py::TableTimeTestCase::test_03_valid_reservation_creation PASSED [ 30%]
tests/test_app.py::TableTimeTestCase::test_04_missing_required_fields_rejected PASSED [ 40%]
tests/test_app.py::TableTimeTestCase::test_05_past_reservation_date_rejected PASSED [ 50%]
tests/test_app.py::TableTimeTestCase::test_06_booking_lookup_success PASSED [ 60%]
tests/test_app.py::TableTimeTestCase::test_07_booking_lookup_fails_incorrect_details PASSED [ 70%]
tests/test_app.py::TableTimeTestCase::test_08_reservation_cancellation_updates_status PASSED [ 80%]
tests/test_app.py::TableTimeTestCase::test_09_over_capacity_booking_rejected PASSED [ 90%]
tests/test_app.py::TableTimeTestCase::test_10_data_persistence_across_restart PASSED [100%]

============================= 10 passed in 1.65s ==============================
```
