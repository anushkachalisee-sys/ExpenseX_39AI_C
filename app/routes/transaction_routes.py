from flask import Blueprint

from app.auth import user_required
from app.controllers.transaction_controller import TransactionController


class TransactionRoutes:
    def __init__(self):
        self.bp = Blueprint("transactions", __name__)
        self.controller = TransactionController()

        self.bp.route("/income", methods=["GET"])(self.list_income)
        self.bp.route("/expense", methods=["GET"])(self.list_expense)
        self.bp.route("/search", methods=["GET"])(self.search)
        self.bp.route("/add", methods=["GET", "POST"])(self.add)
        self.bp.route("/edit/<int:txn_id>", methods=["GET", "POST"])(self.edit)
        self.bp.route("/delete/<int:txn_id>", methods=["POST"])(self.delete)

    @user_required
    def list_income(self):
        return self.controller.list_income()

    @user_required
    def list_expense(self):
        return self.controller.list_expense()

    @user_required
    def search(self):
        return self.controller.search()

    @user_required
    def add(self):
        return self.controller.add()

    @user_required
    def edit(self, txn_id):
        return self.controller.edit(txn_id)

    @user_required
    def delete(self, txn_id):
        return self.controller.delete(txn_id)
