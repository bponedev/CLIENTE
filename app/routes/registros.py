"""
============================================================
 ROTAS DE REGISTROS (CRUD COMPLETO)
============================================================
Responsável por:
- Tela principal (novo registro)
- Gravação
- Edição
- Listagem
- Exclusão lógica
- Exclusão permanente
- Restauração
============================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils import login_required
from app.extensions import get_conn
from app.models import Registros, Users


registros = Blueprint("registros", __name__)


# ============================================================
# TELA PRINCIPAL — FORMULÁRIO DE NOVO REGISTRO
# ============================================================
@registros.route("/")
@login_required
def index():
    """Exibe formulário de cadastro inicial."""
    return render_template("index.html")


# ============================================================
# SALVAR NOVO REGISTRO (submit.html)
# ============================================================
@registros.route("/submit", methods=["POST"])
@login_required
def submit():
    """Recebe dados do formulário e salva no banco."""

    data = {
        "nome": request.form.get("nome"),
        "cpf": request.form.get("cpf"),
        "escritorio_dono": request.form.get("escritorio_dono"),
        "tipo_acao": request.form.get("tipo_acao"),
        "data_fechamento": request.form.get("data_fechamento"),
        "tags": request.form.get("tags"),
    }

    with get_conn() as conn:
        Registros.create(conn, data)

    flash("Registro criado com sucesso!", "success")
    return redirect(url_for("registros.index"))


# ============================================================
# LISTAR REGISTROS POR ESCRITÓRIO
# ============================================================
@registros.route("/table/<string:office>")
@login_required
def table(office):
    """Lista registros não excluídos de um escritório."""

    with get_conn() as conn:
        rows = Registros.list_by_office(conn, office)

    return render_template("table.html", rows=rows, office=office)


# ============================================================
# EDITAR REGISTRO
# ============================================================
@registros.route("/edit/<int:reg_id>", methods=["GET", "POST"])
@login_required
def edit(reg_id):
    """Edita informações de um registro existente."""

    with get_conn() as conn:
        reg = Registros.get(conn, reg_id)

        if request.method == "GET":
            return render_template("edit.html", r=reg)

        # Atualizar registro
        Registros.update(
            conn,
            reg_id,
            nome=request.form.get("nome"),
            cpf=request.form.get("cpf"),
            tipo_acao=request.form.get("tipo_acao"),
            data_fechamento=request.form.get("data_fechamento"),
            tags=request.form.get("tags"),
        )

        flash("Registro atualizado!", "success")
        return redirect(url_for("registros.table", office=reg.escritorio_dono))


# ============================================================
# EXCLUIR (LÓGICO)
# ============================================================
@registros.route("/delete", methods=["POST"])
@login_required
def delete():
    """Exclusão lógica — move registro para área de excluídos."""

    reg_id = request.form.get("id")

    with get_conn() as conn:
        Registros.soft_delete(conn, reg_id)

    flash("Registro movido para excluídos.", "success")
    return redirect(request.referrer)


# ============================================================
# LISTAR EXCLUÍDOS
# ============================================================
@registros.route("/excluidos")
@login_required
def excluidos():
    """Lista registros excluídos logicamente."""

    with get_conn() as conn:
        rows = Registros.list_deleted(conn)

    return render_template("excluidos.html", rows=rows)


# ============================================================
# RESTAURAR
# ============================================================
@registros.route("/restore", methods=["POST"])
@login_required
def restore():
    """Restaura registro excluído logicamente."""

    reg_id = request.form.get("id")

    with get_conn() as conn:
        Registros.restore(conn, reg_id)

    flash("Registro restaurado!", "success")
    return redirect(url_for("registros.excluidos"))


# ============================================================
# EXCLUSÃO PERMANENTE (ADMIN)
# ============================================================
@registros.route("/delete-forever", methods=["POST"])
@login_required
def delete_forever():
    """Remove registro definitivamente (somente ADMIN)."""

    reg_id = request.form.get("id")

    with get_conn() as conn:
        Registros.delete_forever(conn, reg_id)

    flash("Registro removido permanentemente!", "success")
    return redirect(url_for("registros.excluidos"))
