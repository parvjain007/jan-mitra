"""
Database diagnostic and initialization utility for JanMitra AI.
Checks MySQL connectivity and initializes SQLite/MySQL schemas.
"""
import os
import sqlite3

print("--- JanMitra AI Database Setup & Diagnostics ---")

# 1. Try MySQL
mysql_connected = False
try:
    import mysql.connector
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="parvdaddy",
            database="janmitra"
        )
        if mydb.is_connected():
            print("[+] MySQL connection successful!")
            mycursor = mydb.cursor()
            mycursor.execute("SHOW TABLES")
            tables = [t[0] for t in mycursor.fetchall()]
            print("    MySQL Tables:", tables)
            mysql_connected = True
            mydb.close()
    except Exception as e:
        print("[-] MySQL connection not available:", e)
        print("    (This is normal if MySQL service is stopped. The app will use SQLite automatically).")
except ImportError:
    print("[-] mysql-connector not found in current environment.")

# 2. Check SQLite
sqlite_path = os.path.join(os.path.dirname(__file__), "schemes.db")
print(f"[+] Verifying SQLite database: {sqlite_path}")
conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print("    SQLite Tables:", tables)

for t in ["users", "eligibility_applications", "schemes", "scheme_library"]:
    if t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cur.fetchone()[0]
        print(f"    - Table '{t}': {cnt} rows")

conn.close()
print("All database checks complete!")
