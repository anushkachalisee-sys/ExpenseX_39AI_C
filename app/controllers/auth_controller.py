#checking
#working in this file
from datetime import date, timedelta

from flask import flash, redirect, render_template, request, session, url_for

from app.auth import generate_csrf_token, validate_csrf, verify_password
from app.currency import CURRENCIES
from app.database import log_activity
from app.models.budget import BudgetModel
from app.models.category import CategoryModel
from app.models.transaction import TransactionModel
from app.models.user import UserModel
#auth side done and complete

def health_score(total_income, total_expense):
    if total_income == 0:
        return 0
    ratio = total_expense / total_income
    if ratio <= 0:
        return 100
    if ratio >= 1.5:
        return 0
    score = int((1 - ratio / 1.5) * 100)
    return max(0, min(100, score))


def health_label(score):
    if score >= 70:
        return "Excellent"
    if score >= 40:
        return "Fair"
    return "Needs Attention"


def trend_change(current, previous):
    if previous == 0:
        if current > 0:
            return 100.0, "up"
        return 0.0, "flat"
    pct = ((current - previous) / previous) * 100
    if pct > 0.5:
        return round(pct, 1), "up"
    if pct < -0.5:
        return round(abs(pct), 1), "down"
    return 0.0, "flat"


def build_sparkline_series(user_id):
    rows = TransactionModel.get_six_month_comparison(user_id)
    income_map = {}
    expense_map = {}
    balance_map = {}
    for r in rows:
        m = r["month"]
        inc = float(r["income"])
        exp = float(r["expense"])
        income_map[m] = inc
        expense_map[m] = exp
        balance_map[m] = inc - exp

    labels = []
    today = date.today()
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        labels.append(f"{y:04d}-{m:02d}")

    return {
        "income": [income_map.get(l, 0.0) for l in labels],
        "expense": [expense_map.get(l, 0.0) for l in labels],
        "balance": [balance_map.get(l, 0.0) for l in labels],
        "streak": [float(session.get("streak", 0))] * 6,
    }


