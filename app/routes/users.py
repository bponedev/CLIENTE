"""
Gerenciamento de usuários.
"""

from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.db_helpers import query, execute

users_bp = Blueprint("users", __name__)


@users_bp.route("/admin/users")
def admin_users():
    users = query("SELECT * FROM users")
    return render_template("admin_users.html", users=users)


@users_bp.route("/admin/users/create", methods=["GET", "POST"])
def admin_users_create():
    if request.method == "POST":
        execute("""
            INSERT INTO users (username, full_name, password, role)
            VALUES (?, ?, ?, ?)
        """, (request.form["username"], request.form["full_name"],
              request.form["password"], request.form["role"]))

        flash("Usuário criado!", "success")
        return redirect(url_for("users.admin_users"))

    offices = query("SELECT * FROM offices")
    return render_template("admin_users_create.html", offices=offices)


@users_bp.route("/admin/users/edit/<int:id>", methods=["GET", "POST"])
def admin_users_edit(id):
    user = query("SELECT * FROM users WHERE id=?", (id,), one=True)

    if request.method == "POST":
        execute("""
            UPDATE users SET full_name=?, role=?, active=?
            WHERE id=?
        """, (
            request.form["full_name"],
            request.form["role"],
            request.form["active"],
            id
        ))
        flash("Alterado!", "success")
        return redirect(url_for("users.admin_users"))

    return render_template("admin_users_edit.html", user=user)
