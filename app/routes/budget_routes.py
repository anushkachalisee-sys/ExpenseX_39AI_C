from flask import Blueprint
#Check routes
from app.auth import user_required
from app.controllers.budget_controller import BudgetController


class BudgetRoutes:
    def __init__(self):
        self.bp = Blueprint("budget", __name__)
        self.controller = BudgetController()

        self.bp.route("/", methods=["GET"])(self.index)
        self.bp.route("/set", methods=["POST"])(self.set_budget)
        self.bp.route("/goal/add", methods=["POST"])(self.add_goal)
        self.bp.route("/goal/update/<int:goal_id>", methods=["POST"])(self.update_goal)
        self.bp.route("/goal/delete/<int:goal_id>", methods=["POST"])(self.delete_goal)

    @user_required
    def index(self):
        return self.controller.index()

    @user_required
    def set_budget(self):
        return self.controller.set_budget()

    @user_required
    def add_goal(self):
        return self.controller.add_goal()

    @user_required
    def update_goal(self, goal_id):
        return self.controller.update_goal(goal_id)

    @user_required
    def delete_goal(self, goal_id):
        return self.controller.delete_goal(goal_id)
#verification by kushumlata
#checked
