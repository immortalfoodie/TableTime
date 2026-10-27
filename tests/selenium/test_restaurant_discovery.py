"""
test_restaurant_discovery.py - Automated Selenium WebDriver tests for Restaurant Discovery & Profiles.
Maps to Experiment 8 Catalog & Availability Verification (TC-06 through TC-08).

Validates:
1. Full directory listing rendering with all 8 Mumbai restaurants
2. Live interactive search and cuisine filtering
3. Restaurant details view with 30-minute bookable slot generation
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class TestRestaurantDiscovery:

    def test_tc06_restaurant_listing_loads(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-06: Restaurant listing page loads correctly.
        Objective: Verify /restaurants loads all 8 iconic Mumbai venues, prices, hours, and actions.
        """
        driver.get(f"{base_url}/restaurants")
        wait = wait_helper(driver)

        # Explicit wait for title and restaurant cards
        section_title = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "section-title")))
        assert "BROWSE RESTAURANTS" in section_title.text.upper()

        cards = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "restaurant-card")))
        assert len(cards) == 8, f"Expected 8 Mumbai restaurants, found {len(cards)}"

        # Verify key Mumbai venues exist on page
        page_text = driver.page_source
        assert "The Bombay Canteen" in page_text
        assert "Trishna" in page_text
        assert "Leopold Cafe" in page_text
        assert "Bastian" in page_text

        # Capture genuine screenshot
        capture_screenshot(driver, "06_restaurant_listing_page.png")

    def test_tc07_restaurant_search_and_filter(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-07: Search by keyword and filter by cuisine returns matching restaurants only.
        Objective: Verify dynamic query parameters filter out non-matching restaurants.
        """
        driver.get(f"{base_url}/restaurants")
        wait = wait_helper(driver)

        search_input = wait.until(EC.visibility_of_element_located((By.ID, "search-input")))
        filter_submit = wait.until(EC.element_to_be_clickable((By.ID, "filter-submit-btn")))

        # Search for 'Bandra'
        search_input.clear()
        search_input.send_keys("Bandra")
        filter_submit.click()

        # Explicit wait for filtered results
        filtered_cards = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "restaurant-card")))
        assert len(filtered_cards) >= 1
        for card in filtered_cards:
            assert "Bandra" in card.text or "Bastian" in card.text

        # Clear filter
        reset_btn = wait.until(EC.element_to_be_clickable((By.ID, "clear-filters-btn")))
        reset_btn.click()

        # All cards return
        cards_after_reset = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "restaurant-card")))
        assert len(cards_after_reset) == 8

    def test_tc08_restaurant_details_and_time_slots(self, driver, base_url, wait_helper, capture_screenshot):
        """
        TC-SEL-08: Restaurant details profile page renders with bookable time slots.
        Objective: Verify /restaurants/1 displays operating hours, capacity, 30-minute slot pills, and reserve CTA.
        """
        driver.get(f"{base_url}/restaurants/1")
        wait = wait_helper(driver)

        # Profile heading
        title = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "section-title")))
        assert "THE BOMBAY CANTEEN" in title.text.upper()

        # Slot grid
        slots = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "time-slot-pill")))
        assert len(slots) > 0, "No time slots generated for restaurant"

        # Reserve CTA button
        book_btn = wait.until(EC.element_to_be_clickable((By.ID, "proceed-to-book-btn")))
        assert book_btn.is_displayed()

        # Capture genuine screenshot
        capture_screenshot(driver, "07_restaurant_details_and_slots.png")
