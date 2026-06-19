from flask import Blueprint
#Check routes
from app.auth import login_required, user_required
from app.controllers.auth_controller import AuthController


class AuthRoutes:
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()

        self.bp.route("/", methods=["GET"])(self.home)
        self.bp.route("/login", methods=["GET", "POST"])(self.login)
        self.bp.route("/register", methods=["GET", "POST"])(self.register)
        self.bp.route("/logout", methods=["GET"])(self.logout)
        self.bp.route("/dashboard", methods=["GET"])(self.dashboard)
        self.bp.route("/profile", methods=["GET", "POST"])(self.profile)
        self.bp.route("/profile/currency", methods=["POST"])(self.set_currency)

    def home(self):
        return self.controller.home()

    def login(self):
        return self.controller.login()

    def register(self):
        return self.controller.register()

    def logout(self):
        return self.controller.logout()

    @user_required
    def dashboard(self):
        return self.controller.dashboard()

    @login_required
    def profile(self):
        return self.controller.profile()

    @user_required
    def set_currency(self):
        return self.controller.update_currency()
#verification by kushumlata
#checked
