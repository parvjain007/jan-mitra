from flask import Flask, jsonify, send_from_directory, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import random
import string
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
        """Ensure all required tables and default users exist in the database."""
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

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS applied_schemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_email TEXT NOT NULL,
                user_name TEXT,
                scheme_name TEXT NOT NULL,
                scheme_category TEXT,
                reference_no TEXT UNIQUE,
                status TEXT DEFAULT 'Under Review',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Seed demo citizen
            cursor.execute("SELECT id FROM users WHERE email = ?", ("demo@janmitra.gov.in",))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
                """, ("Demo Citizen", "demo@janmitra.gov.in", generate_password_hash("Password@123"), "citizen"))

            # Seed admin user
            cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@janmitra.gov.in",))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
                """, ("System Administrator", "admin@janmitra.gov.in", generate_password_hash("Admin@123"), "admin"))
            else:
                cursor.execute("UPDATE users SET role = 'admin' WHERE email = 'admin@janmitra.gov.in'")

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
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS applied_schemes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    user_email VARCHAR(255) NOT NULL,
                    user_name VARCHAR(255),
                    scheme_name VARCHAR(255) NOT NULL,
                    scheme_category VARCHAR(255),
                    reference_no VARCHAR(100) UNIQUE,
                    status VARCHAR(50) DEFAULT 'Under Review',
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


# ---- Helper Functions & Decorators ----

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            next_url = request.url
            return redirect(f"/login?next={next_url}")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Authentication required."}), 401
            return redirect("/login?next=/admin")
        if session.get("user_role") != "admin":
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Admin authorization required."}), 403
            return redirect("/dashboard")
        return f(*args, **kwargs)
    return decorated_function


def generate_reference_no():
    """Generates a human-friendly unique application reference number."""
    digits = "".join(random.choices(string.digits, k=5))
    return f"JM-2026-{digits}"


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
        except Exception:
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


# ---- Core Routes ----

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

            default_target = "/admin" if user.get("role") == "admin" else "/dashboard"
            next_url = request.args.get("next") or default_target
            return redirect(next_url)
        else:
            return render_template("login.html", error="Invalid email or password.")

    if "user_id" in session:
        if session.get("user_role") == "admin":
            return redirect("/admin")
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---- Authentication API Endpoints ----

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

        target_redirect = "/admin" if user.get("role") == "admin" else "/dashboard"
        return jsonify({
            "success": True,
            "message": "Login successful",
            "redirect": target_redirect,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user.get("role", "citizen")
            }
        })
    return jsonify({"success": False, "message": "Invalid email or password."}), 401


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


# ---- Scheme Eligibility & Application Submission ----

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
    """
    Submits eligibility details and registers the citizen account.
    """
    user = request.form
    name = user.get("name", "").strip()
    email = user.get("email", "").strip()
    mobile = user.get("mobile", "").strip()
    selected_category = user.get("schemeCategory", "")
    password = user.get("password", "").strip()

    # 1. Fetch matching schemes from scheme_library
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

    # 2. Save application to eligibility_applications
    if email:
        existing = find_existing_application(email, mobile)
        if not existing:
            insert_application(user)

        # 3. Create or update User Account
        existing_user = get_user_by_email(email)
        if not existing_user:
            reg_pwd = password if password else "Password@123"
            user_id, _ = create_user(name, email, reg_pwd, role="citizen")
        else:
            user_id = existing_user["id"]
            if password:
                db_t, c = Database.get_connection()
                if db_t == "sqlite":
                    cur = c.cursor()
                    cur.execute("UPDATE users SET password_hash = ? WHERE id = ?", (generate_password_hash(password), user_id))
                    c.commit()
                    cur.close()
                else:
                    cur = c.cursor()
                    cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (generate_password_hash(password), user_id))
                    c.commit()
                    cur.close()
                c.close()

        # Log citizen into session
        session["user_id"] = user_id
        session["user_name"] = name
        session["user_email"] = email
        session["user_role"] = "citizen"

    # Get user's already applied schemes if any
    applied_names = set()
    if "user_email" in session:
        db_type, conn = Database.get_connection()
        if db_type == "sqlite":
            c = conn.cursor()
            c.execute("SELECT scheme_name FROM applied_schemes WHERE user_email = ?", (session["user_email"],))
            applied_names = {row["scheme_name"] for row in c.fetchall()}
            c.close()
            conn.close()

    return render_template(
        "result.html",
        error=None,
        category=selected_category,
        schemes=schemes,
        applied_names=applied_names
    )


# ---- Scheme Application Endpoint (Apply for Multiple Schemes) ----

