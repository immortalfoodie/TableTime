"""
seed_data.py - Populates the TableTime database with realistic sample restaurant data.
Idempotent execution: will not insert duplicate records if data already exists.
"""

SAMPLE_RESTAURANTS = [
    {
        "name": "The Spice Pavilion",
        "cuisine": "North Indian & Mughlai",
        "location": "Connaught Place, Central City",
        "description": "Authentic royal Awadhi and Mughlai delicacies cooked in traditional clay tandoors. Renowned for slow-cooked biryanis and creamy gravies.",
        "opening_time": "11:00",
        "closing_time": "23:00",
        "price_range": "₹₹₹",
        "capacity": 40
    },
    {
        "name": "Bella Trattoria",
        "cuisine": "Italian & Mediterranean",
        "location": "Indiranagar, Metro District",
        "description": "Cozy, rustic Italian dining featuring wood-fired sourdough pizzas, hand-rolled artisanal pastas, and signature tiramisu.",
        "opening_time": "12:00",
        "closing_time": "22:30",
        "price_range": "₹₹",
        "capacity": 30
    },
    {
        "name": "Golden Dragon Wok",
        "cuisine": "Chinese & Pan-Asian",
        "location": "Bandra West, Seaside Avenue",
        "description": "Vibrant Pan-Asian kitchen offering steaming Cantonese dim sums, fiery Sichuan noodles, and wok-tossed specialties in a lively ambience.",
        "opening_time": "12:30",
        "closing_time": "23:00",
        "price_range": "₹₹",
        "capacity": 35
    },
    {
        "name": "Urban Green Cafe",
        "cuisine": "Cafe & Healthy Continental",
        "location": "Koramangala, Tech Park Road",
        "description": "A relaxed urban hangout serving specialty pour-over single-origin coffees, fresh sourdough toasts, nutritious grain bowls, and handcrafted smoothies.",
        "opening_time": "09:00",
        "closing_time": "21:00",
        "price_range": "₹",
        "capacity": 24
    },
    {
        "name": "Coastline Seafood & Grill",
        "cuisine": "Seafood & Coastal",
        "location": "Marine Drive, Harbor Bay",
        "description": "Premium seaside dining showcasing fresh daily catches, coastal coconut curries, grilled prawns, and sunset views over the water.",
        "opening_time": "12:00",
        "closing_time": "22:00",
        "price_range": "₹₹₹",
        "capacity": 28
    },
    {
        "name": "Olive & Basil Bistro",
        "cuisine": "Mediterranean & Greek",
        "location": "Jubilee Hills, City Center",
        "description": "Bright, sunlit bistro serving Mediterranean mezze platters, crisp Greek salads, wood-roasted meats, and refreshing herbed mocktails.",
        "opening_time": "11:30",
        "closing_time": "22:30",
        "price_range": "₹₹",
        "capacity": 32
    }
]


def seed_database(conn):
    """
    Inserts sample restaurant records if the restaurants table is currently empty.
    Returns the number of restaurants added.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM restaurants")
    count = cursor.fetchone()[0]

    if count == 0:
        for r in SAMPLE_RESTAURANTS:
            cursor.execute(
                """
                INSERT INTO restaurants (name, cuisine, location, description, opening_time, closing_time, price_range, capacity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    r["name"],
                    r["cuisine"],
                    r["location"],
                    r["description"],
                    r["opening_time"],
                    r["closing_time"],
                    r["price_range"],
                    r["capacity"]
                )
            )
        conn.commit()
        return len(SAMPLE_RESTAURANTS)
    return 0


if __name__ == "__main__":
    import sqlite3
    from database import get_db_path, init_db

    init_db()
    conn = sqlite3.connect(get_db_path())
    added = seed_database(conn)
    conn.close()
    if added > 0:
        print(f"Successfully seeded {added} sample restaurants.")
    else:
        print("Database already contains restaurant data. No new records inserted.")
