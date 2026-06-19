from flask import Blueprint
#Check routes
#working
from app.auth import admin_required
from app.controllers.admin_controller import AdminController


class AdminRoutes:
    def __init__(self):
        self.bp = Blueprint("admin", __name__)
        self.controller = AdminController()

        self.bp.route("/", methods=["GET"])(self.dashboard)
        self.bp.route("/users", methods=["GET"])(self.users)
        self.bp.route("/users/<int:user_id>", methods=["GET"])(self.user_detail)
        self.bp.route("/users/<int:user_id>/toggle", methods=["POST"])(self.toggle_status)
        self.bp.route("/users/<int:user_id>/role", methods=["POST"])(self.change_role)
        self.bp.route("/users/<int:user_id>/delete", methods=["POST"])(self.delete_user)
        self.bp.route("/audit", methods=["GET"])(self.audit_log)
        self.bp.route("/audit/export/excel", methods=["GET"])(self.audit_export)
        self.bp.route("/categories", methods=["GET"])(self.global_categories)
        self.bp.route("/categories/add", methods=["POST"])(self.add_global_category)
        self.bp.route(
            "/categories/<int:cat_id>/delete", methods=["POST"]
        )(self.delete_global_category)

    @admin_required
    def dashboard(self):
        return self.controller.dashboard()

    @admin_required
    def users(self):
        return self.controller.users()

    @admin_required
    def user_detail(self, user_id):
        return self.controller.user_detail(user_id)

    @admin_required
    def toggle_status(self, user_id):
        return self.controller.toggle_status(user_id)

    @admin_required
    def change_role(self, user_id):
        return self.controller.change_role(user_id)

    @admin_required
    def delete_user(self, user_id):
        return self.controller.delete_user(user_id)

    @admin_required
    def audit_log(self):
        return self.controller.audit_log()

    @admin_required
    def audit_export(self):
        return self.controller.audit_export_excel()

    @admin_required
    def global_categories(self):
        return self.controller.global_categories()

    @admin_required
    def add_global_category(self):
        return self.controller.add_global_category()

    @admin_required
    def delete_global_category(self, cat_id):
        return self.controller.delete_global_category(cat_id)
#verification by kushumlata
#checked
