"""
import_schemes.py

One-time utility script: reads schemes_data.csv (the real scheme dataset
you found) and loads it into a NEW table called `scheme_library` inside
schemes.db.

This is SEPARATE from your existing `schemes` table (the 4 hand-written
schemes your matching engine uses). scheme_library is just for search/
browse/details pages -- it does NOT have structured min_age/max_income
rules, since the real eligibility text is free-form.

HOW TO USE:
1. Place this file (import_schemes.py) in your "jan mitra" project folder,
   the same folder as app.py and schemes.db.
2. Place the CSV file in that same folder, and rename it to:
   schemes_data.csv
   (renaming just keeps things simple/consistent -- avoids typos later)
3. Run:  python import_schemes.py
4. It will print how many rows were successfully loaded.
"""

import csv
import sqlite3

DB_FILE = "schemes.db"
CSV_FILE = "schemes_data.csv"

# --- Step 1: Connect to the database (same file your other schemes live in) ---
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# --- Step 2: Create the new table (separate from your existing `schemes` table) ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS scheme_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_name TEXT,
    slug TEXT,
    details TEXT,
    benefits TEXT,
    eligibility_text TEXT,
    application_process TEXT,
    documents TEXT,
    level TEXT,
    category TEXT,
    tags TEXT
)
""")

# --- Step 3: Read the CSV and insert each row ---
rows_inserted = 0
rows_skipped = 0

with open(CSV_FILE, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            cursor.execute("""
                INSERT INTO scheme_library
                (scheme_name, slug, details, benefits, eligibility_text,
                 application_process, documents, level, category, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get("scheme_name", ""),
                row.get("slug", ""),
                row.get("details", ""),
                row.get("benefits", ""),
                row.get("eligibility", ""),
                row.get("application", ""),
                row.get("documents", ""),
                row.get("level", ""),
                row.get("schemeCategory", ""),
                row.get("tags", ""),
            ))
            rows_inserted += 1
        except Exception as e:
            # If one row is malformed, skip it instead of crashing the whole import
            rows_skipped += 1

# --- Step 4: Save changes and close ---
conn.commit()
conn.close()

print(f"Done! Inserted {rows_inserted} schemes into scheme_library.")
print(f"Skipped {rows_skipped} malformed rows.")
