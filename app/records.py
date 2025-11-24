"""
records.py
----------
Todas as operações de cadastro e manipulação dos registros.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .extensions import get_conn
from .utils import normalize_cpf

records_bp = Blueprint("records", __name__)


# =============================================================================
# NOVO CADASTRO (FORMULÁRIO)
# =============================================================================
@records_bp.route("/")
def index():
    return render_template("index.html")


# =============================================================================
# SUBMIT DO FORMULÁRIO
# =============================================================================
@records_bp.route("/submit", methods=["POST"])
def submit():

    nome = request.form.get("nome")
    cpf = normalize_cpf(request.form.get("cpf"))
    escritorio_dono = request.form.get("escritorio_dono")
    tipo_acao = request.form.get("tipo_acao")
    data_fechamento = request.form.get("data_fechamento")

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO registros (nome, cpf, escritorio_dono, tipo_acao, data_fechamento)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, cpf, escritorio_dono, tipo_acao, data_fechamento))

    conn.commit()
    conn.close()

    return render_template("submit.html")


# =============================================================================
# TABELA DE REGISTROS
# =============================================================================
@records_bp.route("/table/<office>")
def table(office):

    conn = get_conn()
    c = conn.cursor()

    if office == "CENTRAL":
        c.execute("""
            SELECT id, nome, cpf, escritorio_dono, tipo_acao, data_fechamento
            FROM registros
            WHERE excluido=0
            ORDER BY id DESC
        """)
    else:
        c.execute("""
            SELECT id, nome, cpf, escritorio_dono, tipo_acao, data_fechamento
            FROM registros
            WHERE excluido=0 AND escritorio_dono=?
            ORDER BY id DESC
        """, (office,))

    rows = c.fetchall()
    conn.close()

    return render_template("table.html", rows=rows, office=office)


# =============================================================================
# EDITAR
# =============================================================================
@records_bp.route("/edit/<int:reg_id>", methods=["GET", "POST"])
def edit(reg_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT id, nome, cpf, escritorio_dono, tipo_acao, data_fechamento
        FROM registros WHERE id=?
    """, (reg_id,))

    row = c.fetchone()

    if not row:
        conn.close()
        flash("Registro não encontrado.", "error")
        return redirect(url_for("records.index"))

    registro = {
        "id": row[0],
        "nome": row[1],
        "cpf": row[2],
        "escritorio_dono": row[3],
        "tipo_acao": row[4],
        "data_fechamento": row[5]
    }

    if request.method == "POST":

        nome = request.form.get("nome")
        cpf = normalize_cpf(request.form.get("cpf"))
        tipo_acao = request.form.get("tipo_acao")
        data_fechamento = request.form.get("data_fechamento")

        c.execute("""
            UPDATE registros SET
                nome=?, cpf=?, tipo_acao=?, data_fechamento=?
            WHERE id=?
        """, (nome, cpf, tipo_acao, data_fechamento, reg_id))

        conn.commit()
        conn.close()

        flash("Registro atualizado!", "success")
        return redirect(url_for("records.table", office="CENTRAL"))

    conn.close()
    return render_template("edit.html", r=registro)


# =============================================================================
# EXCLUSÃO LÓGICA
# =============================================================================
@records_bp.route("/delete", methods=["POST"])
def delete():

    reg_id = request.form.get("id")

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        UPDATE registros
        SET excluido=1, data_exclusao=datetime('now','localtime')
        WHERE id=?
    """, (reg_id,))

    conn.commit()
    conn.close()

    flash("Registro movido para excluídos.", "success")
    return redirect(url_for("records.index"))


# =============================================================================
# TELA DE EXCLUÍDOS
# =============================================================================
@records_bp.route("/excluidos")
def excluidos():

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT id, nome, cpf, escritorio_dono, tipo_acao,
               data_fechamento, data_exclusao
        FROM registros
        WHERE excluido=1
        ORDER BY data_exclusao DESC
    """)

    rows = c.fetchall()
    conn.close()

    return render_template("excluidos.html", rows=rows)


# =============================================================================
# RESTAURAR
# =============================================================================
@records_bp.route("/restore", methods=["POST"])
def restore():

    reg_id = request.form.get("id")

    conn = get_conn()
    c = conn.cursor()

    c.execute("UPDATE registros SET excluido=0 WHERE id=?", (reg_id,))
    conn.commit()
    conn.close()

    flash("Registro restaurado!", "success")
    return redirect(url_for("records.excluidos"))


# =============================================================================
# EXCLUIR PERMANENTE
# =============================================================================
@records_bp.route("/delete_forever", methods=["POST"])
def delete_forever():

    reg_id = request.form.get("id")

    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM registros WHERE id=?", (reg_id,))
    conn.commit()
    conn.close()

    flash("Registro removido definitivamente.", "success")

    return redirect(url_for("records.excluidos"))