@app.route("/api/apply-scheme", methods=["POST"])
def api_apply_scheme():
    """
    Allows a citizen to apply for multiple schemes.
    Stores the application with unique reference number.
    """
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in to apply for government welfare schemes.",
            "require_login": True
        }), 401

    data = request.get_json(silent=True) or request.form
    scheme_name = data.get("scheme_name", "").strip()
    scheme_category = data.get("scheme_category", "").strip()

    if not scheme_name:
        return jsonify({"success": False, "message": "Scheme name is required."}), 400

    user_id = session.get("user_id")
    user_email = session.get("user_email")
    user_name = session.get("user_name", "Citizen")

    db_type, conn = Database.get_connection()
    ref_no = None

    if db_type == "sqlite":
        cursor = conn.cursor()
        # Check if already applied
        cursor.execute(
            "SELECT id, reference_no, status, applied_at FROM applied_schemes WHERE user_email = ? AND scheme_name = ?",
            (user_email, scheme_name)
        )
        existing = cursor.fetchone()
        if existing:
            ref_no = existing["reference_no"]
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "already_applied": True,
                "message": f"You have already applied for '{scheme_name}'.",
                "reference_no": ref_no,
                "status": existing["status"]
            })

        # Insert new scheme application
        ref_no = generate_reference_no()
        cursor.execute(
            """
            INSERT INTO applied_schemes (user_id, user_email, user_name, scheme_name, scheme_category, reference_no, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, user_email, user_name, scheme_name, scheme_category, ref_no, "Under Review")
        )
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, reference_no, status FROM applied_schemes WHERE user_email = %s AND scheme_name = %s",
            (user_email, scheme_name)
        )
        existing = cursor.fetchone()
        if existing:
            ref_no = existing["reference_no"]
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "already_applied": True,
                "message": f"You have already applied for '{scheme_name}'.",
                "reference_no": ref_no,
                "status": existing["status"]
            })

        ref_no = generate_reference_no()
        cursor.execute(
            """
            INSERT INTO applied_schemes (user_id, user_email, user_name, scheme_name, scheme_category, reference_no, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, user_email, user_name, scheme_name, scheme_category, ref_no, "Under Review")
        )
        conn.commit()
        cursor.close()
        conn.close()

    return jsonify({
        "success": True,
        "already_applied": False,
        "message": f"Successfully applied for '{scheme_name}'!",
        "reference_no": ref_no,
        "scheme_name": scheme_name,
        "status": "Under Review"
    })


# ---- Dashboards ----

