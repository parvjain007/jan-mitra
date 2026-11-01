# JanMitra AI — AI Citizen Welfare Portal

JanMitra AI is an AI-powered citizen welfare platform designed to help citizens across India discover and match government welfare schemes they qualify for.

---

## 🚀 Key Updates & Architecture

1. **Streamlined Registration via Check Eligibility**:
   - The standalone registration tab on the login page has been **removed**.
   - Citizens register directly by completing the **[Check Eligibility Form](/check-eligibility)**.
   - Citizens provide their details (Name, Email, Mobile, Age, State, Income, Occupation, Scheme Category) and create a password.
   - Submitting the form automatically creates their citizen account, saves their scheme application, and logs them in immediately.

2. **Isolated Citizen Dashboard (`/dashboard`)**:
   - After citizen login, the dashboard displays **strictly the logged-in citizen's personal profile**:
     - Full Name, Email, Mobile, Age, State, Income, and Occupation.
     - **Cleaned User Navbar**: "Check Eligibility" is automatically removed from the user navbar once logged in.
     - **My Applied Government Schemes**: Real-time tracker of all welfare schemes applied by this citizen, showing unique reference numbers (`JM-2026-XXXXX`), categories, status ("Under Review", "Approved", "Rejected", "Disbursed"), and date submitted, with printable confirmation slips.
     - **Apply for Multiple Schemes**: Citizens can apply for multiple schemes with a single click from their dashboard or the eligibility results page.
     - Recommended government schemes matched specifically to their profile.
     - Other citizens' data is completely hidden.

3. **Multi-Scheme Application API (`POST /api/apply-scheme`)**:
   - Allows authenticated citizens to apply for any number of eligible welfare schemes.
   - Generates official application reference numbers (`JM-2026-XXXXX`).
   - Prevents accidental duplicate submissions while maintaining instant real-time feedback.

4. **Dedicated Admin Portal (`/admin`) & Status Update Workflow**:
   - The master table showing all portal-wide citizen applications across India has been relocated to **`/admin`**.
   - Added **All Citizen Applied Schemes** table for portal-wide tracking of all scheme applications.
   - **Update Status Button**: Administrators can click the "Update Status" button next to any scheme application to change its status (`Under Review`, `Approved`, `Rejected`, `Disbursed`).
   - The status updates dynamically in real-time in both the admin portal and the citizen's personal dashboard via `POST /api/admin/update-status`.
   - Protected route: Only accessible by users with `admin` privileges.
   - If an admin logs in at `/login`, they are automatically routed to `/admin`.
   - Regular citizens attempting to access `/admin` are safely redirected to their personal `/dashboard`.

---

## 🔑 Login & Demo Credentials

| Role | Email | Password | Destination after Login |
|---|---|---|---|
| **Citizen (Your Account)** | `parvjain248@gmail.com` | `Password@123` | **`/dashboard`** (Personal Profile) |
| **Citizen (Demo)** | `demo@janmitra.gov.in` | `Password@123` | **`/dashboard`** (Personal Profile) |
| **System Administrator** | `admin@janmitra.gov.in` | `Admin@123` | **`/admin`** (Master Database View) |

---

## 📁 Key Routes

- **Home Page**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Check Eligibility & Register**: [http://127.0.0.1:5000/check-eligibility](http://127.0.0.1:5000/check-eligibility)
- **Citizen Login**: [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)
- **My Personal Dashboard**: [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)
- **Admin Control Center**: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)

---

## 🏃 Quick Start

### 1. Run Web Application
Double click `run_python_app.bat` or run:
```bash
python app.py
```

### 2. Run Java GUI Login Application
Double click `run_java_app.bat` or run:
```bash
java -cp . java_auth.JanMitraLoginApp
```

### 3. Run Automated Tests
```bash
python -m unittest test_app.py
```
