"""Tiny Flask app stubs so url_for('auth.login') and url_for('admin.dashboard') work in tests."""

from flask import Blueprint, Flask


def create_test_app():
    app = Flask(__name__)
    app.secret_key = "secret_key"

    auth = Blueprint("auth", __name__)

    @auth.route("/login")
    def login():
        return "This is the login page"

    @auth.route("/dashboard")
    def dashboard():
        return "User dashboard"

    admin = Blueprint("admin", __name__)

    @admin.route("/")
    def dashboard():
        return "Admin dashboard"

    app.register_blueprint(auth)
    app.register_blueprint(admin, url_prefix="/admin")
    return app
