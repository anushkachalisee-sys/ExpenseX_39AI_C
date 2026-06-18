import unittest

from flask import Blueprint

from app.auth import admin_required
from test.stub_app import create_test_app


class TestAdminController(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        admin = Blueprint("admin_pages", __name__)

        @admin.route("/")
        @admin_required
        def dashboard():
            return "Admin Overview"

        @admin.route("/users")
        @admin_required
        def users():
            return "Admin Users"

        self.app.register_blueprint(admin, url_prefix="/admin-pages")
        self.client = self.app.test_client()

    def test_admin_dashboard_redirects_guest_to_login(self):
        """A guest visiting an admin page should redirect to /login."""
        response = self.client.get("/admin-pages/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_admin_dashboard_blocks_regular_user(self):
        """A regular user should not access admin pages."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "user"
        response = self.client.get("/admin-pages/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard", response.location)

    def test_admin_dashboard_opens_for_admin(self):
        """An admin should see the admin overview page."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 99
            sess["role"] = "admin"
        response = self.client.get("/admin-pages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Admin Overview")

    def test_admin_users_opens_for_admin(self):
        """An admin should see the user management page."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 99
            sess["role"] = "admin"
        response = self.client.get("/admin-pages/users")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Admin Users")


if __name__ == "__main__":
    unittest.main()
