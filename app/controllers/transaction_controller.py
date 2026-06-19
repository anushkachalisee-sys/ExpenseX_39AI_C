import math
from datetime import date
#working in this file
#checking
from flask import flash, redirect, render_template, request, session, url_for

from app.currency import to_npr
from app.auth import validate_csrf
from app.database import log_activity
from app.models.budget import BudgetModel
from app.models.category import CategoryModel
from app.models.transaction import TransactionModel
from app.models.user import UserModel


class TransactionController:
    def _check_achievements(self, user_id):
        totals = UserModel.get_totals(user_id)
        streak = session.get("streak", 0)
        unlocked = BudgetModel.check_and_unlock_achievements(user_id, totals, streak)
        for title in unlocked:
            flash(f"Achievement unlocked: {title}!", "success")

    def _parse_amount_to_npr(self, amount_str):
        currency = session.get("currency", "NPR")
        amount = float(amount_str)
        return to_npr(amount, currency)

    def _pagination(self, total, page, per_page):
        total_pages = max(1, math.ceil(total / per_page))
        page = max(1, min(page, total_pages))
        return {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
        }

    def list_income(self):
        user_id = session["user_id"]
        month = request.args.get("month")
        category_id = request.args.get("category_id", type=int)
        page = request.args.get("page", 1, type=int)
        per_page = TransactionModel.PER_PAGE
        month_val = month or date.today().strftime("%Y-%m")
        total = TransactionModel.count_by_type(
            user_id, "income", month_val, category_id
        )
        transactions = TransactionModel.list_by_type(
            user_id, "income", month_val, category_id, page, per_page
        )
        categories = CategoryModel.get_by_type(user_id, "income")
        total_amount = sum(float(t["amount"]) for t in transactions)
        pagination = self._pagination(total, page, per_page)
        return render_template(
            "transactions/income.html",
            transactions=transactions,
            categories=categories,
            month=month_val,
            category_id=category_id,
            total=total_amount,
            pagination=pagination,
            txn_type="income",
        )

    def list_expense(self):
        user_id = session["user_id"]
        month = request.args.get("month")
        category_id = request.args.get("category_id", type=int)
        page = request.args.get("page", 1, type=int)
        per_page = TransactionModel.PER_PAGE
        month_val = month or date.today().strftime("%Y-%m")
        total = TransactionModel.count_by_type(
            user_id, "expense", month_val, category_id
        )
        transactions = TransactionModel.list_by_type(
            user_id, "expense", month_val, category_id, page, per_page
        )
        categories = CategoryModel.get_by_type(user_id, "expense")
        total_amount = sum(float(t["amount"]) for t in transactions)
        pagination = self._pagination(total, page, per_page)
        return render_template(
            "transactions/expense.html",
            transactions=transactions,
            categories=categories,
            month=month_val,
            category_id=category_id,
            total=total_amount,
            pagination=pagination,
            txn_type="expense",
        )

    def search(self):
        user_id = session["user_id"]
        query = request.args.get("q", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = TransactionModel.PER_PAGE

        if not query:
            return render_template(
                "transactions/search.html",
                transactions=[],
                query="",
                total=0,
                pagination=self._pagination(0, 1, per_page),
            )

        total_count = TransactionModel.count_search(user_id, query)
        transactions = TransactionModel.search(user_id, query, page, per_page)
        total_amount = sum(float(t["amount"]) for t in transactions)
        pagination = self._pagination(total_count, page, per_page)

        return render_template(
            "transactions/search.html",
            transactions=transactions,
            query=query,
            total=total_amount,
            pagination=pagination,
        )

    def _form_context(self, user_id, txn_type, transaction=None):
        return {
            "transaction": transaction,
            "categories": CategoryModel.get_by_type(user_id, txn_type),
            "txn_type": txn_type,
        }

    def add(self):
        user_id = session["user_id"]
        txn_type = request.args.get("type", "expense")
        if txn_type not in ("income", "expense"):
            txn_type = "expense"

        if request.method == "POST":
            if not validate_csrf():
                flash("Invalid security token. Please try again.", "danger")
                return redirect(url_for("transactions.add", type=txn_type))

            txn_type = request.form.get("type", txn_type)
            amount_str = request.form.get("amount", "")
            description = request.form.get("description", "").strip()
            notes = request.form.get("notes", "").strip()
            txn_date = request.form.get("date", "")
            category_id = request.form.get("category_id", type=int) or None
            is_recurring = 1 if request.form.get("is_recurring") else 0
            recurrence = request.form.get("recurrence") or None
            if not is_recurring:
                recurrence = None

            try:
                amount = self._parse_amount_to_npr(amount_str)
                if amount <= 0:
                    raise ValueError()
            except (TypeError, ValueError):
                flash("Amount must be a positive number.", "danger")
                return render_template(
                    "transactions/form.html",
                    **self._form_context(user_id, txn_type),
                )

            if not txn_date:
                flash("Date is required.", "danger")
                return render_template(
                    "transactions/form.html",
                    **self._form_context(user_id, txn_type),
                )

            TransactionModel.create(
                user_id,
                category_id,
                txn_type,
                amount,
                description,
                txn_date,
                notes=notes or None,
                is_recurring=is_recurring,
                recurrence=recurrence,
            )
            self._check_achievements(user_id)
            log_activity(
                user_id,
                session.get("user_name", ""),
                f"Added {txn_type}",
                f"Rs.{amount:.2f}",
            )
            flash(f"{txn_type.capitalize()} added successfully.", "success")
            if txn_type == "income":
                return redirect(url_for("transactions.list_income"))
            return redirect(url_for("transactions.list_expense"))

        return render_template(
            "transactions/form.html",
            **self._form_context(user_id, txn_type),
        )

    def edit(self, txn_id):
        user_id = session["user_id"]
        transaction = TransactionModel.find_by_id(txn_id, user_id)
        if not transaction:
            flash("Transaction not found.", "danger")
            return redirect(url_for("auth.dashboard"))

        txn_type = transaction["type"]

        if request.method == "POST":
            if not validate_csrf():
                flash("Invalid security token. Please try again.", "danger")
                return redirect(url_for("transactions.edit", txn_id=txn_id))

            txn_type = request.form.get("type", txn_type)
            amount_str = request.form.get("amount", "")
            description = request.form.get("description", "").strip()
            notes = request.form.get("notes", "").strip()
            txn_date = request.form.get("date", "")
            category_id = request.form.get("category_id", type=int) or None
            is_recurring = 1 if request.form.get("is_recurring") else 0
            recurrence = request.form.get("recurrence") or None
            if not is_recurring:
                recurrence = None

            try:
                amount = self._parse_amount_to_npr(amount_str)
                if amount <= 0:
                    raise ValueError()
            except (TypeError, ValueError):
                flash("Amount must be a positive number.", "danger")
                return render_template(
                    "transactions/form.html",
                    **self._form_context(user_id, txn_type, transaction),
                )

            if not txn_date:
                flash("Date is required.", "danger")
                return render_template(
                    "transactions/form.html",
                    **self._form_context(user_id, txn_type, transaction),
                )

            TransactionModel.update(
                txn_id,
                user_id,
                category_id,
                txn_type,
                amount,
                description,
                txn_date,
                notes=notes or None,
                is_recurring=is_recurring,
                recurrence=recurrence,
            )
            self._check_achievements(user_id)
            flash("Transaction updated successfully.", "success")
            if txn_type == "income":
                return redirect(url_for("transactions.list_income"))
            return redirect(url_for("transactions.list_expense"))

        return render_template(
            "transactions/form.html",
            **self._form_context(user_id, txn_type, transaction),
        )

    def delete(self, txn_id):
        if not validate_csrf():
            flash("Invalid security token. Please try again.", "danger")
            return redirect(url_for("auth.dashboard"))

        user_id = session["user_id"]
        transaction = TransactionModel.find_by_id(txn_id, user_id)
        if not transaction:
            flash("Transaction not found.", "danger")
            return redirect(url_for("auth.dashboard"))

        txn_type = transaction["type"]
        amount = float(transaction["amount"])
        TransactionModel.delete(txn_id, user_id)
        log_activity(
            user_id,
            session.get("user_name", ""),
            f"Deleted {txn_type}",
            f"Rs.{amount:.2f}",
        )
        flash("Transaction deleted.", "success")
        if txn_type == "income":
            return redirect(url_for("transactions.list_income"))
        return redirect(url_for("transactions.list_expense"))
#working correct