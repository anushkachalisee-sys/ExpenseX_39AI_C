import hashlib
import secrets
from functools import wraps

from flask import flash, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, hashed):
    if not hashed:
        return False
    if check_password_hash(hashed, password):
        return True
    legacy = hashlib.sha256(password.encode()).hexdigest()
    return secrets.compare_digest(legacy, hashed)


def generate_csrf_token():
    token = secrets.token_hex(32)
    session["csrf_token"] = token
    return token


def validate_csrf():
    token = request.form.get("csrf_token", "")
    session_token = session.get("csrf_token", "")
    return token and session_token and secrets.compare_digest(token, session_token)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated


def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            flash("Access denied.", "danger")
            return redirect(url_for("auth.dashboard"))
        return f(*args, **kwargs)

    return decorated
#Working
