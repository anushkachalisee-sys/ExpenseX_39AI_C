from flask import flash, redirect, render_template, request, session, url_for

from app.currency import CURRENCIES, to_npr
from app.auth import validate_csrf
from app.models.budget import BudgetModel
from app.models.transaction import TransactionModel
from app.models.user import UserModel


class BudgetController:
    def index(self):
        user_id = session["user_id"]
        budget = BudgetModel.get_budget(user_id)
        goals = BudgetModel.get_goals(user_id)
        achievements = BudgetModel.get_achievements(user_id)
        achievement_defs = BudgetModel.ACHIEVEMENTS
        summary = TransactionModel.get_monthly_summary(user_id)
        today_expense = TransactionModel.get_today_expense(user_id)

        monthly_limit = float(budget["monthly_limit"]) if budget else 0.0
        daily_limit = float(budget["daily_limit"]) if budget else 0.0

        return render_template(
            "budget/index.html",
            budget=budget,
            goals=goals,
            achievements=achievements,
            achievement_defs=achievement_defs,
            summary=summary,
            today_expense=today_expense,
            monthly_limit=monthly_limit,
            daily_limit=daily_limit,
        )

    def set_budget(self):
        if not validate_csrf():
            flash("Invalid security token. Please try again.", "danger")
            return redirect(url_for("budget.index"))

        user_id = session["user_id"]
        currency = session.get("currency", "NPR")
        try:
            monthly_display = float(request.form.get("monthly_limit", 0) or 0)
            daily_display = float(request.form.get("daily_limit", 0) or 0)
            monthly_limit = to_npr(monthly_display, currency)
            daily_limit = to_npr(daily_display, currency)
            if monthly_limit < 0 or daily_limit < 0:
                raise ValueError()
        except (TypeError, ValueError):
            flash("Limits must be valid non-negative numbers.", "danger")
            return redirect(url_for("budget.index"))

        BudgetModel.upsert_budget(user_id, monthly_limit, daily_limit)
        flash("Budget limits updated.", "success")
        return redirect(url_for("budget.index"))

    def add_goal(self):
        if not validate_csrf():
            flash("Invalid security token. Please try again.", "danger")
            return redirect(url_for("budget.index"))

        user_id = session["user_id"]
        currency = session.get("currency", "NPR")
        title = request.form.get("title", "").strip()
        target_str = request.form.get("target_amount", "")
        deadline = request.form.get("deadline", "").strip() or None

        if not title:
            flash("Goal title is required.", "danger")
            return redirect(url_for("budget.index"))

        try:
            target_display = float(target_str)
            if target_display <= 0:
                raise ValueError()
            target_amount = to_npr(target_display, currency)
        except (TypeError, ValueError):
            flash("Target amount must be a positive number.", "danger")
            return redirect(url_for("budget.index"))

        BudgetModel.add_goal(user_id, title, target_amount, deadline)
        flash("Savings goal created.", "success")
        return redirect(url_for("budget.index"))

    def update_goal(self, goal_id):
        if not validate_csrf():
            flash("Invalid security token. Please try again.", "danger")
            return redirect(url_for("budget.index"))

        user_id = session["user_id"]
        currency = session.get("currency", "NPR")
        goal = BudgetModel.find_goal(goal_id, user_id)
        if not goal:
            flash("Goal not found.", "danger")
            return redirect(url_for("budget.index"))

        title = request.form.get("title", "").strip()
        target_str = request.form.get("target_amount", "")
        current_str = request.form.get("current_amount", "0")
        deadline = request.form.get("deadline", "").strip() or None

        if not title:
            flash("Goal title is required.", "danger")
            return redirect(url_for("budget.index"))

        try:
            target_display = float(target_str)
            current_display = float(current_str)
            if target_display <= 0 or current_display < 0:
                raise ValueError()
            target_amount = to_npr(target_display, currency)
            current_amount = to_npr(current_display, currency)
        except (TypeError, ValueError):
            flash("Amounts must be valid numbers.", "danger")
            return redirect(url_for("budget.index"))

        was_completed = goal.get("completed", 0)
        completed = BudgetModel.update_goal(
            goal_id, user_id, title, target_amount, current_amount, deadline
        )

        if completed and not was_completed:
            BudgetModel.unlock_goal_achievement(user_id)
            flash(
                "Congratulations! Goal completed and achievement unlocked!",
                "success",
            )
        else:
            flash("Goal updated.", "success")

        return redirect(url_for("budget.index"))

    def delete_goal(self, goal_id):
        if not validate_csrf():
            flash("Invalid security token. Please try again.", "danger")
            return redirect(url_for("budget.index"))

        user_id = session["user_id"]
        goal = BudgetModel.find_goal(goal_id, user_id)
        if not goal:
            flash("Goal not found.", "danger")
            return redirect(url_for("budget.index"))

        BudgetModel.delete_goal(goal_id, user_id)
        flash("Goal deleted.", "success")
        return redirect(url_for("budget.index"))
#working correct