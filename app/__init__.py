import secrets
from datetime import date

from flask import Flask, render_template, session

import config
from app.database import Database
from app.routes.auth_routes import AuthRoutes


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db = Database()
    try:
        db.create_tables()
    finally:
        db.close()

    auth_routes = AuthRoutes()
    app.register_blueprint(auth_routes.bp)

    @app.before_request
    def ensure_csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)
        if session.get("user_id") and "currency" not in session:
            from app.models.user import UserModel

            user = UserModel.find_by_id(session["user_id"])
            session["currency"] = (user.get("currency") if user else None) or "NPR"

    @app.context_processor
    def inject_globals():
        from app.currency import CURRENCIES, display_amount, format_currency

        return {
            "today": date.today().isoformat(),
            "currencies": CURRENCIES,
            "format_currency": format_currency,
            "display_amount": display_amount,
            "app_name": "ExpenseX",
            "alert_count": 0,
        }

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app