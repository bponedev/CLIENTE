"""
users.py
--------
Camada de gerenciamento de usuários.
Inclui CRUD e vínculo com escritórios.

Funções:
 - Listar usuários
 - Criar usuário
 - Editar usuário
 - Resetar senha
 - Excluir usuário
 - Gerenciar escritórios do usuário
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .extensions import get_conn
from .utils import list_offices, office_keys_to_list

users_bp = Blueprint("users", __name__, url_prefix="/users")


# =============================================================================
# LISTAGEM COMPLETA DE USUÁRIOS (ADMIN)
# =============================================================================
@users_bp.route("/")
def admin_users():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT id, username, full_name, role, active, offices, created_at
        FROM users
        ORDER BY id DESC
    """)

    rows = c.fetchall()
    conn.close()

    users = []
    for r in rows:
        users.append({
            "id": r[0],
            "username": r[1],
            "full_name": r[2],
            "role": r[3],
            "active": r[4],
            "offices": office_keys_to_list(r[5]),
            "created_at": r[6]
        })

    return render_template("admin_users.html", users=users)


# =============================================================================
# CRIAR NOVO USUÁRIO
# =============================================================================
@users_bp.route("/create", methods=["GET", "POST"])
def admin_users_create():

    if request.method == "POST":
        username = request.form.get("username")
        full_name = request.form.get("full_name")
        password = request.form.get("password")
        role = request.form.get("role")
        offices = request.form.getlist("offices")

        offices_str = ",".join(offices)

        conn = get_conn()
        c = conn.cursor()

        c.execute("""
            INSERT INTO users (username, full_name, password, role, active, offices)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (username, full_name, password, role, offices_str))

        conn.commit()
        conn.close()
        flash("Usuário criado com sucesso!", "success")

        return redirect(url_for("users.admin_users"))

    offices = list_offices()
    return render_template("admin_users_create.html", offices=offices)


# =============================================================================
# EDITAR USUÁRIO
# =============================================================================
@users_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
def admin_users_edit(user_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT id, username, full_name, role, active
        FROM users WHERE id=?
    """, (user_id,))

    row = c.fetchone()

    if not row:
        conn.close()
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("users.admin_users"))

    user = {
        "id": row[0],
        "username": row[1],
        "full_name": row[2],
        "role": row[3],
        "active": row[4]
    }

    if request.method == "POST":
        full_name = request.form.get("full_name")
        role = request.form.get("role")
        active = request.form.get("active")

        c.execute("""
            UPDATE users SET
                full_name=?, role=?, active=?
            WHERE id=?
        """, (full_name, role, active, user_id))

        conn.commit()
        conn.close()
        flash("Usuário atualizado!", "success")
        return redirect(url_for("users.admin_users"))

    conn.close()
    return render_template("admin_users_edit.html", user=user)


# =============================================================================
# GERENCIAR ESCRITÓRIOS DO USUÁRIO
# =============================================================================
@users_bp.route("/offices/<int:user_id>", methods=["GET", "POST"])
def admin_users_offices(user_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT offices, full_name FROM users WHERE id=?", (user_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("users.admin_users"))

    assigned = office_keys_to_list(row[0])
    full_name = row[1]

    offices = list_offices()

    if request.method == "POST":
        new_list = request.form.getlist("offices")
        offices_str = ",".join(new_list)

        c.execute("UPDATE users SET offices=? WHERE id=?", (offices_str, user_id))
        conn.commit()
        conn.close()
        flash("Vínculos atualizados!", "success")

        return redirect(url_for("users.admin_users"))

    conn.close()
    return render_template(
        "admin_users_offices.html",
        user={"id": user_id, "full_name": full_name},
        offices=offices,
        assigned=assigned
    )


# =============================================================================
# RESET PASSWORD
# =============================================================================
@users_bp.route("/reset/<int:user_id>", methods=["POST"])
def admin_users_reset_password(user_id):

    new_pass = request.form.get("new_password", "123456")

    conn = get_conn()
    c = conn.cursor()

    c.execute("UPDATE users SET password=? WHERE id=?", (new_pass, user_id))
    conn.commit()
    conn.close()

    flash("Senha redefinida!", "success")
    return redirect(url_for("users.admin_users"))


# =============================================================================
# DELETE USER
# =============================================================================
@users_bp.route("/delete/<int:user_id>", methods=["POST"])
def admin_users_delete(user_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    flash("Usuário removido!", "success")
    return redirect(url_for("users.admin_users"))
