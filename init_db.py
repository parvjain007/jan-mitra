"""
Database initialization and management script for JanMitra AI.
Sets up SQLite database with users, eligibility applications, and schemes.
Also includes MySQL initialization if a MySQL connection is configured.
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "schemes.db")

SAMPLE_SCHEMES = [
    {
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "min_age": 18,
        "max_age": 100,
        "max_income": 400000,
        "states": "All",
        "occupation": "Farmer",
        "category": "Agriculture",
        "benefit": "₹6,000 per year direct income support in 3 equal installments to eligible farmer families."
    },
    {
        "name": "National Means-cum-Merit Scholarship (NMMS)",
        "min_age": 12,
        "max_age": 25,
        "max_income": 350000,
        "states": "All",
        "occupation": "Student",
        "category": "Education & Learning",
        "benefit": "₹12,000 per year scholarship to meritorious students from economically weaker sections."
    },
    {
        "name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "min_age": 18,
        "max_age": 65,
        "max_income": 1000000,
        "states": "All",
        "occupation": "Business Owner",
        "category": "Business & Entrepreneurship",
        "benefit": "Collateral-free micro loans up to ₹10 Lakh for non-corporate, non-farm small/micro enterprises."
    },
    {
        "name": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        "min_age": 60,
        "max_age": 120,
        "max_income": 120000,
        "states": "All",
        "occupation": "Any",
        "category": "Social welfare & Empowerment",
        "benefit": "Monthly pension of ₹200 to ₹500 for elderly citizens living below poverty line."
    },
    {
        "name": "Ayushman Bharat - PMJAY",
        "min_age": 0,
        "max_age": 120,
        "max_income": 250000,
        "states": "All",
        "occupation": "Any",
        "category": "Health & Wellness",
        "benefit": "Health cover of up to ₹5 Lakh per family per year for secondary and tertiary care hospitalization."
    },
    {
        "name": "Pradhan Mantri Awas Yojana (PMAY - Urban / Gramin)",
        "min_age": 18,
        "max_age": 100,
        "max_income": 300000,
        "states": "All",
        "occupation": "Any",
        "category": "Housing & Shelter",
        "benefit": "Financial assistance of ₹1.20 Lakh to ₹2.67 Lakh subsidy for building pucca house."
    },
    {
        "name": "Sukanya Samriddhi Yojana (SSY)",
        "min_age": 0,
        "max_age": 21,
        "max_income": 1500000,
        "states": "All",
        "occupation": "Student",
        "category": "Women and Child",
        "benefit": "High-interest savings account with full tax exemption under Section 80C for girl children."
    },
    {
        "name": "PM SVANidhi (Street Vendor's AtmaNirbhar Nidhi)",
        "min_age": 18,
        "max_age": 70,
        "max_income": 300000,
        "states": "All",
        "occupation": "Self Employed",
        "category": "Banking",
        "benefit": "Collateral-free working capital micro-credit loan up to ₹50,000 with 7% interest subsidy."
    }
]

def init_sqlite_db():
    print(f"Connecting to SQLite database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Users table for authentication
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'citizen',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Eligibility Applications table for user submissions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eligibility_applications (
        ea_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ea_name TEXT NOT NULL,
        ea_email TEXT NOT NULL,
        ea_mobile TEXT NOT NULL,
        ea_age INTEGER NOT NULL,
        ea_state TEXT NOT NULL,
        ea_income INTEGER NOT NULL,
        ea_scheme_category TEXT NOT NULL,
        ea_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. Structured Schemes table for eligibility matching
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schemes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        min_age INTEGER,
        max_age INTEGER,
        max_income INTEGER,
        states TEXT,
        occupation TEXT,
        category TEXT,
        benefit TEXT
    )
    """)

    # Check and insert default schemes if empty
    cursor.execute("SELECT COUNT(*) FROM schemes")
    schemes_count = cursor.fetchone()[0]
    if schemes_count == 0:
        print("Populating structured schemes for eligibility checker...")
        for s in SAMPLE_SCHEMES:
            cursor.execute("""
                INSERT INTO schemes (name, min_age, max_age, max_income, states, occupation, category, benefit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["name"], s["min_age"], s["max_age"], s["max_income"],
                s["states"], s["occupation"], s["category"], s["benefit"]
            ))
        print(f"Inserted {len(SAMPLE_SCHEMES)} default schemes.")

    # Check default demo user
    cursor.execute("SELECT id FROM users WHERE email = ?", ("demo@janmitra.gov.in",))
    if not cursor.fetchone():
        demo_pwd_hash = generate_password_hash("Password@123")
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, ("Demo Citizen", "demo@janmitra.gov.in", demo_pwd_hash, "citizen"))
        print("Created demo user: demo@janmitra.gov.in (password: Password@123)")

    # Insert sample application if none exist
    cursor.execute("SELECT COUNT(*) FROM eligibility_applications")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO eligibility_applications (ea_name, ea_email, ea_mobile, ea_age, ea_state, ea_income, ea_scheme_category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("Aditi Sharma", "aditi@example.com", "9876543210", 20, "Rajasthan", 180000, "Education & Learning"))
        print("Created sample eligibility application for dashboard preview.")

    conn.commit()
    conn.close()
    print("SQLite database initialized successfully!")

if __name__ == "__main__":
    init_sqlite_db()
