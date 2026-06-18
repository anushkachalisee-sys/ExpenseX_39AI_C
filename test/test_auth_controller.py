import unittest

from flask import Blueprint

from app.auth import user_required
from test.stub_app import create_test_app


class TestAuthController(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        auth = Blueprint("auth_pages", __name__)

        @auth.route("/dashboard")
        @user_required
        def dashboard():
            return "Welcome to Dashboard"

        self.app.register_blueprint(auth, url_prefix="/auth-pages")
        self.client = self.app.test_client()

    def test_dashboard_redirects_guest_to_login(self):
        """A guest visiting a protected page should redirect to /login."""
        response = self.client.get("/auth-pages/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_dashboard_opens_for_logged_in_user(self):
        """A logged-in user should see the dashboard page."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "user"
        response = self.client.get("/auth-pages/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Welcome to Dashboard")

    def test_dashboard_redirects_admin_to_admin_home(self):
        """An admin should be sent to the admin area, not the user dashboard."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 99
            sess["role"] = "admin"
        response = self.client.get("/auth-pages/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin", response.location)


if __name__ == "__main__":
    unittest.main()
