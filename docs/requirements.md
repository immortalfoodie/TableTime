# Software Requirements Specification (SRS)
## Restaurant Reservation System &mdash; TableTime

**Academic Course:** Third-Year BE Artificial Intelligence and Data Science  
**Subject:** Software Engineering Mini-Project  
**Application Name:** TableTime  
**Version:** 1.0.0  

---

## 1. Introduction

### 1.1 Purpose
The purpose of TableTime is to provide an intuitive, reliable, and accessible web-based platform where customers can discover dining establishments, view operational hours and seating capacities, reserve available time slots in real time, and manage or cancel reservations independently.

### 1.2 Problem Statement
Traditional restaurant table booking predominantly relies on telephone calls or walk-ins. This manual approach is susceptible to human errors, double booking, scheduling conflicts, and customer inconvenience during peak rush hours. TableTime automates the booking lifecycle, enforcing database-level concurrency control to eliminate overbooking and providing instant booking references for customers.

### 1.3 Scope
TableTime addresses three foundational functionalities:
1. **Browse and Search Restaurants**: Search by name or location and filter by cuisine type.
2. **Make a Reservation**: Select valid date, time slot, guest count, and submit verified contact details.
3. **View and Cancel Reservations**: Retrieve booking status via booking reference and customer email; cancel confirmed bookings with status updates and capacity release.

Commercial complexities such as online payment processing, food ordering, customer loyalty tiers, and external third-party integrations are deliberately excluded to maintain an academic, demonstrable, and clean project scope.

---

## 2. User Roles and Characteristics

| User Role | Description | Key Actions |
| :--- | :--- | :--- |
| **Diner / Customer** | End user visiting the application to book dining tables. | Searches restaurants, books tables, views confirmation receipt, checks reservation status, cancels reservations. |
| **Evaluator / Faculty** | Academic evaluator reviewing system design, database transactions, test suites, and viva concepts. | Inspects schema, validates test execution, verifies transaction-safe capacity enforcement. |

---

## 3. Functional Requirements (FR)

### Module 1: Restaurant Discovery & Search
- **FR-01 (Catalog Browsing):** The system shall display a list of all active restaurants, including name, cuisine, location, opening/closing hours, price tier, and seating capacity.
- **FR-02 (Keyword Search):** The system shall allow users to search restaurants by name, cuisine, or location using case-insensitive pattern matching.
- **FR-03 (Cuisine Filtering):** The system shall provide a dropdown filter enabling users to view restaurants belonging to specific culinary categories.
- **FR-04 (Restaurant Profile):** The system shall present an individual restaurant details page displaying full descriptive information and calculated 30-minute bookable time slots.

### Module 2: Table Reservation
- **FR-05 (Input Collection):** The reservation form shall collect the customer's full name, email address, phone number, date of visit, time slot, guest count, and optional special requests.
- **FR-06 (Input Validation):**
  - All mandatory fields must be validated server-side.
  - Customer email must adhere to valid format standards (`name@domain.tld`).
  - Phone number must contain between 7 and 15 valid digits.
  - Reservation date must not be prior to the current date (`reservation_date >= today`).
  - Time slot must fall within the restaurant's configured operating hours.
  - Guest count must be a positive integer within configured online booking limits.
- **FR-07 (Capacity & Concurrency Check):** The system must execute capacity verification and reservation insertion within an isolated database transaction (`BEGIN IMMEDIATE` in SQLite) to prevent race conditions and overbooking.
- **FR-08 (Unique Booking Reference):** The system shall generate a cryptographically unique alphanumeric booking reference code (e.g., `TT-A8F4D2`) for each successful reservation.
- **FR-09 (Confirmation Receipt):** The system shall present a dedicated confirmation page showing complete booking details, reference code, arrival guidelines, and a printable receipt view.

### Module 3: Reservation Lookup & Cancellation
- **FR-10 (Dual-Key Lookup):** The system shall allow users to retrieve their reservation details using both their unique booking reference and their registered email address.
- **FR-11 (Status Visibility):** The lookup page shall clearly display whether the reservation is `Confirmed` or `Cancelled`.
- **FR-12 (Safe Cancellation):** The system shall provide a cancellation mechanism with a confirmation modal dialog. Upon cancellation, the reservation status is updated to `Cancelled`, and table capacity is immediately released back to the restaurant.

---

## 4. Non-Functional Requirements (NFR)

- **NFR-01 (Performance & Latency):** Typical database queries and page render times must execute within under 100 milliseconds on a standard personal computer.
- **NFR-02 (Usability & Design):** The interface shall employ clean typography, consistent spacing, light backgrounds (`#f8fafc`), dark-slate text (`#0f172a`), and royal blue interactive elements (`#2563eb`), conforming to a professional student developer design system.
- **NFR-03 (Accessibility):** Semantic HTML5 elements (`<header>`, `<main>`, `<article>`, `<nav>`, `<aside>`, `<footer>`), explicit form labels, visible focus outlines, and high text contrast must be strictly maintained.
- **NFR-04 (Security & Injection Prevention):** All SQL statements must utilize parameterized bindings (`?`) to prevent SQL injection vulnerabilities. Cross-Site Request Forgery (CSRF) tokens must protect state-changing POST requests.
- **NFR-05 (Portability & Zero Cloud Cost):** The application must run completely offline on Windows, macOS, or Linux using standard Python and SQLite without requiring paid API keys or cloud services.
- **NFR-06 (Data Persistence):** All committed reservation records and restaurant catalog data must persist across application restarts in an SQLite database file.
- **NFR-07 (Testability):** The backend must provide automated test coverage validating positive workflows, negative input rejections, boundary checks, and transaction rollbacks.

---

## 5. Technology Constraints
- **Backend Framework:** Python 3.10+ with Flask.
- **Database Engine:** SQLite 3 with foreign key enforcement enabled (`PRAGMA foreign_keys = ON`).
- **Templating Engine:** Jinja2.
- **Frontend Stack:** HTML5, CSS3, Vanilla JavaScript (no heavy frontend frameworks required).
- **Test Framework:** Python standard `unittest` and `pytest`.
