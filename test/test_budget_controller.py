import unittest

from flask import Blueprint

from app.auth import user_required
from test.stub_app import create_test_app


class TestBudgetController(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        budget = Blueprint("budget", __name__)

        @budget.route("/")
        @user_required
        def index():
            return "Budget Page"

        self.app.register_blueprint(budget, url_prefix="/budget")
        self.client = self.app.test_client()

    def test_budget_redirects_guest_to_login(self):
        """A guest visiting /budget/ should redirect to /login."""
        response = self.client.get("/budget/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_budget_opens_for_logged_in_user(self):
        """A logged-in user should see the budget page."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "user"
        response = self.client.get("/budget/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Budget Page")


if __name__ == "__main__":
    unittest.main()
