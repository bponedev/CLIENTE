"""
offices.py
----------
Rotas e lógica de gerenciamento de escritórios.

Funções incluídas:
 - Listar escritórios
 - Criar novo escritório
 - Editar escritório existente
 - Excluir escritório (restrito ao ADMIN)

Observações:
 - A tabela 'offices' padroniza todos os escritórios usados no sistema
 - O sistema sempre garante que a chave 'CENTRAL' existe
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .extensions import get_conn
from .utils import normalize_office_key, list_offices, register_office

# -----------------------------------------------------------------------------
# Blueprint dos ESCRITÓRIOS
# -----------------------------------------------------------------------------
offices_bp = Blueprint("offices", __name__, url_prefix="/offices")


# =============================================================================
# PÁGINA PRINCIPAL DE ESCRITÓRIOS
# =============================================================================
@offices_bp.route("/")
def offices_page():
    """
    Exibe todos os escritórios cadastrados.
    """

    offices = list_offices()

    return render_template("offices.html", offices=offices)


# =============================================================================
# CRIAR NOVO ESCRITÓRIO
# =============================================================================
@offices_bp.route("/create", methods=["POST"])
def offices_create():
    """
    Cria um escritório novo.
    """

    office_name = request.form.get("office_name", "").strip()

    if office_name == "":
        flash("Informe um nome para o escritório.", "error")
        return redirect(url_for("offices.offices_page"))

    # Normaliza a chave
    office_key = normalize_office_key(office_name)

    # Registra na tabela (função idempotente)
    register_office(office_key, office_name)

    flash(f"Escritório '{office_name}' criado com sucesso!", "success")
    return redirect(url_for("offices.offices_page"))


# =============================================================================
# EDITAR ESCRITÓRIO
# =============================================================================
@offices_bp.route("/edit/<office_key>", methods=["GET", "POST"])
def office_edit(office_key):
    """
    Edita um escritório existente.
    """

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT office_key, display_name FROM offices WHERE office_key=?", (office_key,))
    row = c.fetchone()

    if not row:
        conn.close()
        flash("Escritório não encontrado.", "error")
        return redirect(url_for("offices.offices_page"))

    office = {
        "office_key": row[0],
        "display_name": row[1]
    }

    # SE FOR POST, SALVAR ALTERAÇÕES
    if request.method == "POST":
        new_display = request.form.get("display_name", "").strip()

        if new_display == "":
            flash("O nome do escritório não pode ser vazio.", "error")
            return redirect(url_for("offices.office_edit", office_key=office_key))

        # Atualiza somente o display_name (a chave nunca muda)
        c.execute("""
            UPDATE offices
            SET display_name=?
            WHERE office_key=?
        """, (new_display, office_key))

        conn.commit()
        conn.close()

        flash("Escritório atualizado com sucesso!", "success")
        return redirect(url_for("offices.offices_page"))

    conn.close()
    return render_template("office_edit.html", office=office)


# =============================================================================
# EXCLUIR ESCRITÓRIO
# =============================================================================
@offices_bp.route("/delete", methods=["POST"])
def offices_delete():
    """
    Exclui definitivamente um escritório da tabela.

    Regras:
      - O escritório CENTRAL não pode ser apagado.
      - Apenas ADMIN deve ter acesso (validação via template/menu).
    """

    office_key = request.form.get("office_key")

    if office_key == "CENTRAL":
        flash("O escritório CENTRAL não pode ser removido.", "error")
        return redirect(url_for("offices.offices_page"))

    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM offices WHERE office_key=?", (office_key,))
    conn.commit()
    conn.close()

    flash("Escritório removido com sucesso!", "success")
    return redirect(url_for("offices.offices_page"))
