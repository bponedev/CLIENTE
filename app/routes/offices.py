"""
============================================================
 ROTAS DE GESTÃO DE ESCRITÓRIOS
============================================================
Responsável por:
- Listar escritórios
- Criar escritório
- Editar nome
- Excluir (somente ADMIN, exceto CENTRAL)
============================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import get_conn
from app.models import Offices
from app.utils import supervisor_required, admin_required


offices_bp = Blueprint("offices", __name__)


# ============================================================
# LISTA DE ESCRITÓRIOS
# ============================================================
@offices_bp.route("/offices", methods=["GET"])
@supervisor_required
def offices_page():
    """Lista todos os escritórios cadastrados."""

    with get_conn() as conn:
        offices = Offices.get_all(conn)

    return render_template("offices.html", offices=offices)


# ============================================================
# CRIAR ESCRITÓRIO
# ============================================================
@offices_bp.route("/offices", methods=["POST"])
@supervisor_required
def offices_create():
    """Cria um novo escritório no banco."""

    name = request.form.get("office_name")

    with get_conn() as conn:
        Offices.create(conn, name)

    flash("Escritório criado com sucesso!", "success")
    return redirect(url_for("offices.offices_page"))


# ============================================================
# EDITAR ESCRITÓRIO
# ============================================================
@offices_bp.route("/offices/<string:office_key>/edit", methods=["GET", "POST"])
@supervisor_required
def office_edit(office_key):
    """Tela de edição do nome de exibição de um escritório."""

    with get_conn() as conn:
        office = Offices.get(conn, office_key)

        if request.method == "GET":
            return render_template("office_edit.html", office=office)

        new_name = request.form.get("display_name")
        Offices.update(conn, office_key, new_name)

    flash("Escritório atualizado!", "success")
    return redirect(url_for("offices.offices_page"))


# ============================================================
# EXCLUIR ESCRITÓRIO
# ============================================================
@offices_bp.route("/offices/delete", methods=["POST"])
@admin_required
def offices_delete():
    """
    Exclui um escritório — exceto CENTRAL.
    Uso exclusivo ADMIN.
    """

    office_key = request.form.get("office_key")

    if office_key == "CENTRAL":
        flash("O escritório CENTRAL não pode ser removido!", "error")
        return redirect(url_for("offices.offices_page"))

    with get_conn() as conn:
        Offices.delete(conn, office_key)

    flash("Escritório excluído!", "success")
    return redirect(url_for("offices.offices_page"))
