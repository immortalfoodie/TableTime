# TableTime Mumbai: Restaurant Reservation System

> **Third-Year B.E. Artificial Intelligence and Data Science &mdash; Software Engineering Mini-Project**  
> Built with **Python (Flask 3.1)**, **Jinja2**, **SQLite 3**, and **Neo-Brutalist HTML5/CSS3/JavaScript**.

---

## 🍽️ 1. Project Overview

**TableTime Mumbai** is a lightweight, responsive, and transaction-safe web platform tailored for dining table reservations across 8 iconic culinary landmarks in Mumbai. Built to eliminate the friction and double-booking errors of telephone inquiries, it allows diners to check real-time seating availability, book operational 30-minute time slots with instant confirmation dining passes (`TT-XXXXXX`), and look up or cancel reservations via self-service.

The application features:
- **Neo-Brutalist Visual Design System:** High-contrast 3px solid ink-black borders, tactile 3D press-down buttons, hard offset shadows (`5px 5px 0px #090d16`), and an electric palette featuring **Electric Indigo (`#4f46e5`)**, **Fresh Neo-Mint (`#10b981`)**, **Hot Coral (`#ff3366`)**, and **Sky Azure (`#0ea5e9`)** on a crisp dotted grid canvas. (Zero generic yellow).
- **Iconic Mumbai Dataset:** 8 legendary dining venues including *The Bombay Canteen* (Lower Parel), *Trishna* (Kala Ghoda), *Leopold Cafe & Bar* (Colaba), *Cafe Madras* (Matunga), *Khyber* (Kala Ghoda), *Bastian* (Bandra West), *Pizza By The Bay* (Marine Drive), and *Gajalee* (Vile Parle).
- **Atomic Concurrency Control:** SQLite transaction locks (`BEGIN IMMEDIATE`) eliminate race conditions and overbooking.
- **100% Offline & Free:** Requires zero paid services, cloud databases, or API keys; runs completely locally.
- **10 Automated Test Cases:** 100% pass rate using both `pytest` and Python standard `unittest`.

---

## 🚀 2. System Features & Pages

| Page | URL Route | Description |
| :--- | :--- | :--- |
| **Page 1: Home** | `GET /` | Neo-brutalist hero, quick search by locality/cuisine, and featured Mumbai restaurants. |
| **Page 2: Restaurant Listing** | `GET /restaurants` | Full directory with live search, cuisine filters, operating hours, price tiers, and seating capacity. |
| **Page 3: Restaurant Details** | `GET /restaurants/<id>` | Full venue profile, operating hours, and 30-minute bookable time slots. |
| **Page 4: Reservation Form** | `GET, POST /book/<id>` | Reservation docket with client/server validation, live slot capacity feedback, and CSRF protection. |
| **Page 5: Booking Confirmation** | `GET /confirmation/<ref>` | Retro neo-brutalist dining pass featuring unique reference code (`TT-XXXXXX`), arrival guidelines, and printable format. |
| **Page 6: Find My Booking** | `GET, POST /find-booking` | Dual-key lookup (Booking Ref + Email), status visibility (`Confirmed` or `Cancelled`), and cancel modal. |
| **Action: Cancel Booking** | `POST /cancel-booking/<ref>` | Safe cancellation releasing table capacity back to the restaurant. |

---

## 📁 3. Project Directory Structure

```text
restaurant-reservation-system/
├── app.py                     # Main Flask application and route controllers
├── database.py                # Database connection, queries, and capacity transactions
├── schema.sql                 # SQLite schema with constraints and performance indexes
├── seed_data.py               # 8 iconic Mumbai restaurants (idempotent seeding)
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
│   ├── booking_form.html      # Page 4: Reservation Form Docket
│   ├── confirmation.html      # Page 5: Booking Confirmation Dining Pass
│   └── find_booking.html      # Page 6: Reservation Lookup & Cancellation Modal
├── static/
│   ├── css/
│   │   └── style.css          # Neo-brutalist design tokens, 3D buttons, hard shadows
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
- **Web Browser:** Google Chrome, Mozilla Firefox, Microsoft Edge, or Safari.
- **Terminal:** Windows PowerShell, Command Prompt, or Bash.

To verify Python is installed:
```powershell
python --version
```

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

### Step 5: Start the Flask Web Application
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

### Step 6: Open the Application in Your Web Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 6. Running the Automated Tests

### Option A: Using `pytest` (Recommended)
```powershell
pytest tests/ -v
```

### Option B: Using standard Python `unittest`
```powershell
python -m unittest tests/test_app.py -v
```

### Verified Test Results Summary:
```text
tests/test_app.py::TableTimeTestCase::test_01_restaurant_listing_loads PASSED           [ 10%]
tests/test_app.py::TableTimeTestCase::test_02_restaurant_search_returns_matching PASSED [ 20%]
tests/test_app.py::TableTimeTestCase::test_03_valid_reservation_creation PASSED        [ 30%]
tests/test_app.py::TableTimeTestCase::test_04_missing_required_fields_rejected PASSED  [ 40%]
tests/test_app.py::TableTimeTestCase::test_05_past_reservation_date_rejected PASSED    [ 50%]
tests/test_app.py::TableTimeTestCase::test_06_booking_lookup_success PASSED            [ 60%]
tests/test_app.py::TableTimeTestCase::test_07_booking_lookup_fails_incorrect_details PASSED [ 70%]
tests/test_app.py::TableTimeTestCase::test_08_reservation_cancellation_updates_status PASSED [ 80%]
tests/test_app.py::TableTimeTestCase::test_09_over_capacity_booking_rejected PASSED    [ 90%]
tests/test_app.py::TableTimeTestCase::test_10_data_persistence_across_restart PASSED   [100%]

============================= 10 passed in 1.65s ==============================
```

---

## 🔒 7. Security, Usability & Concurrency Highlights

1. **SQL Injection Prevention:** Every query uses parameterized inputs (`?`). No string concatenation is used in SQL.
2. **CSRF Protection:** State-changing `POST` submissions require a matching session CSRF token verified via `secrets.compare_digest`.
3. **Atomic Capacity Reservation:** Booking is wrapped in SQLite `BEGIN IMMEDIATE` transactions, verifying remaining capacity before inserting to guarantee no overbooking occurs even under concurrent requests.
4. **Dual-Key Lookup Privacy:** Diners must provide both their `Booking Reference` and registered `Email` to inspect or cancel a reservation.
5. **Accessibility (WCAG 2.1 AA):** High-contrast color palette, visible `:focus-visible` keyboard rings, semantic HTML5 tags (`<main>`, `<nav>`, `<article>`, `<aside>`), and accessible labels for all form controls.

---

## 📚 8. Academic Mini-Project Submission Links

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
