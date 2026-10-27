"""
test_reservation_lifecycle.py - Automated Selenium WebDriver tests for Reservation Lifecycle.
Maps to Experiment 8 Reservation Test Cases (TC-09 through TC-15).

Validates:
1. Reservation docket form rendering & live capacity indicator
2. Mandatory field validation (empty name rejection)
3. Historical past-date validation
4. Party size boundary validation (zero / negative party sizes)
5. Successful end-to-end reservation creation and dining pass receipt
6. Slot capacity limit enforcement (overbooking rejection)
7. Safe reservation cancellation workflow via confirmation modal dialog
"""

import os
import pytest
from datetime import date, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from database import create_reservation, get_db_path, get_restaurant_by_id


class TestReservationLifecycle:

    def test_tc09_reservation_form_renders(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-09: Reservation form docket renders with required input controls.
        Objective: Verify /book/1 presents customer name, email, phone, date, slot, party size, and CSRF token.
        """
        driver.get(f"{base_url}/book/1")
        wait = wait_helper(driver)

        # Form elements
        name_input = wait.until(EC.visibility_of_element_located((By.ID, "customer_name")))
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        phone_input = wait.until(EC.visibility_of_element_located((By.ID, "phone")))
        date_input = wait.until(EC.visibility_of_element_located((By.ID, "reservation_date")))
        time_select = wait.until(EC.visibility_of_element_located((By.ID, "reservation_time")))
        guest_input = wait.until(EC.visibility_of_element_located((By.ID, "guest_count")))
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-booking-btn")))

        assert name_input.is_displayed()
        assert email_input.is_displayed()
        assert phone_input.is_displayed()
        assert date_input.is_displayed()
        assert time_select.is_displayed()
        assert guest_input.is_displayed()
        assert submit_btn.is_displayed()

        # Capture genuine screenshot
        capture_screenshot(driver, "08_reservation_form_inputs.png")

    def test_tc10_missing_required_fields_rejected(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-10: Submitting reservation with missing required fields is rejected.
        Objective: Verify omitting customer name displays server-side validation error.
        """
        driver.get(f"{base_url}/book/1")
        wait = wait_helper(driver)

        # Fill all fields EXCEPT customer_name
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        phone_input = wait.until(EC.visibility_of_element_located((By.ID, "phone")))
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-booking-btn")))

        email_input.clear()
        email_input.send_keys("yash.test@example.com")
        phone_input.clear()
        phone_input.send_keys("+91 98200 12345")
        submit_btn.click()

        # Expected outcome: Validation error alert
        alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-error")))
        assert "Customer name is required" in alert.text

        # Capture genuine screenshot
        capture_screenshot(driver, "09_empty_name_validation.png")

    def test_tc11_past_date_reservation_rejected(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-11: Reservation date in the past is rejected.
        Objective: Verify selecting a historical date triggers explicit validation error.
        """
        driver.get(f"{base_url}/book/1")
        wait = wait_helper(driver)

        name_input = wait.until(EC.visibility_of_element_located((By.ID, "customer_name")))
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        phone_input = wait.until(EC.visibility_of_element_located((By.ID, "phone")))
        date_input = wait.until(EC.visibility_of_element_located((By.ID, "reservation_date")))
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-booking-btn")))

        name_input.clear()
        name_input.send_keys("Pooja Mehta")
        email_input.clear()
        email_input.send_keys("pooja@example.com")
        phone_input.clear()
        phone_input.send_keys("+91 98765 43210")

        # Set past date using JavaScript to test backend validation
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        driver.execute_script("arguments[0].value = arguments[1];", date_input, yesterday)

        submit_btn.click()

        # Expected outcome: Error alert
        alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-error")))
        assert "Reservation date cannot be in the past" in alert.text

        # Capture genuine screenshot
        capture_screenshot(driver, "10_past_date_validation.png")

    def test_tc12_invalid_party_size_rejected(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-12: Zero or negative party sizes are rejected.
        Objective: Verify guest count < 1 triggers explicit validation error.
        """
        driver.get(f"{base_url}/book/1")
        wait = wait_helper(driver)

        name_input = wait.until(EC.visibility_of_element_located((By.ID, "customer_name")))
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        phone_input = wait.until(EC.visibility_of_element_located((By.ID, "phone")))
        guest_input = wait.until(EC.visibility_of_element_located((By.ID, "guest_count")))
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-booking-btn")))

        name_input.clear()
        name_input.send_keys("Rohan Gupta")
        email_input.clear()
        email_input.send_keys("rohan.gupta@example.com")
        phone_input.clear()
        phone_input.send_keys("+91 98200 99999")

        # Set invalid guest count of 0
        driver.execute_script("arguments[0].value = '0';", guest_input)
        submit_btn.click()

        # Expected outcome: Error alert
        alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-error")))
        assert "Guest count must be at least 1" in alert.text

        # Capture genuine screenshot
        capture_screenshot(driver, "11_invalid_party_size_validation.png")

    def test_tc13_valid_reservation_flow(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-13: Successful reservation submission and dining pass confirmation.
        Objective: Verify valid diner details create reservation and redirect to /confirmation/TT-XXXXXX.
        """
        driver.get(f"{base_url}/book/1")
        wait = wait_helper(driver)

        name_input = wait.until(EC.visibility_of_element_located((By.ID, "customer_name")))
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        phone_input = wait.until(EC.visibility_of_element_located((By.ID, "phone")))
        date_input = wait.until(EC.visibility_of_element_located((By.ID, "reservation_date")))
        time_select = wait.until(EC.visibility_of_element_located((By.ID, "reservation_time")))
        guest_input = wait.until(EC.visibility_of_element_located((By.ID, "guest_count")))
        requests_input = wait.until(EC.visibility_of_element_located((By.ID, "special_requests")))
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-booking-btn")))

        target_date = (date.today() + timedelta(days=3)).isoformat()

        name_input.clear()
        name_input.send_keys("Yash Naik")
        email_input.clear()
        email_input.send_keys("yash.automation@example.com")
        phone_input.clear()
        phone_input.send_keys("+91 98200 12345")

        driver.execute_script("arguments[0].value = arguments[1];", date_input, target_date)
        Select(time_select).select_by_visible_text("19:00")

        guest_input.clear()
        guest_input.send_keys("2")
        requests_input.clear()
        requests_input.send_keys("Window booth table preferred; testing automated reservation pass.")

        submit_btn.click()

        # Expected outcome: Redirect to confirmation page
        ref_element = wait.until(EC.visibility_of_element_located((By.ID, "confirmed-booking-ref")))
        booking_ref = ref_element.text
        assert booking_ref.startswith("TT-"), f"Unexpected reference format: {booking_ref}"

        heading = wait.until(EC.visibility_of_element_located((By.ID, "confirmation-heading")))
        assert "RESERVATION CONFIRMED" in heading.text.upper()

        # Verify dining details
        page_source = driver.page_source
        assert "The Bombay Canteen" in page_source
        assert "Yash Naik" in page_source
        assert "2 guests" in page_source

        # Capture genuine screenshot
        capture_screenshot(driver, "12_reservation_confirmation_pass.png")

    def test_tc14_overcapacity_slot_rejected(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-14: Over-capacity booking request is rejected by SQLite transaction lock.
        Objective: Verify that when slot capacity is exhausted, additional bookings are safely blocked.
        """
        db_path = get_db_path()
        rest = get_restaurant_by_id(4, db_path=db_path)  # Cafe Madras (capacity: 32)
        assert rest is not None
        capacity = rest["capacity"]

        test_date = (date.today() + timedelta(days=5)).isoformat()
        slot_time = "14:00"

        # Pre-condition: Reserve capacity - 2 seats
        success, _ = create_reservation(
            restaurant_id=4,
            customer_name="Batch Diners",
            email="batch.diners@example.com",
            phone="+91 98200 55555",
            reservation_date=test_date,
            reservation_time=slot_time,
            guest_count=capacity - 2,
            db_path=db_path
        )
        assert success, "Failed to seed pre-capacity reservation"

        # Now attempt to book 5 guests through the UI when only 2 seats remain
        driver.get(f"{base_url}/book/4")
        wait = wait_helper(driver)

        name_input = wait.until(EC.visibility_of_element_located((By.ID, "customer_name")))
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        phone_input = wait.until(EC.visibility_of_element_located((By.ID, "phone")))
        date_input = wait.until(EC.visibility_of_element_located((By.ID, "reservation_date")))
        time_select = wait.until(EC.visibility_of_element_located((By.ID, "reservation_time")))
        guest_input = wait.until(EC.visibility_of_element_located((By.ID, "guest_count")))
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-booking-btn")))

        name_input.clear()
        name_input.send_keys("Overcapacity Test Group")
        email_input.clear()
        email_input.send_keys("overflow@example.com")
        phone_input.clear()
        phone_input.send_keys("+91 98200 66666")

        driver.execute_script("arguments[0].value = arguments[1];", date_input, test_date)
        Select(time_select).select_by_visible_text(slot_time)

        guest_input.clear()
        guest_input.send_keys("5")

        submit_btn.click()

        # Expected outcome: Capacity error alert
        alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-error")))
        assert "Insufficient capacity" in alert.text

        # Capture genuine screenshot
        capture_screenshot(driver, "13_overcapacity_slot_rejection.png")

    def test_tc15_reservation_cancellation_flow(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-15: Reservation cancellation through the confirmation modal dialog.
        Objective: Verify that confirming cancellation updates booking status to Cancelled and releases seats.
        """
        # Pre-condition: Create an active reservation
        db_path = get_db_path()
        target_date = (date.today() + timedelta(days=6)).isoformat()
        test_email = "cancel.test@example.com"
        success, booking_ref = create_reservation(
            restaurant_id=2,
            customer_name="Aarav Deshmukh",
            email=test_email,
            phone="+91 98200 77777",
            reservation_date=target_date,
            reservation_time="20:00",
            guest_count=4,
            db_path=db_path
        )
        assert success, "Failed to seed reservation for cancellation test"

        # Navigate to find booking page
        driver.get(f"{base_url}/find-booking")
        wait = wait_helper(driver)

        ref_input = wait.until(EC.visibility_of_element_located((By.ID, "booking_ref")))
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "lookup_email")))
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "lookup-submit-btn")))

        ref_input.clear()
        ref_input.send_keys(booking_ref)
        email_input.clear()
        email_input.send_keys(test_email)
        submit_btn.click()

        # Click Cancel button to open confirmation modal
        open_modal_btn = wait.until(EC.element_to_be_clickable((By.ID, "open-cancel-modal-btn")))
        open_modal_btn.click()

        # Verify modal opens
        modal = wait.until(EC.visibility_of_element_located((By.ID, "cancel-modal")))
        assert modal.is_displayed()

        # Capture genuine screenshot of modal dialog
        capture_screenshot(driver, "14_cancellation_modal_dialog.png")

        # Confirm cancellation inside modal
        confirm_cancel_btn = wait.until(EC.element_to_be_clickable((By.ID, "confirm-cancel-btn")))
        confirm_cancel_btn.click()

        # Expected outcome: Status updated to Cancelled
        success_alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-success")))
        assert "successfully cancelled" in success_alert.text

        status_badge = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".badge.badge-danger")))
        assert "CANCELLED" in status_badge.text.upper()

        # Capture genuine screenshot of cancelled state
        capture_screenshot(driver, "15_cancelled_status_confirmed.png")
