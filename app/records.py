"""
records.py
----------
Este módulo contém todas as rotas e funcionalidades ligadas aos REGISTROS:

 - Listagem com filtro + paginação
 - Edição de registros
 - Atualização no banco
 - Exclusão (soft delete → tabela excluidos)
 - Restauração
 - Migração entre escritórios
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, send_file
)
from datetime import datetime
import io
import csv

from .extensions import get_conn
from .utils import (
    normalize_office_key,
    register_office,
    list_offices,
    get_office_display
)

# -----------------------------------------------------------------------------
# Blueprint dos registros
# -----------------------------------------------------------------------------
records_bp = Blueprint("records", __name__, url_prefix="/records")


# =============================================================================
# LISTAGEM DE REGISTROS (com filtro + paginação)
# =============================================================================
@records_bp.route("/table")
def table():
    """
    Lista registros com filtros poderosos e paginação.

    Parâmetros suportados:
     - office=CENTRAL / ALL / outro escritório
     - filtro=id/nome/cpf
     - valor=texto do filtro
     - data_tipo=data_fechamento / data_protocolo
     - data_de=YYYY-MM-DD
     - data_ate=YYYY-MM-DD
     - page=1..N
     - per_page=10/20/50/100
    """

    # --- captura dos parâmetros ------------------------------------------------
    office_param = request.args.get("office", "CENTRAL").upper()
    page       = int(request.args.get("page", 1))
    per_page   = int(request.args.get("per_page", 10))
    filtro     = request.args.get("filtro")
    valor      = request.args.get("valor", "").strip()
    data_tipo  = request.args.get("data_tipo")
    data_de    = request.args.get("data_de")
    data_ate   = request.args.get("data_ate")

    # limite permitido
    if per_page not in (10, 20, 50, 100):
        per_page = 10

    offices = list_offices()

    # --- montagem dinâmica da query -------------------------------------------
    where = []
    params = []

    conn = get_conn()
    c = conn.cursor()

    # Caso ALL, listamos registros de todos escritórios
    if office_param == "ALL":
        pass
    else:
        office_key = normalize_office_key(office_param)
        where.append("escritorio_chave = ?")
        params.append(f"office_{office_key}")

    # Filtro textual
    if filtro and valor:
        if filtro == "nome":
            where.append("LOWER(nome) LIKE ?")
            params.append(f"%{valor.lower()}%")
        elif filtro == "cpf":
            where.append("cpf LIKE ?")
            params.append(f"%{valor}%")
        elif filtro == "id":
            try:
                params.append(int(valor))
                where.append("id = ?")
            except:
                where.append("1=0")  # força 0 resultados

    # Filtro por datas
    if data_tipo in ("data_fechamento", "data_protocolo"):
        if data_de and data_ate:
            where.append(f"{data_tipo} BETWEEN ? AND ?")
            params.extend([data_de, data_ate])
        elif data_de:
            where.append(f"{data_tipo} >= ?")
            params.append(data_de)
        elif data_ate:
            where.append(f"{data_tipo} <= ?")
            params.append(data_ate)

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    # Contagem total
    c.execute(f"SELECT COUNT(*) FROM registros {where_sql}", params)
    total = c.fetchone()[0]

    total_pages = max(1, (total + per_page - 1) // per_page)
    if page < 1: page = 1
    if page > total_pages: page = total_pages

    offset = (page - 1) * per_page

    # Query final
    c.execute(
        f"SELECT * FROM registros {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?",
        params + [per_page, offset]
    )
    rows = c.fetchall()
    conn.close()

    return render_template(
        "table.html",
        rows=rows,
        office=office_param,
        offices=offices,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        filtro=filtro,
        valor=valor,
        data_tipo=data_tipo,
        data_de=data_de,
        data_ate=data_ate
    )


# =============================================================================
# EDITAR REGISTRO
# =============================================================================
@records_bp.route("/edit")
def edit():
    """
    Abre o formulário de edição de um registro.
    """
    registro_id = request.args.get("id")
    office = request.args.get("office", "CENTRAL")

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM registros WHERE id=?", (registro_id,))
    row = c.fetchone()

    conn.close()

    if not row:
        flash("Registro não encontrado.", "error")
        return redirect(url_for("records.table", office=office))

    cliente = {
        "id": row[0], "nome": row[1], "cpf": row[2],
        "escritorio_chave": row[3], "escritorio_nome": row[4],
        "tipo_acao": row[5], "data_fechamento": row[6], "pendencias": row[7],
        "numero_processo": row[8], "data_protocolo": row[9],
        "observacoes": row[10], "captador": row[11],
        "created_at": row[12]
    }

    offices = list_offices()

    return render_template("edit.html", cliente=cliente, office=office, offices=offices)


# =============================================================================
# UPDATE (SALVAR ALTERAÇÕES)
# =============================================================================
@records_bp.route("/update", methods=["POST"])
def update():
    """
    Atualiza um registro já existente no banco.
    """

    registro_id = request.form.get("id")
    escritorio_input = request.form.get("escritorio", "").strip()

    conn = get_conn()
    c = conn.cursor()

    # Descobrir office_key baseado no display
    c.execute(
        "SELECT office_key FROM offices WHERE display_name = ?",
        (escritorio_input.upper(),)
    )
    found = c.fetchone()

    if found:
        office_key = found[0]
        display_name = get_office_display(office_key)
    else:
        office_key = normalize_office_key(escritorio_input)
        display_name = escritorio_input.upper()
        register_office(office_key, display_name)

    # Captura de dados
    nome             = request.form.get("nome")
    cpf              = request.form.get("cpf")
    tipo_acao        = request.form.get("tipo_acao")
    data_fechamento  = request.form.get("data_fechamento")
    pendencias       = request.form.get("pendencias")
    numero_processo  = request.form.get("numero_processo")
    data_protocolo   = request.form.get("data_protocolo")
    observacoes      = request.form.get("observacoes")
    captador         = request.form.get("captador")

    # Update
    c.execute("""
        UPDATE registros
        SET nome=?, cpf=?, escritorio_chave=?, escritorio_nome=?, tipo_acao=?,
            data_fechamento=?, pendencias=?, numero_processo=?, data_protocolo=?,
            observacoes=?, captador=?
        WHERE id=?
    """, (
        nome, cpf,
        f"office_{office_key}", display_name,
        tipo_acao, data_fechamento, pendencias,
        numero_processo, data_protocolo, observacoes, captador,
        registro_id
    ))

    conn.commit()
    conn.close()

    flash("Registro atualizado.", "success")
    return redirect(url_for("records.table", office=office_key))


# =============================================================================
# DELETE (SOFT DELETE → tabela EXCLUIDOS)
# =============================================================================
@records_bp.route("/delete", methods=["POST"])
def delete():
    """
    Move um registro para a tabela EXCLUIDOS (soft delete).
    """

    registro_id = request.form.get("id")
    office = request.form.get("office", "CENTRAL")

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM registros WHERE id=?", (registro_id,))
    row = c.fetchone()

    if row:
        c.execute("""
            INSERT INTO excluidos (
                nome, cpf, escritorio_origem, escritorio_origem_chave,
                tipo_acao, data_fechamento, pendencias, numero_processo,
                data_protocolo, observacoes, captador, created_at, data_exclusao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row[1], row[2], row[4], row[3],
            row[5], row[6], row[7], row[8],
            row[9], row[10], row[11], row[12],
            datetime.utcnow().isoformat()
        ))

        c.execute("DELETE FROM registros WHERE id=?", (registro_id,))
        conn.commit()

        flash("Registro movido para excluídos.", "success")

    conn.close()

    return redirect(url_for("records.table", office=office))


# =============================================================================
# MIGRAR REGISTRO ENTRE ESCRITÓRIOS
# =============================================================================
@records_bp.route("/migrate", methods=["POST"])
def migrate():
    """
    Move um único registro para outro escritório.
    """

    registro_id = request.form.get("id")
    office_target = request.form.get("office_target", "").strip()
    office_current = request.form.get("office_current", "CENTRAL")

    if not office_target:
        flash("Destino inválido.", "error")
        return redirect(url_for("records.table", office=office_current))

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM registros WHERE id=?", (registro_id,))
    row = c.fetchone()

    if not row:
        flash("Registro não encontrado.", "error")
        return redirect(url_for("records.table", office=office_current))

    target_key = normalize_office_key(office_target)
    target_display = office_target.upper()

    register_office(target_key, target_display)

    c.execute("""
        UPDATE registros
           SET escritorio_chave=?,
               escritorio_nome=?
         WHERE id=?
    """, (f"office_{target_key}", target_display, registro_id))

    conn.commit()
    conn.close()

    flash("Registro migrado com sucesso.", "success")

    return redirect(url_for("records.table", office=target_key))
