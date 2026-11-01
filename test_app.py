"""
Automated End-to-End Test Suite for JanMitra AI
Tests all routes, authentication, database operations, and matching engine.
"""
import unittest
import json
from app import app, Database

class JanMitraTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key-123"
        self.client = app.test_client()

    def test_01_home_page(self):
        """Verify home page loads successfully."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"JanMitra AI", res.data)

    def test_02_eligibility_page(self):
        """Verify eligibility checker page loads."""
        res = self.client.get("/check-eligibility")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Check your eligibility", res.data)

    def test_03_login_page_get(self):
        """Verify login page renders."""
        res = self.client.get("/login")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Citizen Login", res.data)

    def test_04_auth_status_unauthenticated(self):
        """Verify guest status."""
        res = self.client.get("/api/auth/status")
        data = res.get_json()
        self.assertFalse(data["logged_in"])
        self.assertIsNone(data["user"])

    def test_05_login_invalid_credentials(self):
        """Verify incorrect password is rejected."""
        res = self.client.post("/api/auth/login", json={
            "email": "demo@janmitra.gov.in",
            "password": "WrongPassword999"
        })
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data["success"])

    def test_06_login_valid_demo_credentials(self):
        """Verify demo credentials log in successfully."""
        res = self.client.post("/api/auth/login", json={
            "email": "demo@janmitra.gov.in",
            "password": "Password@123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["email"], "demo@janmitra.gov.in")

    def test_07_user_registration(self):
        """Verify new citizen registration works."""
        import time
        test_email = f"testcitizen_{int(time.time()*1000)}@example.com"
        res = self.client.post("/api/auth/register", json={
            "name": "Rajesh Kumar",
            "email": test_email,
            "password": "TestPassword@123",
            "confirm_password": "TestPassword@123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["name"], "Rajesh Kumar")

    def test_08_protected_dashboard_redirects_unauthenticated(self):
        """Verify dashboard requires login."""
        # Fresh client without session
        fresh_client = app.test_client()
        res = fresh_client.get("/dashboard")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/login", res.headers["Location"])

    def test_09_dashboard_accessible_when_authenticated(self):
        """Verify dashboard loads when authenticated."""
        with self.client:
            # Login first
            login_res = self.client.post("/api/auth/login", json={
                "email": "demo@janmitra.gov.in",
                "password": "Password@123"
            })
            self.assertEqual(login_res.status_code, 200)

            # Access dashboard
            dash_res = self.client.get("/dashboard")
            self.assertEqual(dash_res.status_code, 200)
            self.assertIn(b"Applications dashboard", dash_res.data)

    def test_10_api_check_eligibility(self):
        """Verify matching engine returns schemes."""
        res = self.client.post("/api/check-eligibility", json={
            "age": 22,
            "income": 150000,
            "state": "Rajasthan",
            "occupation": "Student",
            "schemeCategory": "Education & Learning"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("matches", data)
        self.assertGreaterEqual(len(data["matches"]), 1)

    def test_11_form_submit_and_result(self):
        """Verify /submit creates application and renders result page."""
        res = self.client.post("/submit", data={
            "name": "Unit Test Citizen",
            "email": "unittest@example.com",
            "mobile": "9999988888",
            "age": "24",
            "state": "Rajasthan",
            "income": "200000",
            "occupation": "Student",
            "schemeCategory": "Education & Learning"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"JanMitra AI", res.data)
        self.assertTrue(b"Education" in res.data)

    def test_12_ai_chat_assistant(self):
        """Verify AI chat endpoint returns intelligent recommendations."""
        res = self.client.post("/api/ai-chat", json={
            "message": "Are there scholarships for students?"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("reply", data)

    def test_13_logout(self):
        """Verify logout clears session."""
        with self.client:
            self.client.post("/api/auth/login", json={
                "email": "demo@janmitra.gov.in",
                "password": "Password@123"
            })
            logout_res = self.client.get("/logout")
            self.assertEqual(logout_res.status_code, 302)
            
            # Verify status is now unauthenticated
            status_res = self.client.get("/api/auth/status")
            self.assertFalse(status_res.get_json()["logged_in"])

if __name__ == "__main__":
    unittest.main()
