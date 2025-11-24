"""
============================================================
 ROTAS DE ADMINISTRAÇÃO DE USUÁRIOS
============================================================
Responsável por:
- Listar usuários
- Criar usuário
- Editar informações
- Vincular escritórios
- Resetar senha
- Excluir usuário
============================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import get_conn
from app.models import Users, Offices
from app.utils import admin_required, supervisor_required


users_bp = Blueprint("users", __name__)


# ============================================================
# LISTAGEM DE USUÁRIOS
# ============================================================
@users_bp.route("/admin/users")
@supervisor_required
def admin_users():
    """Lista todos os usuários cadastrados no sistema."""

    with get_conn() as conn:
        users = Users.get_all(conn)
        offices = Offices.get_all(conn)

    # Ajusta escritórios vinculados para cada usuário
    for u in users:
        u.offices = Users.get_user_offices(conn, u.id)

    return render_template("admin_users.html", users=users)


# ============================================================
# CRIAR USUÁRIO
# ============================================================
@users_bp.route("/admin/users/create", methods=["GET", "POST"])
@supervisor_required
def admin_users_create():
    """
    Tela para criar novo usuário.
    Ao enviar (POST), grava no banco e redireciona.
    """

    with get_conn() as conn:
        offices = Offices.get_all(conn)

        if request.method == "GET":
            return render_template("admin_users_create.html", offices=offices)

        # Dados enviados do formulário
        data = {
            "username": request.form.get("username"),
            "full_name": request.form.get("full_name"),
            "password": request.form.get("password"),
            "role": request.form.get("role"),
        }

        # Criar usuário
        new_id = Users.create(conn, data)

        # Escritórios vinculados
        offices_selected = request.form.getlist("offices")
        Users.update_user_offices(conn, new_id, offices_selected)

        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("users.admin_users"))


# ============================================================
# EDITAR USUÁRIO
# ============================================================
@users_bp.route("/admin/users/<int:user_id>/edit", methods=["GET", "POST"])
@supervisor_required
def admin_users_edit(user_id):
    """Edita nome, role e status de um usuário."""

    with get_conn() as conn:
        user = Users.get(conn, user_id)

        if request.method == "GET":
            return render_template("admin_users_edit.html", user=user)

        # Atualizar usuário
        Users.update(
            conn,
            user_id,
            full_name=request.form.get("full_name"),
            role=request.form.get("role"),
            active=request.form.get("active"),
        )

        flash("Usuário atualizado!", "success")
        return redirect(url_for("users.admin_users"))


# ============================================================
# VINCULAR ESCRITÓRIOS
# ============================================================
@users_bp.route("/admin/users/<int:user_id>/offices", methods=["GET", "POST"])
@supervisor_required
def admin_users_offices(user_id):
    """Tela de vinculação dos escritórios a um usuário."""

    with get_conn() as conn:
        user = Users.get(conn, user_id)
        offices = Offices.get_all(conn)
        assigned = Users.get_user_offices(conn, user_id)

        if request.method == "GET":
            return render_template(
                "admin_users_offices.html",
                user=user,
                offices=offices,
                assigned=assigned,
            )

        selected = request.form.getlist("offices")
        Users.update_user_offices(conn, user_id, selected)

        flash("Escritórios atualizados!", "success")
        return redirect(url_for("users.admin_users"))


# ============================================================
# RESETAR SENHA (ADMIN)
# ============================================================
@users_bp.route("/admin/users/<int:user_id>/reset", methods=["POST"])
@admin_required
def admin_users_reset_password(user_id):
    """Redefine senha para '123456'."""

    with get_conn() as conn:
        Users.update(conn, user_id, password="123456")

    flash("Senha redefinida para 123456", "success")
    return redirect(url_for("users.admin_users"))


# ============================================================
# EXCLUIR USUÁRIO
# ============================================================
@users_bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_users_delete(user_id):
    """Remove um usuário definitivamente."""

    with get_conn() as conn:
        Users.delete(conn, user_id)

    flash("Usuário removido!", "success")
    return redirect(url_for("users.admin_users"))
