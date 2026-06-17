"""Minimal routes so templates can resolve url_for until full modules exist."""

from flask import Blueprint, redirect, url_for


def register_placeholder_blueprints(app):
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

    app.register_blueprint(admin)
