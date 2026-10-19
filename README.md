# TableTime: Restaurant Reservation System

> **Third-Year B.E. Artificial Intelligence and Data Science &mdash; Software Engineering Mini-Project**  
> Built with **Python (Flask)**, **Jinja2**, **SQLite 3**, and **Semantic HTML5/CSS3/JavaScript**.

---

## 🍽️ 1. Project Overview

**TableTime** is a lightweight, responsive, and transaction-safe web application for dining table reservations. It allows customers to discover local restaurants, check real-time seating capacity, book dining slots with instant confirmation codes, and look up or cancel reservations.

The application adheres strictly to software engineering best practices:
- **No Paid APIs or Cloud Dependencies:** Operates 100% offline after installing local Python dependencies.
- **Transaction-Safe Concurrency:** Enforces SQLite transaction locks (`BEGIN IMMEDIATE`) to eliminate overbooking.
- **Clean Student-Developer Aesthetics:** White and light-grey backgrounds, dark-slate text, royal blue highlights, clear visual hierarchy, and full mobile/tablet responsiveness.
- **Automated Test Coverage:** 10 automated test cases with 100% pass rate using `pytest` and `unittest`.
- **Comprehensive Documentation:** Full academic project report, UML diagrams, SRS requirements, and test logs.

---

## 🚀 2. System Features & Pages

| Page | URL Route | Description |
| :--- | :--- | :--- |
| **Page 1: Home** | `GET /` | TableTime branding, search bar, cuisine selector, and featured restaurant cards. |
| **Page 2: Restaurant Listing** | `GET /restaurants` | Full directory with live search, cuisine filters, operational hours, price tiers, and seating capacity. |
| **Page 3: Restaurant Details** | `GET /restaurants/<id>` | In-depth venue profile, operating hours, and 30-minute bookable time slots. |
| **Page 4: Reservation Form** | `GET, POST /book/<id>` | Accessible booking form with client & server validation, capacity checks, and CSRF protection. |
| **Page 5: Booking Confirmation** | `GET /confirmation/<ref>` | Printable receipt featuring unique reference code (`TT-XXXXXX`), arrival guidelines, and dining details. |
| **Page 6: Find My Booking** | `GET, POST /find-booking` | Dual-key lookup (Booking Ref + Email), status visibility (`Confirmed` or `Cancelled`), and cancel modal. |
| **Action: Cancel Booking** | `POST /cancel-booking/<ref>` | Safe cancellation releasing table capacity back to the restaurant. |

---

## 📁 3. Project Directory Structure

```text
restaurant-reservation-system/
├── app.py                     # Main Flask application and route handlers
├── database.py                # Database connection, queries, and capacity transactions
├── schema.sql                 # SQLite schema with constraints and performance indexes
├── seed_data.py               # 6 realistic sample restaurants with idempotent seeding
├── requirements.txt           # Python dependency specifications (Flask, pytest)
├── README.md                  # Complete setup, running, and testing guide
├── tests/
│   ├── __init__.py            # Test package marker
│   └── test_app.py            # 10 automated test cases (unittest / pytest)
├── templates/
│   ├── base.html              # Shared base layout with header, nav, flash alerts, and footer
│   ├── index.html             # Page 1: Home
│   ├── restaurants.html       # Page 2: Restaurant Listing & Search
│   ├── restaurant_details.html# Page 3: Restaurant Details & Time Slots
│   ├── booking_form.html      # Page 4: Reservation Form
│   ├── confirmation.html      # Page 5: Booking Confirmation Receipt
│   └── find_booking.html      # Page 6: Reservation Lookup & Cancellation Modal
├── static/
│   ├── css/
│   │   └── style.css          # Design system, accessible focus, responsive layouts
│   └── js/
│       └── main.js            # Dynamic slot capacity checking and modal triggers
└── docs/
    ├── requirements.md        # Software Requirements Specification (SRS)
    ├── test_cases.md          # Test execution matrix and specifications
    ├── mini_project_report.md # Academic 18-section Software Engineering report
    ├── screenshots/           # Actual high-resolution screenshots of the running app
    └── diagrams/
        ├── use_case.mmd       # Mermaid Use Case diagram
        ├── activity.mmd       # Mermaid Activity workflow diagram
        ├── sequence.mmd       # Mermaid Sequence diagram
        └── er_diagram.mmd     # Mermaid Entity-Relationship diagram
```

