from flask import Flask, jsonify, send_from_directory, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "janmitra-ai-secret-key-2026-production")

# ---- Database Configuration ----
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "parvdaddy",
    "database": "janmitra"
}

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "schemes.db")


class Database:
    """Resilient database manager supporting MySQL with automatic SQLite fallback."""
    
    @staticmethod
    def get_connection():
        """Attempts to connect to MySQL; if unavailable, falls back to SQLite seamlessly."""
        if MYSQL_AVAILABLE:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                if conn.is_connected():
                    return "mysql", conn
            except Exception:
                pass
        
        # SQLite Fallback
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row  # Dict-like row access
        return "sqlite", conn

    @staticmethod
    def init_tables():
        """Ensure all required tables and default data exist in the database."""
        db_type, conn = Database.get_connection()
        cursor = conn.cursor()

        if db_type == "sqlite":
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

            # Seed demo user if missing
            cursor.execute("SELECT id FROM users WHERE email = ?", ("demo@janmitra.gov.in",))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
                """, ("Demo Citizen", "demo@janmitra.gov.in", generate_password_hash("Password@123"), "citizen"))

            conn.commit()
            cursor.close()
            conn.close()
        else:
            # MySQL setup
            try:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) DEFAULT 'citizen',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS eligibility_applications (
                    ea_id INT AUTO_INCREMENT PRIMARY KEY,
                    ea_name VARCHAR(255) NOT NULL,
                    ea_email VARCHAR(255) NOT NULL,
                    ea_mobile VARCHAR(20) NOT NULL,
                    ea_age INT NOT NULL,
                    ea_state VARCHAR(100) NOT NULL,
                    ea_income INT NOT NULL,
                    ea_scheme_category VARCHAR(255) NOT NULL,
                    ea_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                conn.commit()
            except Exception as e:
                print(f"MySQL init error: {e}")
            finally:
                cursor.close()
                conn.close()

# Initialize tables at startup
try:
    Database.init_tables()
except Exception as e:
    print(f"DB Init notice: {e}")


# ---- Helper Functions ----

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            next_url = request.url
            return redirect(f"/login?next={next_url}")
        return f(*args, **kwargs)
    return decorated_function


def get_user_by_email(email):
    db_type, conn = Database.get_connection()
    if db_type == "sqlite":
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? LIMIT 1", (email,))
        row = cursor.fetchone()
        user = dict(row) if row else None
        cursor.close()
        conn.close()
        return user
    else:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user


def create_user(name, email, password, role="citizen"):
    pwd_hash = generate_password_hash(password)
    db_type, conn = Database.get_connection()
    if db_type == "sqlite":
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (name, email, pwd_hash, role)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id, None
        except sqlite3.IntegrityError:
            return None, "An account with this email already exists."
        finally:
            cursor.close()
            conn.close()
    else:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                (name, email, pwd_hash, role)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id, None
        except Exception as e:
            return None, "An account with this email already exists or database error occurred."
        finally:
            cursor.close()
            conn.close()


def get_schemes_from_db():
    db_type, conn = Database.get_connection()
    if db_type == "sqlite":
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schemes")
        rows = [dict(r) for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return rows
    else:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM schemes")
            rows = cursor.fetchall()
        except Exception:
            cursor.execute("SELECT * FROM scheme_category")
            rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows


def check_match(scheme, user):
    try:
        age = int(user.get("age", 0))
    except (ValueError, TypeError):
        age = 0

    try:
        income = int(user.get("income", 0))
    except (ValueError, TypeError):
        income = 0

    min_age = scheme.get("min_age")
    max_age = scheme.get("max_age")
    if min_age is not None and age < min_age:
        return False
    if max_age is not None and age > max_age:
        return False

    max_income = scheme.get("max_income")
    if max_income is not None and income > max_income:
        return False

    scheme_state = scheme.get("states", "All")
    user_state = user.get("state", "All")
    if scheme_state != "All" and user_state and scheme_state.lower() != user_state.lower():
        return False

    scheme_occ = scheme.get("occupation", "Any")
    user_occ = user.get("occupation", "Any")
    if scheme_occ != "Any" and user_occ and scheme_occ.lower() != user_occ.lower():
        return False

    scheme_cat = scheme.get("category") or scheme.get("scheme_category", "Any")
    user_cat = user.get("schemeCategory") or user.get("category", "Any")
    if scheme_cat != "Any" and user_cat and scheme_cat.lower() != user_cat.lower():
        return False

    return True


def insert_application(data):
    db_type, conn = Database.get_connection()
    if db_type == "sqlite":
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO eligibility_applications
                (ea_name, ea_email, ea_mobile, ea_age, ea_state, ea_income, ea_scheme_category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("name", ""),
            data.get("email", ""),
            data.get("mobile", ""),
            data.get("age", 0),
            data.get("state", ""),
            data.get("income", 0),
            data.get("schemeCategory", "")
        ))
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO eligibility_applications
                (ea_name, ea_email, ea_mobile, ea_age, ea_state, ea_income, ea_scheme_category)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("name", ""),
            data.get("email", ""),
            data.get("mobile", ""),
            data.get("age", 0),
            data.get("state", ""),
            data.get("income", 0),
            data.get("schemeCategory", "")
        ))
        conn.commit()
        cursor.close()
        conn.close()


def find_existing_application(email, mobile):
    db_type, conn = Database.get_connection()
    if db_type == "sqlite":
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ea_id, ea_email, ea_mobile
            FROM eligibility_applications
            WHERE ea_email = ? OR ea_mobile = ?
            LIMIT 1
        """, (email, mobile))
        row = cursor.fetchone()
        res = dict(row) if row else None
        cursor.close()
        conn.close()
        return res
    else:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ea_id, ea_email, ea_mobile
            FROM eligibility_applications
            WHERE ea_email = %s OR ea_mobile = %s
            LIMIT 1
        """, (email, mobile))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row


# ---- Routes ----

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/check-eligibility")
def eligibility():
    return send_from_directory(".", "eligibility.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            session.permanent = remember
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["user_role"] = user.get("role", "citizen")
            next_url = request.args.get("next") or "/dashboard"
            return redirect(next_url)
        else:
            return render_template("login.html", error="Invalid email or password.")

    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name or not email or not password:
        return render_template("login.html", error="All fields are required.")
    if len(password) < 6:
        return render_template("login.html", error="Password must be at least 6 characters.")
    if password != confirm_password:
        return render_template("login.html", error="Passwords do not match.")

    user_id, err = create_user(name, email, password)
    if err:
        return render_template("login.html", error=err)

    session["user_id"] = user_id
    session["user_name"] = name
    session["user_email"] = email
    session["user_role"] = "citizen"
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---- Authentication API Endpoints (for AJAX / Fetch) ----

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or request.form
    email = data.get("email", "").strip()
    password = data.get("password", "")
    remember = bool(data.get("remember"))

    user = get_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        session.permanent = remember
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]
        session["user_role"] = user.get("role", "citizen")
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user.get("role", "citizen")
            }
        })
    return jsonify({"success": False, "message": "Invalid email or password."}), 401


@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or request.form
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400
    if confirm_password and password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400

    user_id, err = create_user(name, email, password)
    if err:
        return jsonify({"success": False, "message": err}), 400

    session["user_id"] = user_id
    session["user_name"] = name
    session["user_email"] = email
    session["user_role"] = "citizen"
    return jsonify({
        "success": True,
        "message": "Account created successfully",
        "user": {"id": user_id, "name": name, "email": email, "role": "citizen"}
    })


@app.route("/api/auth/status")
def auth_status():
    if "user_id" in session:
        return jsonify({
            "logged_in": True,
            "user": {
                "id": session.get("user_id"),
                "name": session.get("user_name"),
                "email": session.get("user_email"),
                "role": session.get("user_role")
            }
        })
    return jsonify({"logged_in": False, "user": None})


# ---- Scheme Eligibility & Submission Routes ----

@app.route("/api/check-eligibility", methods=["POST"])
def api_check_eligibility():
    user = request.get_json(silent=True) or request.form.to_dict()
    if not user:
        return jsonify({"error": "No user criteria provided"}), 400

    schemes = get_schemes_from_db()
    matches = [scheme for scheme in schemes if check_match(scheme, user)]
    return jsonify({"matches": matches, "total_scanned": len(schemes)})


@app.route('/submit', methods=['POST'])
def submit():
    user = request.form
    selected_category = user.get("schemeCategory", "")

    db_type, conn = Database.get_connection()
    if db_type == "sqlite":
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT scheme_name, details, benefits, eligibility_text AS eligibility, documents, level, category AS scheme_category
            FROM scheme_library
            WHERE category LIKE ? OR scheme_name LIKE ?
            LIMIT 20
            """,
            (f"%{selected_category}%", f"%{selected_category}%")
        )
        schemes = [dict(r) for r in cursor.fetchall()]
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT scheme_name, details, benefits, eligibility_text AS eligibility, documents, level, category AS scheme_category
                FROM scheme_library
                WHERE category LIKE %s OR scheme_name LIKE %s
                LIMIT 20
                """,
                (f"%{selected_category}%", f"%{selected_category}%")
            )
        except Exception:
            cursor.execute(
                """
                SELECT scheme_name, details, benefits, scheme_category, slevel AS level
                FROM scheme_library
                WHERE scheme_category LIKE %s
                LIMIT 20
                """,
                (f"%{selected_category}%",)
            )
        schemes = cursor.fetchall()
        cursor.close()
        conn.close()

    email = user.get("email")
    mobile = user.get("mobile")
    if email and mobile:
        existing = find_existing_application(email, mobile)
        if not existing:
            insert_application(user)

    return render_template(
        "result.html",
        error=None,
        category=selected_category,
        schemes=schemes
    )


@app.route("/dashboard")
@login_required
def dashboard():
    db_type, conn = Database.get_connection()
    if db_type == "sqlite":
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ea_id, ea_name, ea_email, ea_mobile, ea_age, ea_state, ea_income, ea_scheme_category, ea_created_at
            FROM eligibility_applications
            ORDER BY ea_created_at DESC
            """
        )
        applications = [dict(r) for r in cursor.fetchall()]
        cursor.close()
        conn.close()
    else:
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

    user_info = {
        "name": session.get("user_name", "Citizen"),
        "email": session.get("user_email", ""),
        "role": session.get("user_role", "citizen")
    }
    return render_template("dashboard.html", applications=applications, current_user=user_info)


