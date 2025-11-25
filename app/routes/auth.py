from flask import Blueprint, render_template, redirect, request, session
from app.utils import success, error

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        pw = request.form.get("password")

        if user == "admin" and pw == "123":
            session["user"] = user
            success("Login realizado!")
            return redirect("/")

        error("Usuário ou senha inválidos")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    success("Sessão encerrada.")
    return redirect("/login")
