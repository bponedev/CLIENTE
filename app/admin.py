"""
admin.py
--------
Funções administrativas auxiliares.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .extensions import get_conn

admin_bp = Blueprint("admin_extra", __name__, url_prefix="/admin")


# =============================================================================
# ALTERAR SENHA PRÓPRIA
# =============================================================================
@admin_bp.route("/change_password", methods=["GET", "POST"])
def change_password():

    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        old = request.form.get("old")
        new = request.form.get("new")

        conn = get_conn()
        c = conn.cursor()

        c.execute("SELECT password FROM users WHERE id=?", (user["id"],))
        current = c.fetchone()[0]

        if current != old:
            flash("Senha atual incorreta.", "error")
            conn.close()
            return redirect(url_for("admin_extra.change_password"))

        c.execute("UPDATE users SET password=? WHERE id=?", (new, user["id"]))
        conn.commit()
        conn.close()

        flash("Senha alterada!", "success")
        return redirect(url_for("records.index"))

    return render_template("admin_change_password.html")
