import secrets
from datetime import date

from flask import Flask, render_template, session

import config
from app.database import Database
from app.models.budget import BudgetModel
from app.models.transaction import TransactionModel
from app.routes.admin_routes import AdminRoutes
from app.routes.auth_routes import AuthRoutes
from app.routes.budget_routes import BudgetRoutes
from app.routes.category_routes import CategoryRoutes
from app.routes.report_routes import ReportRoutes
from app.routes.transaction_routes import TransactionRoutes


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db = Database()
    try:
        db.create_tables()
    finally:
        db.close()

    auth_routes = AuthRoutes()
    transaction_routes = TransactionRoutes()
    category_routes = CategoryRoutes()
    budget_routes = BudgetRoutes()
    report_routes = ReportRoutes()
    admin_routes = AdminRoutes()

    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(transaction_routes.bp, url_prefix="/transactions")
    app.register_blueprint(category_routes.bp, url_prefix="/categories")
    app.register_blueprint(budget_routes.bp, url_prefix="/budget")
    app.register_blueprint(report_routes.bp, url_prefix="/reports")
    app.register_blueprint(admin_routes.bp, url_prefix="/admin")

    @app.before_request
    def ensure_csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)
        if session.get("user_id") and "currency" not in session:
            from app.models.user import UserModel

            user = UserModel.find_by_id(session["user_id"])
            session["currency"] = (user.get("currency") if user else None) or "NPR"

    def user_initials(name):
        if not name:
            return "U"
        parts = str(name).strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return parts[0][0].upper() if parts[0] else "U"

    @app.context_processor
    def inject_globals():
        from app.currency import CURRENCIES, display_amount, format_currency

        ctx = {
            "today": date.today().isoformat(),
            "currencies": CURRENCIES,
            "format_currency": format_currency,
            "display_amount": display_amount,
            "user_initials": user_initials,
            "app_name": "ExpenseX",
            "alert_count": 0,
        }
        user_id = session.get("user_id")
        if user_id:
            budget = BudgetModel.get_budget(user_id)
            summary = TransactionModel.get_monthly_summary(user_id)
            today_expense = TransactionModel.get_today_expense(user_id)
            monthly_limit = float(budget["monthly_limit"]) if budget else 0.0
            daily_limit = float(budget["daily_limit"]) if budget else 0.0
            count = 0
            if monthly_limit > 0 and summary["expense"] >= monthly_limit:
                count += 1
            if daily_limit > 0 and today_expense >= daily_limit:
                count += 1
            ctx["alert_count"] = count
        return ctx

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app
