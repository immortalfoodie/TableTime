/**
 * TableTime - Client-Side Enhancements
 * Handles accessible modal dialogs, date picker restrictions,
 * and live slot availability checking.
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Enforce minimum date as today for reservation date pickers
  const dateInputs = document.querySelectorAll('input[type="date"]');
  const todayStr = new Date().toISOString().split("T")[0];

  dateInputs.forEach(function (input) {
    if (!input.getAttribute("min")) {
      input.setAttribute("min", todayStr);
    }
  });

  // 2. Cancellation Confirmation Modal Logic
  const cancelBtn = document.getElementById("open-cancel-modal-btn");
  const modal = document.getElementById("cancel-modal");
  const closeModalBtn = document.getElementById("close-modal-btn");

  if (cancelBtn && modal) {
    cancelBtn.addEventListener("click", function () {
      modal.classList.add("active");
      if (closeModalBtn) {
        closeModalBtn.focus();
      }
    });

    if (closeModalBtn) {
      closeModalBtn.addEventListener("click", function () {
        modal.classList.remove("active");
        cancelBtn.focus();
      });
    }

    // Close on overlay click
    modal.addEventListener("click", function (e) {
      if (e.target === modal) {
        modal.classList.remove("active");
      }
    });

    // Close on Escape key
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && modal.classList.contains("active")) {
        modal.classList.remove("active");
        cancelBtn.focus();
      }
    });
  }

  // 3. Live Slot Capacity Check on Booking Form
  const bookingForm = document.getElementById("reservation-form");
  if (bookingForm) {
    const restaurantId = bookingForm.getAttribute("data-restaurant-id");
    const dateSelect = document.getElementById("reservation_date");
    const timeSelect = document.getElementById("reservation_time");
    const capacityIndicator = document.getElementById("slot-capacity-indicator");
    const guestInput = document.getElementById("guest_count");

    function checkSlotAvailability() {
      if (!restaurantId || !dateSelect || !timeSelect || !capacityIndicator) {
        return;
      }

      const selectedDate = dateSelect.value;
      const selectedTime = timeSelect.value;

      if (!selectedDate || !selectedTime) return;

      capacityIndicator.textContent = "Checking availability...";
      capacityIndicator.style.color = "var(--color-text-muted)";

      fetch(`/api/restaurant/${restaurantId}/capacity?date=${encodeURIComponent(selectedDate)}&time=${encodeURIComponent(selectedTime)}`)
        .then((response) => response.json())
        .then((data) => {
          if (data.remaining_capacity !== undefined) {
            const rem = data.remaining_capacity;
            const total = data.total_capacity;

            if (rem <= 0) {
              capacityIndicator.textContent = `❌ Slot full (0 / ${total} seats remaining). Please choose another time.`;
              capacityIndicator.style.color = "var(--color-error-text)";
            } else if (rem <= 4) {
              capacityIndicator.textContent = `⚠️ Limited seating: only ${rem} seat(s) remaining for this time slot.`;
              capacityIndicator.style.color = "var(--color-warning-text)";
            } else {
              capacityIndicator.textContent = `✅ Available: ${rem} seats open for this time slot.`;
              capacityIndicator.style.color = "var(--color-success-text)";
            }

            // Adjust guest input max if limited
            if (guestInput) {
              const maxAllowed = Math.min(parseInt(guestInput.getAttribute("data-max-guests") || "12"), rem);
              if (maxAllowed > 0) {
                guestInput.max = maxAllowed;
              }
            }
          }
        })
        .catch(() => {
          capacityIndicator.textContent = "";
        });
    }

    if (dateSelect && timeSelect) {
      dateSelect.addEventListener("change", checkSlotAvailability);
      timeSelect.addEventListener("change", checkSlotAvailability);
      // Run once on load
      checkSlotAvailability();
    }
  }
});
