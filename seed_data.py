"""
seed_data.py - Populates the TableTime database with famous iconic Mumbai restaurants.
Idempotent execution: will not insert duplicate records if data already exists.
"""

SAMPLE_RESTAURANTS = [
    {
        "name": "The Bombay Canteen",
        "cuisine": "Modern Regional Indian",
        "location": "Kamala Mills, Lower Parel, Mumbai",
        "description": "Celebrated culinary institution in a restored mill compound, renowned for reinventing diverse regional Indian flavors, iconic Eggs Kejriwal, and innovative craft cocktails.",
        "opening_time": "12:00",
        "closing_time": "23:30",
        "price_range": "₹₹₹",
        "capacity": 45
    },
    {
        "name": "Trishna",
        "cuisine": "Coastal Mangalorean & Seafood",
        "location": "Kala Ghoda, Fort, South Mumbai",
        "description": "Globally legendary seafood temple famous for signature butter pepper garlic crab, fresh jumbo prawns, koliwada fry, and soft neer dosas mopping up rich coastal gravies.",
        "opening_time": "12:00",
        "closing_time": "23:00",
        "price_range": "₹₹₹",
        "capacity": 36
    },
    {
        "name": "Leopold Cafe & Bar",
        "cuisine": "Heritage Cafe & Continental",
        "location": "Colaba Causeway, South Mumbai",
        "description": "Established in 1871, Mumbai's most iconic and bustling cafe landmark. Famous for hearty chicken stroganoff, chilled draught towers, spicy chili chicken, and vintage atmosphere.",
        "opening_time": "08:00",
        "closing_time": "23:30",
        "price_range": "₹₹",
        "capacity": 50
    },
    {
        "name": "Cafe Madras",
        "cuisine": "South Indian & Udupi",
        "location": "Kings Circle, Matunga, Mumbai",
        "description": "Matunga's legendary breakfast stronghold serving melt-in-the-mouth butter idlis, crispy ghee podi dosas, piping hot filter kaapi, and flavorful bisibelebath since 1940.",
        "opening_time": "07:00",
        "closing_time": "21:30",
        "price_range": "₹",
        "capacity": 32
    },
    {
        "name": "Khyber",
        "cuisine": "North-West Frontier & Mughlai",
        "location": "MG Road, Kala Ghoda, South Mumbai",
        "description": "A regal Mughal-frontier palace adorned with authentic stonework and MF Husain murals. Renowned for slow-simmered Nalli Nihari, dal makhani, and clay-oven tandoori grills.",
        "opening_time": "12:30",
        "closing_time": "23:30",
        "price_range": "₹₹₹",
        "capacity": 40
    },
    {
        "name": "Bastian",
        "cuisine": "Modern Asian & Gourmet Seafood",
        "location": "Linking Road, Bandra West, Mumbai",
        "description": "Bandra's high-energy, celebrity-favorite dining hotspot celebrated for its Singapore chili crab, lobster thermidor, avocado poke bowls, and signature decadent cheesecakes.",
        "opening_time": "12:00",
        "closing_time": "23:30",
        "price_range": "₹₹₹",
        "capacity": 48
    },
    {
        "name": "Pizza By The Bay",
        "cuisine": "Gourmet Italian & Pizzas",
        "location": "Marine Drive, Churchgate, Mumbai",
        "description": "Prime art-deco oceanfront destination overlooking Marine Drive's Queen's Necklace. Serves artisanal thin-crust pizzas, comforting pastas, and sundowner coffee with sweeping Arabian Sea views.",
        "opening_time": "11:00",
        "closing_time": "23:00",
        "price_range": "₹₹",
        "capacity": 38
    },
    {
        "name": "Gajalee",
        "cuisine": "Malvani & Maharashtrian Coastal",
        "location": "Hanuman Road, Vile Parle East, Mumbai",
        "description": "The benchmark for Konkan culinary mastery, acclaimed for rawa-fried Bombil (Bombay duck), spicy green masala stuffed pomfret, tandoori crab, and refreshing solkadhi.",
        "opening_time": "11:30",
        "closing_time": "22:30",
        "price_range": "₹₹",
        "capacity": 35
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
        print(f"Successfully seeded {added} iconic Mumbai restaurants.")
    else:
        print("Database already contains restaurant data. No new records inserted.")
