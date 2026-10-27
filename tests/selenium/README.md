# TableTime Mumbai &mdash; Selenium Automated Test Suite
## Software Engineering Lab Experiment No. 8

> **Objective:** Automated functional and regression testing using **Python 3.12**, **Selenium WebDriver 4.43**, and **Pytest 9.0** on the **TableTime Restaurant Reservation System**.

---

## 📋 1. Prerequisites & Installation

Verify that Python is installed (Python 3.10+):
```powershell
python --version
```

Install test dependencies (including Selenium WebDriver and Pytest-HTML):
```powershell
pip install -r requirements.txt
```

*Note: Selenium 4.x includes built-in Selenium Manager, which automatically detects your installed Google Chrome or Microsoft Edge browser and manages drivers automatically without manual executable downloads.*

---

## 🚀 2. How to Start the Web Application

The test runner automatically starts the local Flask server on `http://127.0.0.1:5000` using a safe, isolated test database (`test_selenium.db`) if the application is not already running.

To start the application manually for interactive browser inspection:
```powershell
python app.py
```
Application URL: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧪 3. Executing the Selenium Test Suite

### Option A: Master Runner Script (Recommended)
Executes all 15 automated test cases in headless Chrome, collects timing data, parses JUnit XML, generates Markdown & CSV summaries, and takes a genuine screenshot of the HTML test report:
```powershell
python tests/selenium/run_selenium_tests.py
```

### Option B: Direct Pytest Command
```powershell
pytest tests/selenium/ -v --junitxml=test_artifacts/reports/junit_report.xml --html=test_artifacts/reports/selenium_test_report.html --self-contained-html
```

---

## 📁 4. Generated Artifacts & Reports Directory

All test execution artifacts are stored in `test_artifacts/`:

```text
test_artifacts/
├── reports/
│   ├── junit_report.xml             # Machine-readable JUnit XML test report
│   ├── selenium_test_report.html    # Standalone interactive HTML visual test report
│   ├── test_execution_report.md     # Academic Markdown execution report & comparison
│   └── test_execution_matrix.csv    # Tabular CSV test execution matrix
└── screenshots/
    ├── 01_auth_lookup_page.png              # TC-SEL-01: Find My Booking portal initial state
    ├── 02_empty_auth_validation.png         # TC-SEL-02: Empty lookup credentials rejection
    ├── 03_invalid_credentials_error.png     # TC-SEL-03: Nonexistent booking reference error
    ├── 04_invalid_email_validation.png      # TC-SEL-04: Malformed email syntax validation
    ├── 05_valid_auth_docket_page.png        # TC-SEL-05: Authenticated reservation docket
    ├── 06_restaurant_listing_page.png       # TC-SEL-06: 8 Mumbai restaurant directory cards
    ├── 07_restaurant_details_and_slots.png  # TC-SEL-08: Venue profile & 30-min bookable slots
    ├── 08_reservation_form_inputs.png       # TC-SEL-09: Booking docket with test inputs
    ├── 09_empty_name_validation.png         # TC-SEL-10: Missing mandatory name rejection
    ├── 10_past_date_validation.png          # TC-SEL-11: Historical date rejection alert
    ├── 11_invalid_party_size_validation.png # TC-SEL-12: Zero/negative guest count rejection
    ├── 12_reservation_confirmation_pass.png # TC-SEL-13: Official dining pass with reference
    ├── 13_overcapacity_slot_rejection.png   # TC-SEL-14: Concurrency capacity limit rejection
    ├── 14_cancellation_modal_dialog.png     # TC-SEL-15: Neo-brutalist cancellation modal
    ├── 15_cancelled_status_confirmed.png    # TC-SEL-15: Released capacity and status 'Cancelled'
    └── 16_test_execution_report.png         # Real capture of the generated HTML test report
```

---

## 🛡️ 5. Safe Test Data & Isolation

- **Test Database Isolation:** All tests run against `test_selenium.db` configured via `DATABASE_PATH` in `conftest.py`.
- **Zero Production Overwrite:** The primary production catalog (`tabletime.db`) is never modified or polluted by test runs.
- **Idempotency:** The test suite seeds fresh test dockets and tears down temporary records automatically.