# ---- Interactive AI Chat Assistant Endpoint ----

@app.route("/api/ai-chat", methods=["POST"])
def ai_chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").lower()

    if not message:
        return jsonify({"reply": "Hello! How can I help you find government schemes today?"})

    # Search keyword matching in scheme_library
    db_type, conn = Database.get_connection()
    keywords = [w for w in message.replace("?", "").replace(",", "").split() if len(w) > 3]
    results = []

    if db_type == "sqlite":
        cursor = conn.cursor()
        for kw in keywords[:3]:
            cursor.execute(
                "SELECT scheme_name, category, benefits FROM scheme_library WHERE scheme_name LIKE ? OR category LIKE ? OR details LIKE ? LIMIT 3",
                (f"%{kw}%", f"%{kw}%", f"%{kw}%")
            )
            for r in cursor.fetchall():
                results.append(dict(r))
        cursor.close()
        conn.close()

    # Deduplicate results
    unique_schemes = {}
    for r in results:
        unique_schemes[r["scheme_name"]] = r

    schemes_list = list(unique_schemes.values())[:3]
    if schemes_list:
        reply = f"Based on your query, here are relevant schemes you might qualify for:"
        return jsonify({"reply": reply, "schemes": schemes_list})
    else:
        return jsonify({
            "reply": "I analyzed your situation. For comprehensive results matching your exact age, state, and income, please check your eligibility using our 1-minute checker!",
            "schemes": []
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"JanMitra AI server starting on http://127.0.0.1:{port}")
    app.run(debug=True, host="127.0.0.1", port=port)
