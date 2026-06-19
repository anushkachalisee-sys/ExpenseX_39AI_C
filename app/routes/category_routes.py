from flask import Blueprint
#Check routes
from app.auth import user_required
from app.controllers.category_controller import CategoryController


class CategoryRoutes:
    def __init__(self):
        self.bp = Blueprint("categories", __name__)
        self.controller = CategoryController()

        self.bp.route("/", methods=["GET"])(self.list_all)
        self.bp.route("/add", methods=["GET", "POST"])(self.add)
        self.bp.route("/edit/<int:cat_id>", methods=["GET", "POST"])(self.edit)
        self.bp.route("/delete/<int:cat_id>", methods=["POST"])(self.delete)

    @user_required
    def list_all(self):
        return self.controller.list_all()

    @user_required
    def add(self):
        return self.controller.add()

    @user_required
    def edit(self, cat_id):
        return self.controller.edit(cat_id)

    @user_required
    def delete(self, cat_id):
        return self.controller.delete(cat_id)
# verification by kushumlata
#checked
