import unittest

from flask import Blueprint

from app.auth import user_required
from test.stub_app import create_test_app


class TestTransactionController(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        transactions = Blueprint("transactions", __name__)

        @transactions.route("/income")
        @user_required
        def list_income():
            return "Income Page"

        @transactions.route("/expense")
        @user_required
        def list_expense():
            return "Expense Page"

        self.app.register_blueprint(transactions, url_prefix="/transactions")
        self.client = self.app.test_client()

    def test_income_redirects_guest_to_login(self):
        """A guest visiting /transactions/income should redirect to /login."""
        response = self.client.get("/transactions/income")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_income_opens_for_logged_in_user(self):
        """A logged-in user should see the income page."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "user"
        response = self.client.get("/transactions/income")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Income Page")

    def test_expense_redirects_admin_to_admin_home(self):
        """An admin should not use user transaction pages."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 99
            sess["role"] = "admin"
        response = self.client.get("/transactions/expense")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin", response.location)


if __name__ == "__main__":
    unittest.main()
