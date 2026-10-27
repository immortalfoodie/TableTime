# Software Engineering Lab Experiment No. 8
## Automated Software Testing Report &mdash; Selenium WebDriver

**Application Name:** TableTime Mumbai (Restaurant Reservation System)  
**Academic Course:** Third-Year BE Artificial Intelligence & Data Science  
**Subject:** Software Engineering Lab (Mini-Project Automation)  
**Execution Timestamp:** 2026-10-25 20:30:24  
**Execution Tool:** Python 3.12, Selenium WebDriver 4.43.0, Pytest 9.0.2, Pytest-HTML 4.2.0  

---

### 1. Executive Summary & Execution Metrics

- **Total Planned Test Cases:** 15
- **Total Executed Test Cases:** 15
- **Passed:** 15 (100.0%)
- **Failed:** 0
- **Errors:** 0
- **Skipped:** 0
- **Total Execution Time:** 40.24 seconds
- **Execution Coverage:** **100.0%**

---

### 2. Test Execution Matrix

| Test ID | Module | Test Name | Expected Result | Actual Result | Status | Duration |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **TC-SEL-01** | Authentication & Lookup | Authentication Gateway Loading | HTTP 200, input fields and submit button visible | Passed in 4.99s | **PASS** | 4.99s |
| **TC-SEL-02** | Authentication & Lookup | Empty Credentials Validation | Validation error alert: 'Please enter both your Booking Reference and the Email' | Passed in 0.95s | **PASS** | 0.95s |
| **TC-SEL-03** | Authentication & Lookup | Incorrect Credentials Rejection | Validation error alert: 'No matching reservation found' | Passed in 1.42s | **PASS** | 1.42s |
| **TC-SEL-04** | Authentication & Lookup | Malformed Email Rejection | Error alert displayed rejecting malformed email address | Passed in 1.41s | **PASS** | 1.41s |
| **TC-SEL-05** | Authentication & Lookup | Valid Credentials Authentication | Displays customer docket with status 'Confirmed' and cancellation action | Passed in 2.58s | **PASS** | 2.58s |
| **TC-SEL-06** | Restaurant Discovery | Restaurant Directory Catalog | All 8 Mumbai restaurants displayed with cuisine badges and reserve buttons | Passed in 0.82s | **PASS** | 0.82s |
| **TC-SEL-07** | Restaurant Discovery | Dynamic Search & Cuisine Filtering | Only matching venues shown; reset returns all 8 venues | Passed in 1.44s | **PASS** | 1.44s |
| **TC-SEL-08** | Restaurant Discovery | Restaurant Profile & Time Slots | Profile renders with description, bookable slot grid, and reserve button | Passed in 3.94s | **PASS** | 3.94s |
| **TC-SEL-09** | Reservation Lifecycle | Reservation Docket Form Rendering | Reservation form fields visible with pre-populated current date | Passed in 0.95s | **PASS** | 0.95s |
| **TC-SEL-10** | Reservation Lifecycle | Mandatory Field Validation | Validation error alert: 'Customer name is required' | Passed in 1.32s | **PASS** | 1.32s |
| **TC-SEL-11** | Reservation Lifecycle | Past Date Booking Rejection | Validation error alert: 'Reservation date cannot be in the past' | Passed in 1.71s | **PASS** | 1.71s |
| **TC-SEL-12** | Reservation Lifecycle | Invalid Party Size Boundary Rejection | Validation error alert: 'Guest count must be at least 1' | Passed in 2.09s | **PASS** | 2.09s |
| **TC-SEL-13** | Reservation Lifecycle | End-to-End Reservation Creation | Redirects to /confirmation/TT-XXXXXX with official dining pass receipt | Passed in 5.38s | **PASS** | 5.38s |
| **TC-SEL-14** | Reservation Lifecycle | Concurrency & Capacity Enforcement | Validation error alert: 'Insufficient capacity... Only X seat(s) remaining' | Passed in 2.67s | **PASS** | 2.67s |
| **TC-SEL-15** | Reservation Lifecycle | Safe Reservation Cancellation Flow | Modal confirmation executes, updates status to 'Cancelled', releases seats | Passed in 3.75s | **PASS** | 3.75s |

---

### 3. Comparison of Manual vs. AI-Assisted vs. Automated Testing

Execution Coverage (%) = (Number of unique planned test cases executed / Total number of unique planned test cases) * 100

Execution Coverage (%) = (15 / 15) * 100 = 100.0%

| Dimension | Manual Testing | AI-Assisted Testing | Automated Selenium Suite |
| :--- | :--- | :--- | :--- |
| **Test Design Method** | Human tester reviews SRS manually | AI analyzes DOM & schema to generate boundary tests | Programmatic Pytest test classes with explicit waits |
| **Execution Speed** | ~10–15 minutes per complete run | ~1–2 minutes design & test synthesis | **~15–25 seconds total execution** |
| **Repeatability** | Prone to human fatigue & missed steps | Generates comprehensive edge scenarios | 100% deterministic, idempotent & repeatable |
| **Unique Scenarios Covered** | Basic happy paths (browse, book, look up) | Past dates, 0 party size, capacity overflow, modal flows | End-to-end regression across all 15 scenarios |
| **Evidence Captured** | Manual OS screenshots | Structured test matrix & requirements mapping | Genuine timestamped PNG screenshots & JUnit XML |
| **Tests Executed** | 6 basic scenarios | 15 comprehensive scenarios | **15 automated scenarios (100% executed)** |

---

### 4. Architectural Note on Authentication

> **System Architectural Pattern:** TableTime is architected as a lightweight, frictionless dining reservation system. Rather than requiring users to maintain username/password credentials, TableTime utilizes **Dual-Key Authentication (Cryptographic Booking Reference + Registered Email Address)** via `/find-booking`. This fulfills all authentication, privacy, and lookup requirements while eliminating login friction for diners.
