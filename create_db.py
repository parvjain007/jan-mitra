# import sqlite3

# conn = sqlite3.connect("schemes.db")
# cursor = conn.cursor()

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS schemes (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT,
#     min_age INTEGER,
#     max_age INTEGER,
#     max_income INTEGER,
#     states TEXT,
#     occupation TEXT,
#     category TEXT,
#     benefit TEXT
# )
# """)

# conn.commit()
# conn.close()
# print("Database and table created successfully!")

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="parvdaddy",
  database="janmitra"
)

# print(mydb)
mycursor = mydb.cursor()
mycursor.execute("SHOW TABLES")
for table in mycursor:
    print(table)

