"""
============================================================
 ROTAS DE AUTENTICAÇÃO (LOGIN / LOGOUT)
============================================================
Responsável por:
- Exibir a tela de login
- Validar credenciais
- Criar sessão do usuário
- Encerrar sessão
============================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Users
from app.extensions import get_conn
from app.utils import login_required


auth = Blueprint("auth", __name__)


# ============================================================
#  LOGIN — Tela de Login (GET) e Validação (POST)
# ============================================================
@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Exibe o formulário de login.
    Caso seja POST, valida usuário e senha,
    salva sessão e redireciona para a tela principal.
    """

    # GET → Apenas exibe a página
    if request.method == "GET":
        return render_template("login.html")

    # POST → Validar credenciais
    username = request.form.get("username")
    password = request.form.get("password")

    with get_conn() as conn:
        user = Users.get_by_username(conn, username)

        if not user or user.password != password:
            flash("Credenciais inválidas", "error")
            return redirect(url_for("auth.login"))

        if user.active != 1:
            flash("Usuário inativo", "error")
            return redirect(url_for("auth.login"))

    # Criar sessão
    session["user_id"] = user.id

    flash("Login realizado com sucesso!", "success")
    return redirect(url_for("registros.index"))
    


# ============================================================
# LOGOUT — Remove sessão e volta ao login
# ============================================================
@auth.route("/logout")
@login_required
def logout():
    """Remove sessão e retorna ao login."""
    session.clear()
    flash("Sessão encerrada.", "success")
    return redirect(url_for("auth.login"))
