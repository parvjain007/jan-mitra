"""
Automated Test Suite for JanMitra AI
Tests authentication, eligibility registration, citizen dashboard isolation,
and admin route protection.
"""
import unittest
import json
import time
from app import app, Database

class JanMitraUpdatedTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key-updates-123"
        self.client = app.test_client()

    def test_01_home_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"JanMitra AI", res.data)

    def test_02_eligibility_page_has_password_field(self):
        res = self.client.get("/check-eligibility")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Create Account Password", res.data)

    def test_03_login_page_has_only_login(self):
        res = self.client.get("/login")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Citizen Login", res.data)
        # Verify registration form was removed
        self.assertNotIn(b'id="registerForm"', res.data)

    def test_04_login_citizen_redirects_to_dashboard(self):
        res = self.client.post("/api/auth/login", json={
            "email": "demo@janmitra.gov.in",
            "password": "Password@123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["redirect"], "/dashboard")

    def test_05_login_admin_redirects_to_admin(self):
        res = self.client.post("/api/auth/login", json={
            "email": "admin@janmitra.gov.in",
            "password": "Admin@123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["redirect"], "/admin")

    def test_06_eligibility_form_registers_citizen(self):
        """Verify check eligibility form registers user and logs them in."""
        unique_email = f"citizen_{int(time.time()*1000)}@example.com"
        res = self.client.post("/submit", data={
            "name": "Sunil Verma",
            "email": unique_email,
            "mobile": "9876123450",
            "age": "28",
            "state": "Rajasthan",
            "income": "250000",
            "occupation": "Farmer",
            "schemeCategory": "Agriculture",
            "password": "CitizenSecret@123"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"JanMitra AI", res.data)

        # Verify citizen is logged in
        status_res = self.client.get("/api/auth/status")
        status_data = status_res.get_json()
        self.assertTrue(status_data["logged_in"])
        self.assertEqual(status_data["user"]["email"], unique_email)

    def test_07_citizen_dashboard_shows_only_own_data(self):
        """Verify citizen dashboard displays strictly logged-in citizen's details."""
        unique_email = f"isolated_{int(time.time()*1000)}@example.com"
        with self.client:
            # Submit application
            self.client.post("/submit", data={
                "name": "Deepak Mehta",
                "email": unique_email,
                "mobile": "9123456780",
                "age": "32",
                "state": "Gujarat",
                "income": "180000",
                "occupation": "Business Owner",
                "schemeCategory": "Business & Entrepreneurship",
                "password": "Password@123"
            })

            # View dashboard
            dash_res = self.client.get("/dashboard")
            self.assertEqual(dash_res.status_code, 200)
            self.assertIn(b"Deepak Mehta", dash_res.data)
            self.assertIn(unique_email.encode(), dash_res.data)
            self.assertIn(b"Your Citizen Profile Details", dash_res.data)
            
            # Ensure it does NOT show other citizens' emails in their personal applications list
            # (e.g. aditi@example.com is in DB from earlier sample, but must not appear in Deepak's table)
            self.assertNotIn(b"aditi@example.com", dash_res.data)

    def test_08_admin_route_restricted(self):
        """Verify citizen cannot access /admin and is redirected to /dashboard."""
        fresh_client = app.test_client()
        with fresh_client:
            # Login as regular citizen
            fresh_client.post("/api/auth/login", json={
                "email": "demo@janmitra.gov.in",
                "password": "Password@123"
            })
            # Try accessing /admin
            admin_res = fresh_client.get("/admin")
            self.assertEqual(admin_res.status_code, 302)
            self.assertIn("/dashboard", admin_res.headers["Location"])

    def test_09_admin_route_accessible_by_admin(self):
        """Verify admin can access /admin and sees portal-wide submissions."""
        fresh_client = app.test_client()
        with fresh_client:
            # Login as admin
            fresh_client.post("/api/auth/login", json={
                "email": "admin@janmitra.gov.in",
                "password": "Admin@123"
            })
            # Access /admin
            admin_res = fresh_client.get("/admin")
            self.assertEqual(admin_res.status_code, 200)
            self.assertIn(b"Portal-Wide Submissions Database", admin_res.data)

    def test_10_logout(self):
        with self.client:
            self.client.post("/api/auth/login", json={
                "email": "demo@janmitra.gov.in",
                "password": "Password@123"
            })
            logout_res = self.client.get("/logout")
            self.assertEqual(logout_res.status_code, 302)
            status_res = self.client.get("/api/auth/status")
            self.assertFalse(status_res.get_json()["logged_in"])

    def test_11_apply_scheme_unauthorized_for_guest(self):
        """Unauthenticated guests cannot apply for schemes."""
        client = app.test_client()
        res = client.post("/api/apply-scheme", json={
            "scheme_name": "PM Kisan Samman Nidhi",
            "scheme_category": "Agriculture"
        })
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertTrue(data.get("require_login"))

    def test_12_apply_multiple_schemes_and_view_in_dashboard(self):
        """Citizen can apply for multiple schemes and see all of them in their dashboard."""
        client = app.test_client()
        citizen_email = f"multiapp_{int(time.time()*1000)}@example.com"

        with client:
            # 1. Register citizen via eligibility check
            reg_res = client.post("/submit", data={
                "name": "Ravi Kumar",
                "email": citizen_email,
                "mobile": "9811223344",
                "age": "35",
                "state": "Rajasthan",
                "income": "220000",
                "occupation": "Farmer",
                "schemeCategory": "Agriculture",
                "password": "Password@123"
            })
            self.assertEqual(reg_res.status_code, 200)

            # 2. Apply for Scheme #1
            res1 = client.post("/api/apply-scheme", json={
                "scheme_name": "PM Kisan Samman Nidhi",
                "scheme_category": "Agriculture"
            })
            self.assertEqual(res1.status_code, 200)
            data1 = res1.get_json()
            self.assertTrue(data1["success"])
            self.assertFalse(data1["already_applied"])
            ref1 = data1["reference_no"]
            self.assertTrue(ref1.startswith("JM-2026-"))

            # 3. Apply for Scheme #2 (Multiple schemes support)
            res2 = client.post("/api/apply-scheme", json={
                "scheme_name": "PM Fasal Bima Yojana",
                "scheme_category": "Agriculture"
            })
            self.assertEqual(res2.status_code, 200)
            data2 = res2.get_json()
            self.assertTrue(data2["success"])
            self.assertFalse(data2["already_applied"])
            ref2 = data2["reference_no"]
            self.assertTrue(ref2.startswith("JM-2026-"))
            self.assertNotEqual(ref1, ref2)

            # 4. Duplicate prevention for same scheme
            res_dup = client.post("/api/apply-scheme", json={
                "scheme_name": "PM Kisan Samman Nidhi",
                "scheme_category": "Agriculture"
            })
            self.assertEqual(res_dup.status_code, 200)
            data_dup = res_dup.get_json()
            self.assertTrue(data_dup["already_applied"])
            self.assertEqual(data_dup["reference_no"], ref1)

            # 5. Verify citizen dashboard displays all applied schemes
            dash_res = client.get("/dashboard")
            self.assertEqual(dash_res.status_code, 200)
            self.assertIn(b"My Applied Government Schemes", dash_res.data)
            self.assertIn(b"PM Kisan Samman Nidhi", dash_res.data)
            self.assertIn(b"PM Fasal Bima Yojana", dash_res.data)
            self.assertIn(ref1.encode(), dash_res.data)
            self.assertIn(ref2.encode(), dash_res.data)
            self.assertIn(b"2 Applied", dash_res.data)

    def test_13_citizen_applied_schemes_isolated(self):
        """Citizen B should not see schemes applied by Citizen A in their dashboard."""
        client_a = app.test_client()
        client_b = app.test_client()
        email_a = f"citizen_a_{int(time.time()*1000)}@example.com"
        email_b = f"citizen_b_{int(time.time()*1000)}@example.com"

        unique_scheme = f"Special Grant Scheme {int(time.time())}"

        # Citizen A registers and applies
        with client_a:
            client_a.post("/submit", data={
                "name": "Citizen A",
                "email": email_a,
                "mobile": "9900000001",
                "age": "25",
                "state": "Delhi",
                "income": "300000",
                "schemeCategory": "Education",
                "password": "Password@123"
            })
            client_a.post("/api/apply-scheme", json={
                "scheme_name": unique_scheme,
                "scheme_category": "Education"
            })

        # Citizen B registers and views dashboard
        with client_b:
            client_b.post("/submit", data={
                "name": "Citizen B",
                "email": email_b,
                "mobile": "9900000002",
                "age": "40",
                "state": "Maharashtra",
                "income": "400000",
                "schemeCategory": "Health",
                "password": "Password@123"
            })
            dash_b = client_b.get("/dashboard")
            self.assertEqual(dash_b.status_code, 200)
            # Citizen B should NOT see Citizen A's unique applied scheme
            self.assertNotIn(unique_scheme.encode(), dash_b.data)

    def test_14_admin_dashboard_shows_all_applied_schemes(self):
        """Admin dashboard displays all applied schemes across all citizens."""
        client = app.test_client()
        with client:
            client.post("/api/auth/login", json={
                "email": "admin@janmitra.gov.in",
                "password": "Admin@123"
            })
            admin_res = client.get("/admin")
            self.assertEqual(admin_res.status_code, 200)
            self.assertIn(b"All Citizen Applied Schemes", admin_res.data)
            self.assertIn(b"Schemes Applied", admin_res.data)
            self.assertIn(b"Update Status", admin_res.data)

    def test_15_dashboard_navbar_does_not_have_check_eligibility(self):
        """Verify Check Eligibility is removed from citizen navbar after login."""
        client = app.test_client()
        with client:
            client.post("/api/auth/login", json={
                "email": "demo@janmitra.gov.in",
                "password": "Password@123"
            })
            dash_res = client.get("/dashboard")
            self.assertEqual(dash_res.status_code, 200)
            # The .dash-nav navbar header must NOT contain Check Eligibility
            nav_html = dash_res.data.split(b'class="dash-nav"')[1].split(b'</header>')[0]
            self.assertNotIn(b"Check Eligibility", nav_html)

    def test_16_admin_update_status_permissions(self):
        """Verify access controls on admin update status endpoint."""
        client = app.test_client()
        # 1. Unauthenticated guest
        res_guest = client.post("/api/admin/update-status", json={
            "application_id": 1,
            "status": "Approved"
        })
        self.assertEqual(res_guest.status_code, 401)

        # 2. Regular citizen
        with client:
            client.post("/api/auth/login", json={
                "email": "demo@janmitra.gov.in",
                "password": "Password@123"
            })
            res_citizen = client.post("/api/admin/update-status", json={
                "application_id": 1,
                "status": "Approved"
            })
            self.assertEqual(res_citizen.status_code, 403)

    def test_17_admin_update_status_reflected_in_citizen_dashboard(self):
        """Admin can update an application status and citizen sees the updated status."""
        cit_client = app.test_client()
        adm_client = app.test_client()
        cit_email = f"status_cit_{int(time.time()*1000)}@example.com"

        # 1. Citizen registers and applies for a scheme
        with cit_client:
            cit_client.post("/submit", data={
                "name": "Kavita Rao",
                "email": cit_email,
                "mobile": "9811223399",
                "age": "29",
                "state": "Karnataka",
                "income": "240000",
                "schemeCategory": "Women & Child",
                "password": "Password@123"
            })
            app_res = cit_client.post("/api/apply-scheme", json={
                "scheme_name": "Pradhan Mantri Matru Vandana Yojana",
                "scheme_category": "Women & Child"
            })
            self.assertEqual(app_res.status_code, 200)
            ref_no = app_res.get_json()["reference_no"]

            # Initially shows Under Review
            d1 = cit_client.get("/dashboard")
            self.assertIn(b"Under Review", d1.data)

        # 2. Admin logs in and updates status to 'Approved'
        with adm_client:
            adm_client.post("/api/auth/login", json={
                "email": "admin@janmitra.gov.in",
                "password": "Admin@123"
            })
            update_res = adm_client.post("/api/admin/update-status", json={
                "reference_no": ref_no,
                "status": "Approved"
            })
            self.assertEqual(update_res.status_code, 200)
            u_data = update_res.get_json()
            self.assertTrue(u_data["success"])
            self.assertEqual(u_data["status"], "Approved")

        # 3. Citizen checks dashboard: status is now 'Approved'
        with cit_client:
            d2 = cit_client.get("/dashboard")
            self.assertEqual(d2.status_code, 200)
            self.assertIn(b"Approved", d2.data)

        # 4. Admin updates status to 'Disbursed'
        with adm_client:
            update_res2 = adm_client.post("/api/admin/update-status", json={
                "reference_no": ref_no,
                "status": "Disbursed"
            })
            self.assertEqual(update_res2.status_code, 200)
            self.assertEqual(update_res2.get_json()["status"], "Disbursed")

        # 5. Citizen dashboard now reflects 'Disbursed'
        with cit_client:
            d3 = cit_client.get("/dashboard")
            self.assertEqual(d3.status_code, 200)
            self.assertIn(b"Disbursed", d3.data)

if __name__ == "__main__":
    unittest.main()
