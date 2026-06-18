import unittest

from flask import Blueprint

from app.auth import user_required
from test.stub_app import create_test_app


class TestCategoryController(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        categories = Blueprint("categories", __name__)

        @categories.route("/")
        @user_required
        def list_all():
            return "Categories Page"

        self.app.register_blueprint(categories, url_prefix="/categories")
        self.client = self.app.test_client()

    def test_categories_redirect_guest_to_login(self):
        """A guest visiting /categories/ should redirect to /login."""
        response = self.client.get("/categories/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_categories_opens_for_logged_in_user(self):
        """A logged-in user should see the categories page."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "user"
        response = self.client.get("/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Categories Page")


if __name__ == "__main__":
    unittest.main()
