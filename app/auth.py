"""
auth.py
-------
Controle de login, logout e sessão do usuário.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .extensions import get_conn

auth_bp = Blueprint("auth", __name__)


# =============================================================================
# LOGIN
# =============================================================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_conn()
        c = conn.cursor()

        c.execute("""
            SELECT id, username, full_name, role, active
            FROM users
            WHERE username=? AND password=?
        """, (username, password))

        row = c.fetchone()
        conn.close()

        if not row:
            flash("Usuário ou senha inválidos.", "error")
            return redirect(url_for("auth.login"))

        if row[4] == 0:
            flash("Usuário inativo.", "error")
            return redirect(url_for("auth.login"))

        session["user"] = {
            "id": row[0],
            "username": row[1],
            "full_name": row[2],
            "role": row[3]
        }

        return redirect(url_for("records.index"))

    return render_template("login.html")


# =============================================================================
# LOGOUT
# =============================================================================
@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login"))


# =============================================================================
# Helper para acesso a partir dos templates
# =============================================================================
@auth_bp.app_context_processor
def inject_user():
    return {"current_user": session.get("user")}
