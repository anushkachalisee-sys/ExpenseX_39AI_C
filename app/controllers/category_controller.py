from flask import flash, redirect, render_template, request, session, url_for

from app.auth import validate_csrf
from app.models.category import CategoryModel


class CategoryController:
    def list_all(self):
        user_id = session["user_id"]
        categories = CategoryModel.get_all_with_counts(user_id)
        return render_template("categories/list.html", categories=categories)

    def add(self):
        user_id = session["user_id"]

        if request.method == "POST":
            if not validate_csrf():
                flash("Invalid security token. Please try again.", "danger")
                return redirect(url_for("categories.add"))

            name = request.form.get("name", "").strip()
            cat_type = request.form.get("type", "expense")

            if not name:
                flash("Category name is required.", "danger")
                return render_template("categories/form.html", category=None)

            if cat_type not in ("income", "expense"):
                cat_type = "expense"

            if CategoryModel.duplicate_exists(user_id, name, cat_type):
                flash("A category with this name and type already exists.", "danger")
                return render_template("categories/form.html", category=None)

            CategoryModel.create(user_id, name, cat_type)
            flash("Category created successfully.", "success")
            return redirect(url_for("categories.list_all"))

        return render_template("categories/form.html", category=None)

    def edit(self, cat_id):
        user_id = session["user_id"]
        category = CategoryModel.find_by_id(cat_id, user_id)
        if not category:
            flash("Category not found.", "danger")
            return redirect(url_for("categories.list_all"))

        if category.get("user_id") is None:
            flash("Global categories cannot be edited.", "danger")
            return redirect(url_for("categories.list_all"))

        if request.method == "POST":
            if not validate_csrf():
                flash("Invalid security token. Please try again.", "danger")
                return redirect(url_for("categories.edit", cat_id=cat_id))

            name = request.form.get("name", "").strip()
            cat_type = request.form.get("type", category["type"])

            if not name:
                flash("Category name is required.", "danger")
                return render_template("categories/form.html", category=category)

            if cat_type not in ("income", "expense"):
                cat_type = category["type"]

            if CategoryModel.duplicate_exists(user_id, name, cat_type, cat_id):
                flash("A category with this name and type already exists.", "danger")
                return render_template("categories/form.html", category=category)

            CategoryModel.update(cat_id, user_id, name, cat_type)
            flash("Category updated successfully.", "success")
            return redirect(url_for("categories.list_all"))

        return render_template("categories/form.html", category=category)

    def delete(self, cat_id):
        if not validate_csrf():
            flash("Invalid security token. Please try again.", "danger")
            return redirect(url_for("categories.list_all"))

        user_id = session["user_id"]
        category = CategoryModel.find_by_id(cat_id, user_id)
        if not category:
            flash("Category not found.", "danger")
            return redirect(url_for("categories.list_all"))

        if category.get("user_id") is None:
            flash("Global categories cannot be deleted.", "danger")
            return redirect(url_for("categories.list_all"))

        CategoryModel.delete(cat_id, user_id)
        flash("Category deleted.", "success")
        return redirect(url_for("categories.list_all"))
#working correct