@app.route("/dashboard")
@login_required
def dashboard():
    """
    Citizen Personal Dashboard:
    Displays strictly the logged-in citizen's personal profile, their own submitted eligibility checks,
    ALL schemes applied by this user, and recommended schemes.
    """
    user_email = session.get("user_email")
    user_name = session.get("user_name", "Citizen")
    user_role = session.get("user_role", "citizen")
    user_id = session.get("user_id")

    db_type, conn = Database.get_connection()
    applications = []
    applied_schemes = []
    matched_schemes = []
    citizen_profile = {
        "id": user_id,
        "name": user_name,
        "email": user_email,
        "mobile": None,
        "age": None,
        "state": None,
        "income": None,
        "occupation": None,
        "schemeCategory": None
    }

    if db_type == "sqlite":
        cursor = conn.cursor()
        
        # 1. Fetch ONLY this citizen's eligibility checks
        cursor.execute(
            """
            SELECT ea_id, ea_name, ea_email, ea_mobile, ea_age, ea_state, ea_income, ea_scheme_category, ea_created_at
            FROM eligibility_applications
            WHERE ea_email = ?
            ORDER BY ea_created_at DESC
            """,
            (user_email,)
        )
        applications = [dict(r) for r in cursor.fetchall()]

        # 2. Fetch ALL schemes applied by this user
        cursor.execute(
            """
            SELECT id, scheme_name, scheme_category, reference_no, status, applied_at
            FROM applied_schemes
            WHERE user_email = ?
            ORDER BY applied_at DESC
            """,
            (user_email,)
        )
        applied_schemes = [dict(r) for r in cursor.fetchall()]

        # Populate profile details from latest eligibility submission
        if applications:
            latest = applications[0]
            citizen_profile.update({
                "name": latest.get("ea_name") or user_name,
                "mobile": latest.get("ea_mobile"),
                "age": latest.get("ea_age"),
                "state": latest.get("ea_state"),
                "income": latest.get("ea_income"),
                "schemeCategory": latest.get("ea_scheme_category")
            })

            # Fetch top recommended schemes for citizen's category
            cat = latest.get("ea_scheme_category")
            if cat:
                cursor.execute(
                    """
                    SELECT scheme_name, details, benefits, category AS scheme_category
                    FROM scheme_library
                    WHERE category LIKE ?
                    LIMIT 6
                    """,
                    (f"%{cat}%",)
                )
                matched_schemes = [dict(r) for r in cursor.fetchall()]

        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT ea_id, ea_name, ea_email, ea_mobile, ea_age, ea_state, ea_income, ea_scheme_category, ea_created_at
            FROM eligibility_applications
            WHERE ea_email = %s
            ORDER BY ea_created_at DESC
            """,
            (user_email,)
        )
        applications = cursor.fetchall()

        cursor.execute(
            """
            SELECT id, scheme_name, scheme_category, reference_no, status, applied_at
            FROM applied_schemes
            WHERE user_email = %s
            ORDER BY applied_at DESC
            """,
            (user_email,)
        )
        applied_schemes = cursor.fetchall()

        if applications:
            latest = applications[0]
            citizen_profile.update({
                "name": latest.get("ea_name") or user_name,
                "mobile": latest.get("ea_mobile"),
                "age": latest.get("ea_age"),
                "state": latest.get("ea_state"),
                "income": latest.get("ea_income"),
                "schemeCategory": latest.get("ea_scheme_category")
            })
            cat = latest.get("ea_scheme_category")
            if cat:
                cursor.execute(
                    """
                    SELECT scheme_name, details, benefits, scheme_category
                    FROM scheme_library
                    WHERE scheme_category LIKE %s
                    LIMIT 6
                    """,
                    (f"%{cat}%",)
                )
                matched_schemes = cursor.fetchall()
        cursor.close()
        conn.close()

    applied_scheme_names = {s["scheme_name"] for s in applied_schemes}

    current_user_data = {
        "id": user_id,
        "name": user_name,
        "email": user_email,
        "role": user_role
    }

    return render_template(
        "dashboard.html",
        citizen_profile=citizen_profile,
        applications=applications,
        applied_schemes=applied_schemes,
        applied_scheme_names=applied_scheme_names,
        matched_schemes=matched_schemes,
        current_user=current_user_data
    )


@app.route("/admin")
@admin_required
def admin_dashboard():
    """
    Dedicated Admin Portal Route:
    Displays portal-wide database of ALL citizen submissions and scheme applications.
    """
    db_type, conn = Database.get_connection()
    applications = []
    all_applied_schemes = []
    total_users = 0

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

        cursor.execute(
            """
            SELECT id, user_name, user_email, scheme_name, scheme_category, reference_no, status, applied_at
            FROM applied_schemes
            ORDER BY applied_at DESC
            """
        )
        all_applied_schemes = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

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

        cursor.execute(
            """
            SELECT id, user_name, user_email, scheme_name, scheme_category, reference_no, status, applied_at
            FROM applied_schemes
            ORDER BY applied_at DESC
            """
        )
        all_applied_schemes = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS cnt FROM users")
        row = cursor.fetchone()
        total_users = row["cnt"] if row else 0

        cursor.close()
        conn.close()

    admin_user = {
        "name": session.get("user_name", "System Administrator"),
        "email": session.get("user_email", "admin@janmitra.gov.in"),
        "role": "admin"
    }

    return render_template(
        "admin_dashboard.html",
        applications=applications,
        all_applied_schemes=all_applied_schemes,
        total_users=total_users,
        current_user=admin_user
    )


@app.route("/api/admin/update-status", methods=["POST"])
@admin_required
def admin_update_status():
    """
    Allows administrator to update the status of any citizen's scheme application.
    Supported statuses: 'Under Review', 'Approved', 'Rejected', 'Disbursed'
    """
    data = request.get_json(silent=True) or request.form
    app_id = data.get("application_id") or data.get("id")
    reference_no = data.get("reference_no")
    new_status = data.get("status", "").strip()

    valid_statuses = ["Under Review", "Approved", "Rejected", "Disbursed"]
    if new_status not in valid_statuses:
        return jsonify({
            "success": False,
            "message": f"Invalid status. Choose from: {', '.join(valid_statuses)}"
        }), 400

    if not app_id and not reference_no:
        return jsonify({
            "success": False,
            "message": "Application ID or Reference Number is required."
        }), 400

    db_type, conn = Database.get_connection()
    updated = False

    if db_type == "sqlite":
        cursor = conn.cursor()
        if app_id:
            cursor.execute(
                "UPDATE applied_schemes SET status = ? WHERE id = ?",
                (new_status, app_id)
            )
        else:
            cursor.execute(
                "UPDATE applied_schemes SET status = ? WHERE reference_no = ?",
                (new_status, reference_no)
            )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        if app_id:
            cursor.execute(
                "UPDATE applied_schemes SET status = %s WHERE id = %s",
                (new_status, app_id)
            )
        else:
            cursor.execute(
                "UPDATE applied_schemes SET status = %s WHERE reference_no = %s",
                (new_status, reference_no)
            )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        conn.close()

    if not updated:
        return jsonify({"success": False, "message": "Application record not found."}), 404

    return jsonify({
        "success": True,
        "message": f"Status successfully updated to '{new_status}'.",
        "status": new_status,
        "application_id": app_id,
        "reference_no": reference_no
    })


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
