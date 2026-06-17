from flask import Blueprint

from app.auth import user_required
from app.controllers.report_controller import ReportController


class ReportRoutes:
    def __init__(self):
        self.bp = Blueprint("reports", __name__)
        self.controller = ReportController()

        self.bp.route("/", methods=["GET"])(self.index)
        self.bp.route("/export/csv", methods=["GET"])(self.export_csv)
        self.bp.route("/export/pdf", methods=["GET"])(self.export_pdf)
        self.bp.route("/export/excel", methods=["GET"])(self.export_excel)

    @user_required
    def index(self):
        return self.controller.index()

    @user_required
    def export_csv(self):
        return self.controller.export_csv()

    @user_required
    def export_pdf(self):
        return self.controller.export_pdf()

    @user_required
    def export_excel(self):
        return self.controller.export_excel()
