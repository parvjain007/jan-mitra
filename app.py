from flask import Flask, jsonify, send_from_directory, request , render_template
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, static_folder=".", static_url_path="")

# ---- MySQL connection settings ----
# Update these to match your MySQL server.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "parvdaddy",
    "database": "janmitra"
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def get_schemes_from_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # returns rows as dicts, like sqlite3.Row
    cursor.execute("SELECT * FROM scheme_category")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def check_match(scheme, user):
    age = int(user["age"])
    income = int(user["income"])

    if age < scheme["min_age"] or age > scheme["max_age"]:
        return False
    if scheme["max_income"] is not None and income > scheme["max_income"]:
        return False
    if scheme["states"] != "All" and scheme["states"] != user["state"]:
        return False
    if scheme["occupation"] != "Any" and scheme["occupation"] != user["occupation"]:
        return False
    if scheme["scheme_category"] != "Any" and scheme["scheme_category"] != user["schemeCategory"]:
        return False
    return True


@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/check-eligibility")
def eligibility():
    return send_from_directory(".", "eligibility.html")


@app.route("/api/check-eligibility", methods=["POST"])
def check_eligibility():
    user = request.get_json()

    schemes = get_schemes_from_db()
    matches = [scheme for scheme in schemes if check_match(scheme, user)]

    return jsonify({"matches": matches})


def insert_application(data):
    """Insert a form submission into the eligibility_applications table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO eligibility_applications
            (ea_name, ea_email, ea_mobile, ea_age, ea_state, ea_income, ea_scheme_category)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data["name"],
            data["email"],
            data["mobile"],
            data["age"],
            data["state"],
            data["income"],
            data["schemeCategory"]
        )
    )
    conn.commit()
    cursor.close()
    conn.close()

def find_existing_application(email, mobile):
    """Return the existing row if this email or mobile is already registered, else None."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT ea_id, ea_email, ea_mobile
        FROM eligibility_applications
        WHERE ea_email = %s OR ea_mobile = %s
        LIMIT 1
        """,
        (email, mobile)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

@app.route('/submit', methods=['POST'])
def submit():
    user = request.form
    selected_category = user["schemeCategory"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT scheme_name, details, benefits, scheme_category, slevel
        FROM scheme_library
        WHERE scheme_category LIKE %s
        LIMIT 20
        """,
        (f"%{selected_category}%",)
    )
    schemes = cursor.fetchall()
    cursor.close()
    conn.close()

    existing = find_existing_application(user["email"], user["mobile"])
    if not existing:
        insert_application(user)

    return render_template(
        "result.html",
        error=None,
        category=selected_category,
        schemes=schemes
    )

@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT ea_id, ea_name, ea_email, ea_mobile, ea_age, ea_state, ea_income, ea_scheme_category, ea_created_at
        FROM eligibility_applications
        ORDER BY ea_created_at DESC
        """
    )
    applications = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("dashboard.html", applications=applications)



if __name__ == "__main__":
    app.run(debug=True, port=5000)