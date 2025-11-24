"""
views.py  
---------
Rotas gerais da aplicação:
 - Tela inicial (index)
 - Formulário de criação de registros
 - Submissão de novos registros

Arquitetura limpa, organizada e totalmente comentada para fácil manutenção.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

from .extensions import get_conn
from .utils import normalize_office_key, register_office, list_offices

# -----------------------------------------------------------------------------
# Blueprint de rotas principais
# -----------------------------------------------------------------------------
views_bp = Blueprint("views", __name__)


# =============================================================================
# ROTA: PÁGINA INICIAL
# =============================================================================
@views_bp.route("/")
def index():
    """
    Renderiza a página inicial com o formulário de criação de registros.
    Exibe também a lista de escritórios disponíveis.
    """
    offices = list_offices()
    return render_template("index.html", offices=offices)


# =============================================================================
# ROTA: SUBMIT (SALVAR REGISTRO)
# =============================================================================
@views_bp.route("/submit", methods=["POST"])
def submit():
    """
    Recebe os dados enviados pelo formulário inicial e salva no banco.
    Esta rota foi cuidadosamente estruturada para lidar com:
    - nomes de escritórios dinâmicos
    - criação automática de escritórios não existentes
    - normalização dos dados
    """

    try:
        # ------------------------------
        # 1) Coleta dos dados
        # ------------------------------
        nome = request.form.get("nome", "").strip()
        cpf = request.form.get("cpf", "").strip()
        escritorio_input = request.form.get("escritorio", "").strip() or "CENTRAL"

        tipo_acao = request.form.get("tipo_acao", "")
        data_fechamento = request.form.get("data_fechamento", "")
        pendencias = request.form.get("pendencias", "")
        numero_processo = request.form.get("numero_processo", "")
        data_protocolo = request.form.get("data_protocolo", "")
        observacoes = request.form.get("observacoes", "")
        captador = request.form.get("captador", "NÃO PAGO")

        now = datetime.utcnow().isoformat()

        # ------------------------------
        # 2) Mapeamento do escritório
        #    → Se digitado manualmente, normalizamos
        # ------------------------------
        offices = list_offices()
        office_key = None
        display_name = None

        # Caso usuário selecione um escritório existente
        for office in offices:
            if office["display"] == escritorio_input:
                office_key = office["key"]
                display_name = office["display"]
                break

        # Caso contrário, cria automaticamente
        if not office_key:
            office_key = normalize_office_key(escritorio_input)
            display_name = escritorio_input.upper()
            register_office(office_key, display_name)

        # ------------------------------
        # 3) Inserção no banco
        # ------------------------------
        conn = get_conn()
        c = conn.cursor()

        c.execute("""
            INSERT INTO registros (
                nome, cpf, escritorio_chave, escritorio_nome,
                tipo_acao, data_fechamento, pendencias, numero_processo,
                data_protocolo, observacoes, captador, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nome, cpf, f"office_{office_key}", display_name,
            tipo_acao, data_fechamento, pendencias, numero_processo,
            data_protocolo, observacoes, captador, now
        ))

        conn.commit()
        conn.close()

        flash("Registro salvo com sucesso.", "success")

        return redirect(url_for("records.table", office=office_key))

    except Exception as e:
        flash(f"Erro ao salvar registro: {str(e)}", "error")
        return redirect(url_for("views.index"))


# =============================================================================
# ROTA: PÁGINA DE TESTE / STATUS
# =============================================================================
@views_bp.route("/status")
def status():
    """
    Rota utilitária simples para verificar se o servidor está online.
    (Útil para integração com Render, UptimeRobot, etc.)
    """
    return {"status": "ok", "message": "API funcionando normalmente."}
