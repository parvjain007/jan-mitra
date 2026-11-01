# JanMitra AI — AI Citizen Welfare Portal

JanMitra AI is an AI-powered citizen welfare platform designed to help citizens across India discover and match government welfare schemes they are eligible for.

---

## 🚀 Key Features

1. **Citizen Authentication System (Full Working Login & Signup)**:
   - **Web Interface**: Modern, responsive login and registration page (`/login`) with dark/light mode toggle.
   - **Validation**: Email validation, interactive password strength meter, password confirmation matching, and password visibility toggles.
   - **Quick Demo Access**: Instant one-click credentials auto-fill (`demo@janmitra.gov.in` / `Password@123`).
   - **Backend Security**: Cryptographically secure PBKDF2/SHA-256 password hashing and session management.
   - **Protected Dashboard**: Citizen applications dashboard (`/dashboard`) protected with authentication.
   - **Java Implementation**: Includes both a Java Swing Desktop GUI (`JanMitraLoginApp.java`) and a standalone Java HTTP Server (`JanMitraAuthServer.java`) in the `java/` directory.

2. **AI Eligibility Checker**:
   - Compares user age, income, state, occupation, and scheme category against verified government criteria.
   - Free-form interactive AI Chat assistant on the home page.

3. **Resilient Dual-Database Architecture**:
   - Seamlessly uses MySQL if running (`DB_CONFIG` in `app.py`).
   - Automatically falls back to SQLite (`schemes.db`) with 3,400+ government schemes in `scheme_library` if MySQL is unavailable, ensuring zero downtime.

---

## 📁 Project Structure

```
jan-mitra-ai/
├── app.py                     # Main Flask application with auth, matching engine & API
├── index.html                 # Modern home page with interactive AI assistant & navbar
├── eligibility.html           # Citizen eligibility questionnaire
├── login.html                 # Citizen Login & Registration interface
├── schemes.db                 # SQLite database (schemes, scheme_library, users, applications)
├── create_db.py               # Database diagnostics utility
├── init_db.py                 # Database initialization & seeding script
├── test_app.py                # 13 automated unit & integration tests
│
├── templates/
│   ├── login.html             # Templated login & registration page
│   ├── dashboard.html         # Authenticated applications dashboard
│   └── result.html            # Matched schemes display page
│
├── java/
│   ├── JanMitraLoginApp.java  # Java Swing Desktop GUI login & registration app
│   └── JanMitraAuthServer.java# Standalone Java HTTP server for login authentication
│
├── run_python_app.bat         # Single-click runner for Flask web server
├── run_java_app.bat           # Single-click runner for Java GUI Login application
└── run_java_server.bat        # Single-click runner for Java HTTP Authentication server
```

---

## 🏃 Quick Start Guide

### 1. Run the Python Web Application
Double-click `run_python_app.bat` or run:
```bash
python app.py
```
Open your browser and navigate to:
- **Home**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Citizen Login**: [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)
- **Eligibility Checker**: [http://127.0.0.1:5000/check-eligibility](http://127.0.0.1:5000/check-eligibility)
- **Dashboard**: [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)

#### Demo Login Credentials:
- **Email**: `demo@janmitra.gov.in`
- **Password**: `Password@123`

---

### 2. Run the Java Login Application
If you want to run the **Java Desktop GUI application**:
Double-click `run_java_app.bat` or execute:
```bash
javac -d . java/JanMitraLoginApp.java
java -cp . java_auth.JanMitraLoginApp
```

If you want to run the **standalone Java HTTP authentication server** (port 8080):
Double-click `run_java_server.bat` or execute:
```bash
javac -d . java/JanMitraAuthServer.java
java -cp . java_auth.JanMitraAuthServer
```

---

### 3. Run Automated Tests
To verify all 13 test cases (authentication, matching engine, database, and routes):
```bash
python -m unittest test_app.py
```