---

## ⚙️ 4. Prerequisites

- **Python:** Version 3.10, 3.11, or 3.12 installed on your computer.
- **Git:** (Optional) for version control.
- **Terminal:** Windows PowerShell, Command Prompt, or Bash.

To verify Python is installed, open PowerShell and execute:
```powershell
python --version
```
Expected output: `Python 3.10.x` (or newer).

---

## 💻 5. Installation & Execution (Windows PowerShell)

Follow these exact step-by-step commands in **Windows PowerShell**:

### Step 1: Navigate to Project Directory
```powershell
cd "c:\Users\Yash Naik\Downloads\restaurantUI"
```

### Step 2: Create a Python Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate the Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an Execution Policy restriction, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once, then activate again).*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Initialize Database & Seed Sample Data
The application automatically creates and seeds the database when it starts. You can also explicitly run:
```powershell
python seed_data.py
```
Expected output:
```text
Successfully seeded 6 sample restaurants.
```

### Step 6: Start the Flask Web Application
```powershell
python app.py
```
Expected output:
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Step 7: Open the Application in Your Web Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 6. Running the Automated Tests

The test suite validates positive and negative workflows, input validations, slot capacity limits, and persistence.

### Option A: Using `pytest` (Recommended)
```powershell
pytest tests/ -v
```

### Option B: Using standard Python `unittest`
```powershell
python -m unittest tests/test_app.py -v
```

### Test Results Summary:
```text
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

============================= 10 passed in 3.87s ==============================
```

---

## 🔒 7. Security, Usability & Concurrency Highlights

1. **SQL Injection Prevention:** Every query uses parameterized inputs (`?`). No string concatenation is used in SQL.
2. **CSRF Protection:** State-changing `POST` submissions require a matching session CSRF token verified via `secrets.compare_digest`.
3. **Atomic Capacity Reservation:** Booking is wrapped in SQLite `BEGIN IMMEDIATE` transactions, verifying remaining capacity before inserting to guarantee no overbooking occurs even under concurrent requests.
4. **Dual-Key Lookup Privacy:** Diners must provide both their `Booking Reference` and registered `Email` to inspect or cancel a reservation.
5. **Accessibility (WCAG 2.1 AA):** High-contrast color palette, visible `:focus-visible` keyboard rings, semantic HTML5 tags (`<main>`, `<nav>`, `<article>`, `<aside>`), and accessible labels for all form controls.

---

## 🛠️ 8. Troubleshooting & Common Issues

| Issue / Error | Cause | Solution |
| :--- | :--- | :--- |
| **`Address already in use` (Port 5000)** | Another instance of Flask or AirPlay is running on port 5000. | Stop the other process or run `app.run(port=5001)` in `app.py`. |
| **`PSSecurityException: Script Execution Disabled`** | PowerShell default script execution policy. | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the current terminal. |
| **`OperationalError: database is locked`** | A long-running write lock was held. | TableTime uses 10.0s timeouts and fast atomic transactions. Restart the app if a stale lock exists. |
| **Past Date Error on Booking** | Selected date is earlier than today's local date. | Choose today or any future calendar date. |

---

## 📚 9. Academic Mini-Project Submission Links

- **Software Requirements Specification (SRS):** [`docs/requirements.md`](docs/requirements.md)
- **Detailed Test Case Documentation:** [`docs/test_cases.md`](docs/test_cases.md)
- **Complete Academic Mini-Project Report:** [`docs/mini_project_report.md`](docs/mini_project_report.md)
- **Design Diagrams:**
  - [Use Case Diagram](docs/diagrams/use_case.mmd)
  - [Activity Diagram](docs/diagrams/activity.mmd)
  - [Sequence Diagram](docs/diagrams/sequence.mmd)
  - [Entity Relationship Diagram](docs/diagrams/er_diagram.mmd)

---

## 👥 Authors
*Third-Year B.E. Artificial Intelligence and Data Science* &bull; Academic Year 2026
