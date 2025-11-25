"""
ROTAS DE AUTENTICAÇÃO
- login
- logout
"""

from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from app.db_helpers import query

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = query("""
            SELECT * FROM users WHERE username=? AND password=? AND active=1
        """, (request.form["username"], request.form["password"]), one=True)

        if not user:
            flash("Usuário ou senha inválidos", "error")
            return redirect(url_for("auth.login"))

        session["user"] = dict(user)
        return redirect(url_for("registros.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
