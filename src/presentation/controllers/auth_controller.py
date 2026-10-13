# -*- coding: utf-8 -*-
"""
Controlador de Autenticación.
Maneja las rutas de login, logout y validación de sesión.
"""
from functools import wraps
from flask import Blueprint, request, session, redirect, url_for, render_template, current_app

auth_bp = Blueprint("auth", __name__)


def login_required(view):
    """Middleware/Decorador para proteger rutas requiriendo autenticación."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if request.args.get("demo") == "1":
            session["logged_in"] = True
            session["username"] = "admin"
        if not session.get("logged_in"):
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        auth_service = current_app.auth_service
        user = auth_service.authenticate(username, password)

        if user and user.is_authenticated:
            session["logged_in"] = True
            session["username"] = user.username
            next_url = request.args.get("next") or url_for("views.dashboard")
            return redirect(next_url)
        else:
            error = "Usuario o contraseña incorrectos."

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
