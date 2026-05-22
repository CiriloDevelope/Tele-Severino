from flask import Blueprint, render_template, request, redirect, url_for
from app.services.auth_service import login_user, register_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Futuro backend:
        # Validar usuário no PostgreSQL.
        login_user(email, password)

        return redirect(url_for("main.splash", next="/home"))

    return render_template("login.html")


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        account_type = request.form.get("account_type")

        # Futuro backend:
        # Criar usuário no PostgreSQL.
        register_user(name, email, password, account_type)

        return redirect(url_for("main.splash", next="/home"))

    return render_template("cadastro.html")
