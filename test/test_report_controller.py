import unittest

from flask import Blueprint

from app.auth import user_required
from test.stub_app import create_test_app


class TestReportController(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        reports = Blueprint("reports", __name__)

        @reports.route("/")
        @user_required
        def index():
            return "Reports Page"

        self.app.register_blueprint(reports, url_prefix="/reports")
        self.client = self.app.test_client()

    def test_reports_redirect_guest_to_login(self):
        """A guest visiting /reports/ should redirect to /login."""
        response = self.client.get("/reports/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_reports_opens_for_logged_in_user(self):
        """A logged-in user should see the reports page."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "user"
        response = self.client.get("/reports/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Reports Page")


if __name__ == "__main__":
    unittest.main()
