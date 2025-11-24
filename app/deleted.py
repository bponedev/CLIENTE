"""
deleted.py
----------
Rotas relacionadas à tabela EXCLUIDOS:

 - Listagem de excluídos
 - Restauração individual
 - Restauração em lote
 - Exclusão permanente
 - Exclusão permanente em lote
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

from .extensions import get_conn
from .utils import (
    normalize_office_key,
    register_office,
    list_offices,
    get_office_display
)


# -----------------------------------------------------------------------------
# Blueprint dos EXCLUÍDOS
# -----------------------------------------------------------------------------
deleted_bp = Blueprint("deleted", __name__, url_prefix="/deleted")


# =============================================================================
# LISTAGEM DOS EXCLUÍDOS
# =============================================================================
@deleted_bp.route("/")
def excluidos():
    """
    Lista todos os registros que foram movidos para a tabela 'excluidos'.
    """

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM excluidos ORDER BY id DESC")
    rows = c.fetchall()

    conn.close()

    offices = list_offices()

    return render_template("excluidos.html", rows=rows, offices=offices)


# =============================================================================
# RESTAURAR UM REGISTRO
# =============================================================================
@deleted_bp.route("/restore", methods=["POST"])
def restore():
    """
    Restaura um registro individual, movendo-o de volta para 'registros'.
    """

    registro_id = request.form.get("id")

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM excluidos WHERE id=?", (registro_id,))
    row = c.fetchone()

    if row:
        origem_display = row[3]  # escritório_nome original
        origem_chave = row[4]    # office_<KEY>

        # recuperar key real
        if origem_chave.startswith("office_"):
            office_key = origem_chave.replace("office_", "").upper()
        else:
            office_key = normalize_office_key(origem_display)

        register_office(office_key, origem_display)

        c.execute("""
            INSERT INTO registros (
                nome, cpf, escritorio_chave, escritorio_nome,
                tipo_acao, data_fechamento, pendencias,
                numero_processo, data_protocolo,
                observacoes, captador, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row[1], row[2],
            f"office_{office_key}", origem_display,
            row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12]
        ))

        # remover da tabela excluídos
        c.execute("DELETE FROM excluidos WHERE id=?", (registro_id,))
        conn.commit()

        flash("Registro restaurado.", "success")

    conn.close()

    return redirect(url_for("deleted.excluidos"))


# =============================================================================
# RESTAURAR SELECIONADOS
# =============================================================================
@deleted_bp.route("/restore_selected", methods=["POST"])
def restore_selected():
    """
    Restaura múltiplos registros selecionados.
    """

    ids = request.form.getlist("ids")

    conn = get_conn()
    c = conn.cursor()

    for registro_id in ids:
        c.execute("SELECT * FROM excluidos WHERE id=?", (registro_id,))
        row = c.fetchone()

        if not row:
            continue

        origem_display = row[3]
        origem_chave = row[4]

        if origem_chave.startswith("office_"):
            office_key = origem_chave.replace("office_", "")
        else:
            office_key = normalize_office_key(origem_display)

        register_office(office_key, origem_display)

        c.execute("""
            INSERT INTO registros (
                nome, cpf, escritorio_chave, escritorio_nome,
                tipo_acao, data_fechamento, pendencias,
                numero_processo, data_protocolo,
                observacoes, captador, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row[1], row[2],
            f"office_{office_key}", origem_display,
            row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12]
        ))

        c.execute("DELETE FROM excluidos WHERE id=?", (registro_id,))

    conn.commit()
    conn.close()

    flash("Registros restaurados com sucesso.", "success")

    return redirect(url_for("deleted.excluidos"))


# =============================================================================
# EXCLUSÃO PERMANENTE
# =============================================================================
@deleted_bp.route("/delete_forever", methods=["POST"])
def delete_forever():
    """
    Remove permanentemente um único registro.
    """

    registro_id = request.form.get("id")

    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM excluidos WHERE id=?", (registro_id,))
    conn.commit()
    conn.close()

    flash("Registro excluído permanentemente.", "success")

    return redirect(url_for("deleted.excluidos"))


# =============================================================================
# EXCLUSÃO PERMANENTE EM LOTE
# =============================================================================
@deleted_bp.route("/delete_forever_selected", methods=["POST"])
def delete_forever_selected():
    """
    Remove permanentemente múltiplos registros.
    """

    ids = request.form.getlist("ids")

    conn = get_conn()
    c = conn.cursor()

    for rid in ids:
        c.execute("DELETE FROM excluidos WHERE id=?", (rid,))

    conn.commit()
    conn.close()

    flash("Registros excluídos permanentemente.", "success")

    return redirect(url_for("deleted.excluidos"))
