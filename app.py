"""
app.py - Main Flask Application for TableTime Restaurant Reservation System.
Implements routes for browsing, booking, confirmation, lookup, and cancellation,
with server-side validation, CSRF protection, and error handling.
"""

import os
import re
import secrets
from datetime import datetime, date
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort,
    jsonify
)

from database import (
    init_db,
    get_all_restaurants,
    get_restaurant_by_id,
    get_all_cuisines,
    generate_time_slots,
    check_slot_capacity,
    create_reservation,
    get_reservation_by_ref,
    lookup_reservation,
    cancel_reservation
)

app = Flask(__name__)
# Secret key for session security and CSRF tokens
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "tabletime-secret-key-3rd-year-se-project-2026")

# Regular expression for email validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
# Regular expression for basic phone validation (7 to 15 digits, allowing optional leading +)
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-]{7,15}$")


# ==========================================
# CSRF Protection Helpers
# ==========================================
def generate_csrf_token():
    """Generates and stores a CSRF token in the user's session if not already present."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(16)
    return session["_csrf_token"]


app.jinja_env.globals["csrf_token"] = generate_csrf_token


def validate_csrf():
    """Validates the CSRF token submitted in form requests."""
    token = request.form.get("csrf_token")
    expected = session.get("_csrf_token")
    if not token or not expected or not secrets.compare_digest(token, expected):
        abort(400, description="Invalid or missing CSRF token. Please refresh the page and try again.")


# Context processor for current date
@app.context_processor
def inject_globals():
    return {
        "today_str": date.today().isoformat(),
        "current_year": datetime.now().year
    }


# ==========================================
# Routes
# ==========================================

@app.route("/")
def index():
    """
    Page 1: Home page with TableTime branding, search/filter bar,
    featured restaurants, and quick action links.
    """
    cuisines = get_all_cuisines()
    # Featured: top 3 restaurants
    all_restaurants = get_all_restaurants()
    featured = all_restaurants[:3]
    return render_template("index.html", cuisines=cuisines, featured=featured)


@app.route("/restaurants")
def restaurants():
    """
    Page 2: Restaurant Listing page with search by name/cuisine/location
    and cuisine filter dropdown.
    """
    search_query = request.args.get("search", "").strip()
    cuisine_filter = request.args.get("cuisine", "").strip()

    restaurant_list = get_all_restaurants(
        search_query=search_query,
        cuisine_filter=cuisine_filter
    )
    cuisines = get_all_cuisines()

    return render_template(
        "restaurants.html",
        restaurants=restaurant_list,
        cuisines=cuisines,
        search_query=search_query,
        selected_cuisine=cuisine_filter
    )


@app.route("/restaurants/<int:restaurant_id>")
def restaurant_details(restaurant_id):
    """
    Page 3: Restaurant Details page showing location, hours, description,
    available time slots, and a Reserve button.
    """
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        flash("Restaurant not found.", "error")
        return redirect(url_for("restaurants"))

    time_slots = generate_time_slots(restaurant["opening_time"], restaurant["closing_time"])
    return render_template("restaurant_details.html", restaurant=restaurant, time_slots=time_slots)


@app.route("/book/<int:restaurant_id>", methods=["GET", "POST"])
def book(restaurant_id):
    """
    Page 4: Reservation Form & Submission.
    Validates name, email, phone, date, time slot, guest count, and capacity.
    """
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        flash("Restaurant not found.", "error")
        return redirect(url_for("restaurants"))

    time_slots = generate_time_slots(restaurant["opening_time"], restaurant["closing_time"])
    max_guests = min(12, restaurant["capacity"])

    # Form defaults
    form_data = {
        "customer_name": "",
        "email": "",
        "phone": "",
        "reservation_date": date.today().isoformat(),
        "reservation_time": time_slots[0] if time_slots else "12:00",
        "guest_count": 2,
        "special_requests": ""
    }

    if request.method == "POST":
        validate_csrf()

        # Extract form inputs
        customer_name = request.form.get("customer_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        res_date_str = request.form.get("reservation_date", "").strip()
        res_time_str = request.form.get("reservation_time", "").strip()
        guest_count_raw = request.form.get("guest_count", "").strip()
        special_requests = request.form.get("special_requests", "").strip()

        form_data = {
            "customer_name": customer_name,
            "email": email,
            "phone": phone,
            "reservation_date": res_date_str,
            "reservation_time": res_time_str,
            "guest_count": guest_count_raw,
            "special_requests": special_requests
        }

        # Validation errors list
        errors = []

        # 1. Name validation
        if not customer_name:
            errors.append("Customer name is required.")
        elif len(customer_name) < 2 or len(customer_name) > 100:
            errors.append("Customer name must be between 2 and 100 characters.")

        # 2. Email validation
        if not email:
            errors.append("Email address is required.")
        elif not EMAIL_REGEX.match(email):
            errors.append("Please enter a valid email address (e.g., alex@example.com).")

        # 3. Phone validation
        if not phone:
            errors.append("Phone number is required.")
        elif not PHONE_REGEX.match(phone):
            errors.append("Please enter a valid phone number (7 to 15 digits).")

        # 4. Date validation
        res_date = None
        if not res_date_str:
            errors.append("Reservation date is required.")
        else:
            try:
                res_date = datetime.strptime(res_date_str, "%Y-%m-%d").date()
                if res_date < date.today():
                    errors.append("Reservation date cannot be in the past. Please choose today or a future date.")
            except ValueError:
                errors.append("Invalid date format. Expected YYYY-MM-DD.")

        # 5. Time slot validation
        if not res_time_str:
            errors.append("Reservation time slot is required.")
        elif res_time_str not in time_slots:
            errors.append(f"Selected time '{res_time_str}' is outside opening hours ({restaurant['opening_time']} - {restaurant['closing_time']}).")

        # 6. Guest count validation
        guest_count = None
        try:
            guest_count = int(guest_count_raw)
            if guest_count < 1:
                errors.append("Guest count must be at least 1.")
            elif guest_count > max_guests:
                errors.append(f"Maximum online party size is {max_guests} guests for this restaurant.")
        except (ValueError, TypeError):
            errors.append("Guest count must be a positive integer.")

        # If any validation failed, re-display form with error messages
        if errors:
            for err in errors:
                flash(err, "error")
            return render_template(
                "booking_form.html",
                restaurant=restaurant,
                time_slots=time_slots,
                max_guests=max_guests,
                form_data=form_data
            )

        # 7. Concurrency & Capacity check in Database Transaction
        success, result = create_reservation(
            restaurant_id=restaurant["id"],
            customer_name=customer_name,
            email=email,
            phone=phone,
            reservation_date=res_date_str,
            reservation_time=res_time_str,
            guest_count=guest_count,
            special_requests=special_requests
        )

        if not success:
            # Result contains capacity or database error
            flash(result, "error")
            return render_template(
                "booking_form.html",
                restaurant=restaurant,
                time_slots=time_slots,
                max_guests=max_guests,
                form_data=form_data
            )

        # Success: result is booking_ref
        booking_ref = result
        flash("Reservation successfully confirmed!", "success")
        return redirect(url_for("confirmation", booking_ref=booking_ref))

    return render_template(
        "booking_form.html",
        restaurant=restaurant,
        time_slots=time_slots,
        max_guests=max_guests,
        form_data=form_data
    )


@app.route("/confirmation/<booking_ref>")
def confirmation(booking_ref):
    """
    Page 5: Booking Confirmation page displaying unique reference,
    full details, and options to print or manage.
    """
    reservation = get_reservation_by_ref(booking_ref)
    if not reservation:
        flash("Booking reference not found.", "error")
        return redirect(url_for("find_booking"))

    return render_template("confirmation.html", reservation=reservation)


@app.route("/find-booking", methods=["GET", "POST"])
def find_booking():
    """
    Page 6: Find My Booking page.
    Look up reservations using booking reference AND email address.
    Displays reservation details and cancellation action.
    """
    reservation = None
    lookup_performed = False
    searched_ref = ""
    searched_email = ""

    if request.method == "POST":
        validate_csrf()
        searched_ref = request.form.get("booking_ref", "").strip()
        searched_email = request.form.get("email", "").strip()
        lookup_performed = True

        if not searched_ref or not searched_email:
            flash("Please enter both your Booking Reference and the Email used during booking.", "error")
        else:
            reservation = lookup_reservation(searched_ref, searched_email)
            if not reservation:
                flash("No matching reservation found. Please check your booking reference and email address.", "error")

    # Support redirecting from cancel action with query params
    ref_param = request.args.get("ref", "").strip()
    email_param = request.args.get("email", "").strip()
    if not lookup_performed and ref_param and email_param:
        searched_ref = ref_param
        searched_email = email_param
        lookup_performed = True
        reservation = lookup_reservation(searched_ref, searched_email)

    return render_template(
        "find_booking.html",
        reservation=reservation,
        lookup_performed=lookup_performed,
        searched_ref=searched_ref,
        searched_email=searched_email
    )


@app.route("/cancel-booking/<booking_ref>", methods=["POST"])
def cancel_booking(booking_ref):
    """
    Cancels an active reservation after user confirmation.
    """
    validate_csrf()
    email = request.form.get("email", "").strip()

    # Verify reservation exists and email matches
    reservation = lookup_reservation(booking_ref, email)
    if not reservation:
        flash("Invalid cancellation request: booking reference or email mismatch.", "error")
        return redirect(url_for("find_booking"))

    success, message = cancel_reservation(booking_ref)
    if success:
        flash("Your reservation has been successfully cancelled.", "success")
    else:
        flash(message, "error")

    # Redirect back to find booking page showing the updated status
    return redirect(url_for("find_booking", ref=booking_ref, email=email))


@app.route("/api/restaurant/<int:restaurant_id>/capacity")
def api_slot_capacity(restaurant_id):
    """
    API endpoint returning slot capacity for dynamic JS feedback.
    """
    res_date = request.args.get("date", date.today().isoformat())
    res_time = request.args.get("time", "")
    if not res_time:
        return jsonify({"error": "Missing time parameter"}), 400

    remaining, total = check_slot_capacity(restaurant_id, res_date, res_time)
    return jsonify({
        "restaurant_id": restaurant_id,
        "date": res_date,
        "time": res_time,
        "remaining_capacity": remaining,
        "total_capacity": total
    })


# ==========================================
# Error Handlers
# ==========================================

@app.errorhandler(400)
def bad_request(e):
    return render_template("base.html", error_title="400 - Bad Request", error_message=str(e.description)), 400


@app.errorhandler(404)
def not_found(e):
    return render_template("base.html", error_title="404 - Page Not Found", error_message="The requested page could not be found."), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("base.html", error_title="500 - Server Error", error_message="An unexpected server error occurred. Please try again later."), 500


if __name__ == "__main__":
    init_db()
    # Runs locally on port 5000
    app.run(debug=True, host="127.0.0.1", port=5000)