class AuthController:
    def _redirect_after_auth(self):
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("auth.dashboard"))

    def _profile_template(self):
        return (
            "admin/profile.html"
            if session.get("role") == "admin"
            else "auth/profile.html"
        )

    def home(self):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("auth.dashboard"))

    def login(self):
        if session.get("user_id"):
            return self._redirect_after_auth()

        if request.method == "POST":
            if not validate_csrf():
                flash("Invalid security token. Please try again.", "danger")
                return render_template("auth/login.html")

            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = UserModel.find_by_email(email)
            if not user or not verify_password(password, user["password"]):
                flash("Invalid email or password.", "danger")
                return render_template("auth/login.html")

            if not UserModel.is_active_user(user):
                flash("Account is deactivated.", "danger")
                return render_template("auth/login.html")

            streak = UserModel.update_login_streak(user["id"])
            generate_csrf_token()

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]
            session["streak"] = streak
            session["currency"] = user.get("currency") or "NPR"

            log_activity(user["id"], user["name"], "User logged in", email)

            totals = UserModel.get_totals(user["id"])
            unlocked = BudgetModel.check_and_unlock_achievements(
                user["id"], totals, streak
            )
            if unlocked:
                flash(f"Achievement unlocked: {', '.join(unlocked)}!", "success")

            flash(f"Welcome back, {user['name']}!", "success")
            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("auth.dashboard"))

        return render_template("auth/login.html")

    def register(self):
        if session.get("user_id"):
            return self._redirect_after_auth()

        if request.method == "POST":
            if not validate_csrf():
                flash("Invalid security token. Please try again.", "danger")
                return render_template("auth/register.html")

            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm_password", "")

            if not name or not email or not password:
                flash("All fields are required.", "danger")
                return render_template("auth/register.html")

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("auth/register.html")

            if password != confirm:
                flash("Passwords do not match.", "danger")
                return render_template("auth/register.html")

            if UserModel.find_by_email(email):
                flash("Email is already registered.", "danger")
                return render_template("auth/register.html")

            user_id = UserModel.create(name, email, password)
            CategoryModel.copy_global_to_user(user_id)
            log_activity(user_id, name, "User registered", email)

            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))

        return render_template("auth/register.html")

    def logout(self):
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("auth.login"))

    def dashboard(self):
        user_id = session["user_id"]
        currency = session.get("currency", "NPR")
        month = date.today().strftime("%Y-%m")
        summary = TransactionModel.get_monthly_summary(user_id, month)
        prev_summary = TransactionModel.get_prev_month_summary(user_id)
        totals = UserModel.get_totals(user_id)
        today_expense = TransactionModel.get_today_expense(user_id)
        recent = TransactionModel.get_recent(user_id, 5)
        budget = BudgetModel.get_budget(user_id)
        achievements = BudgetModel.get_achievements(user_id)

        monthly_limit = float(budget["monthly_limit"]) if budget else 0.0
        daily_limit = float(budget["daily_limit"]) if budget else 0.0
        monthly_expense = summary["expense"]
        balance = summary["income"] - summary["expense"]
        total_balance = totals["income"] - totals["expense"]

        alerts = []
        if monthly_limit > 0 and monthly_expense >= monthly_limit:
            alerts.append(
                {
                    "type": "danger",
                    "message": "You have reached or exceeded your monthly spending limit.",
                }
            )
        if daily_limit > 0 and today_expense >= daily_limit:
            alerts.append(
                {
                    "type": "warning",
                    "message": "You have reached or exceeded your daily spending limit.",
                }
            )

        streak = session.get("streak", 0)
        BudgetModel.check_and_unlock_achievements(user_id, totals, streak)

        month_income = summary["income"]
        month_expense = summary["expense"]
        remaining_balance = month_income - month_expense
        scale = max(month_income, month_expense, monthly_limit, 1.0)
        budget_pct = (
            min(100.0, (month_expense / monthly_limit) * 100)
            if monthly_limit > 0
            else 0.0
        )

        month_analytics = {
            "income": {
                "amount": month_income,
                "pct": min(100.0, (month_income / scale) * 100),
            },
            "expense": {
                "amount": month_expense,
                "pct": min(100.0, (month_expense / scale) * 100),
            },
            "budget": {
                "amount": month_expense,
                "limit": monthly_limit,
                "pct": budget_pct,
            },
            "remaining": {
                "amount": remaining_balance,
                "pct": min(100.0, max(0.0, remaining_balance) / scale * 100),
            },
        }

        score = health_score(totals["income"], totals["expense"])
        sparklines = build_sparkline_series(user_id)

        inc_trend_pct, inc_trend_dir = trend_change(
            summary["income"], prev_summary["income"]
        )
        exp_trend_pct, exp_trend_dir = trend_change(
            summary["expense"], prev_summary["expense"]
        )
        bal_current = summary["income"] - summary["expense"]
        bal_prev = prev_summary["income"] - prev_summary["expense"]
        bal_trend_pct, bal_trend_dir = trend_change(bal_current, bal_prev)

        return render_template(
            "auth/dashboard.html",
            summary=summary,
            totals=totals,
            balance=balance,
            total_balance=total_balance,
            today_expense=today_expense,
            recent=recent,
            budget=budget,
            achievements=achievements,
            alerts=alerts,
            month=month,
            monthly_limit=monthly_limit,
            daily_limit=daily_limit,
            month_analytics=month_analytics,
            health_score=score,
            score_label=health_label(score),
            sparklines=sparklines,
            currency=currency,
            inc_trend_pct=inc_trend_pct,
            inc_trend_dir=inc_trend_dir,
            exp_trend_pct=exp_trend_pct,
            exp_trend_dir=exp_trend_dir,
            bal_trend_pct=bal_trend_pct,
            bal_trend_dir=bal_trend_dir,
            streak=streak,
        )

    def profile(self):
        user_id = session["user_id"]
        user = UserModel.find_by_id(user_id)
        template = self._profile_template()
        is_admin = session.get("role") == "admin"

        if request.method == "POST":
            if not validate_csrf():
                flash("Invalid security token. Please try again.", "danger")
                return render_template(template, user=user, is_admin=is_admin)

            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm_password", "")
            currency = user.get("currency") or "NPR"
            if not is_admin:
                currency = request.form.get("currency", currency)
                if currency not in CURRENCIES:
                    currency = "NPR"

            if not name or not email:
                flash("Name and email are required.", "danger")
                return render_template(template, user=user, is_admin=is_admin)

            if UserModel.email_exists_for_other(email, user_id):
                flash("Email is already in use by another account.", "danger")
                return render_template(template, user=user, is_admin=is_admin)

            if password:
                if len(password) < 6:
                    flash("Password must be at least 6 characters.", "danger")
                    return render_template(template, user=user, is_admin=is_admin)
                if password != confirm:
                    flash("Passwords do not match.", "danger")
                    return render_template(template, user=user, is_admin=is_admin)
                if is_admin:
                    UserModel.update_profile(user_id, name, email, password)
                else:
                    UserModel.update_profile(
                        user_id, name, email, password, currency
                    )
            else:
                if is_admin:
                    UserModel.update_profile(user_id, name, email)
                else:
                    UserModel.update_profile(user_id, name, email, currency=currency)

            session["user_name"] = name
            session["email"] = email
            if not is_admin:
                session["currency"] = currency
            log_activity(user_id, name, "Updated profile", "")
            user = UserModel.find_by_id(user_id)
            flash("Profile updated successfully.", "success")
            return render_template(template, user=user, is_admin=is_admin)

        return render_template(template, user=user, is_admin=is_admin)

    def update_currency(self):
        if not validate_csrf():
            flash("Invalid security token.", "danger")
            return redirect(request.referrer or url_for("auth.dashboard"))

        user_id = session["user_id"]
        currency = request.form.get("currency", "NPR")
        if currency not in CURRENCIES:
            currency = "NPR"

        UserModel.update_currency(user_id, currency)
        session["currency"] = currency
        flash("Currency updated.", "success")
        return redirect(request.referrer or url_for("auth.dashboard"))
#working correct