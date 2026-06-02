"""Minimal routes so templates can resolve url_for until full modules exist."""

from flask import Blueprint, redirect, url_for


def register_placeholder_blueprints(app):
    categories = Blueprint("categories", __name__, url_prefix="/categories")

    @categories.route("/")
    def list_all():
        return redirect(url_for("auth.dashboard"))

    budget = Blueprint("budget", __name__, url_prefix="/budget")

    @budget.route("/")
    def index():
        return redirect(url_for("auth.dashboard"))

    reports = Blueprint("reports", __name__, url_prefix="/reports")

    @reports.route("/")
    def index():
        return redirect(url_for("auth.dashboard"))

    admin = Blueprint("admin", __name__, url_prefix="/admin")

    @admin.route("/")
    def dashboard():
        return (
            "<!DOCTYPE html><html><body style='font-family:sans-serif;padding:2rem'>"
            "<h1>Admin dashboard</h1><p>Coming soon.</p>"
            "<p><a href='/logout'>Log out</a></p></body></html>"
        )

    @admin.route("/users")
    def users():
        return redirect(url_for("auth.dashboard"))

    @admin.route("/audit")
    def audit_log():
        return redirect(url_for("auth.dashboard"))

    @admin.route("/categories")
    def global_categories():
        return redirect(url_for("auth.dashboard"))

    for bp in (categories, budget, reports, admin):
        app.register_blueprint(bp)
