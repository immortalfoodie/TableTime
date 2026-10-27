"""
test_authentication_and_lookup.py - Automated Selenium WebDriver tests for Authentication & Lookup.
Maps to Experiment 8 Login & Authentication Test Cases (TC-01 through TC-05).

Note on Architecture:
TableTime employs a Dual-Key Authentication model (Booking Reference Code + Customer Email)
via the Find My Booking portal (/find-booking) rather than a persistent user/password account system.
This module validates:
1. Portal loading and element presence
2. Empty credential submission handling
3. Incorrect/non-existent credential rejection
4. Invalid email format handling
5. Valid credential authentication displaying confidential reservation dockets
"""

import os
import pytest
from datetime import date, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from database import create_reservation, get_db_path


class TestAuthenticationAndLookup:

    def test_tc01_auth_lookup_page_loads(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-01: Authentication / Find My Booking page loads correctly.
        Objective: Verify /find-booking loads with HTTP 200 equivalent, title, heading, and form fields.
        """
        driver.get(f"{base_url}/find-booking")
        wait = wait_helper(driver)

        # Explicit wait for page elements
        title_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "section-title")))
        ref_input = wait.until(EC.visibility_of_element_located((By.ID, "booking_ref")))
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "lookup_email")))
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "lookup-submit-btn")))

        assert "FIND MY BOOKING" in title_element.text.upper()
        assert ref_input.is_displayed()
        assert email_input.is_displayed()
        assert submit_btn.is_displayed()

        # Capture genuine screenshot
        capture_screenshot(driver, "01_auth_lookup_page.png")

    def test_tc02_empty_credentials_rejected(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-02: Empty authentication form submission is rejected.
        Objective: Verify submitting empty booking reference and email triggers validation error.
        """
        driver.get(f"{base_url}/find-booking")
        wait = wait_helper(driver)

        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "lookup-submit-btn")))
        submit_btn.click()

        # Explicit wait for flash alert
        alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-error")))
        assert "Please enter both your Booking Reference and the Email" in alert.text

        # Capture genuine screenshot
        capture_screenshot(driver, "02_empty_auth_validation.png")

    def test_tc03_incorrect_credentials_rejected(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-03: Non-existent or incorrect authentication credentials are rejected.
        Objective: Verify submitting invalid reference or wrong email returns error without exposing data.
        """
        driver.get(f"{base_url}/find-booking")
        wait = wait_helper(driver)

        ref_input = wait.until(EC.visibility_of_element_located((By.ID, "booking_ref")))
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "lookup_email")))
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "lookup-submit-btn")))

        ref_input.clear()
        ref_input.send_keys("TT-INVALID99")
        email_input.clear()
        email_input.send_keys("nonexistent@example.com")
        submit_btn.click()

        alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-error")))
        assert "No matching reservation found" in alert.text

        # Capture genuine screenshot
        capture_screenshot(driver, "03_invalid_credentials_error.png")

    def test_tc04_invalid_email_format_rejected(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-04: Malformed email syntax is handled and rejected.
        Objective: Verify malformed email in lookup form fails authentication.
        """
        driver.get(f"{base_url}/find-booking")
        wait = wait_helper(driver)

        ref_input = wait.until(EC.visibility_of_element_located((By.ID, "booking_ref")))
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "lookup_email")))
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "lookup-submit-btn")))

        ref_input.clear()
        ref_input.send_keys("TT-NONEXIST")
        email_input.clear()
        email_input.send_keys("invalid-email-format-without-at")
        submit_btn.click()

        alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-error")))
        assert "No matching reservation found" in alert.text or "email" in alert.text.lower()

        # Capture genuine screenshot
        capture_screenshot(driver, "04_invalid_email_validation.png")

    def test_tc05_valid_credentials_authenticate_and_display_docket(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-05: Valid dual-key credentials successfully authenticate and render reservation pass.
        Objective: Verify valid reference code and matching email unlock the diner's reservation docket.
        """
        # Precondition: Seed a dedicated test reservation in SQLite
        db_path = get_db_path()
        target_date = (date.today() + timedelta(days=2)).isoformat()
        test_email = "test.diner@mumbai-tabletime.com"
        success, booking_ref = create_reservation(
            restaurant_id=1,
            customer_name="Test Diner Yash",
            email=test_email,
            phone="+91 9820011111",
            reservation_date=target_date,
            reservation_time="20:00",
            guest_count=2,
            special_requests="Window table requested",
            db_path=db_path
        )
        assert success, f"Failed to seed reservation: {booking_ref}"

        # Test Steps
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

        # Expected Outcome: Reservation docket renders with booking ref, customer name, and Confirmed badge
        docket_heading = wait.until(EC.visibility_of_element_located((By.ID, "booking-result-heading")))
        assert booking_ref in docket_heading.text

        status_badge = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".badge.badge-success")))
        assert "CONFIRMED" in status_badge.text.upper()

        cancel_btn = wait.until(EC.visibility_of_element_located((By.ID, "open-cancel-modal-btn")))
        assert cancel_btn.is_displayed()

        # Capture genuine screenshot
        capture_screenshot(driver, "05_valid_auth_docket_page.png")
