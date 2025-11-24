"""
auth.py
-----------------------------------------------------
Módulo responsável por TUDO relacionado à autenticação:

- Login e Logout
- Sessão de usuário (session["user_id"])
- Decoradores: login_required, require_roles
- Funções utilitárias para buscar usuários no banco
- Expor `current_user` automaticamente aos templates

Este arquivo é carregado no create_app().
"""

from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session
)
from werkzeug.security import check_password_hash

from .extensions import get_conn


# =====================================================
# BLUEPRINT DE AUTENTICAÇÃO
# =====================================================

auth_bp = Blueprint("auth", __name__)


# =====================================================
# FUNÇÕES DE ACESSO AO BANCO (USUÁRIOS)
# =====================================================

def get_user_by_username(username):
    """
    Retorna um dicionário com os dados do usuário.

    Args:
        username (str): Nome de usuário

    Returns:
        dict | None
    """
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT id, username, full_name, password_hash, role, active
        FROM users
        WHERE username = ?
    """, (username,))
    row = c.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "username": row["username"],
        "full_name": row["full_name"],
        "password_hash": row["password_hash"],
        "role": row["role"],
        "active": row["active"],
    }


def get_user_by_id(uid):
    """
    Busca usuário pelo ID.

    Args:
        uid (int): ID do usuário

    Returns:
        dict | None
    """
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT id, username, full_name, role, active
        FROM users
        WHERE id = ?
    """, (uid,))
    row = c.fetchone()

    conn.close()
    if not row:
        return None

    return {
        "id": row["id"],
        "username": row["username"],
        "full_name": row["full_name"],
        "role": row["role"],
        "active": row["active"],
    }


def get_user_offices(user_id):
    """
    Retorna os escritórios que o usuário tem permissão de acessar.

    Returns:
        list[str]: lista de office_keys
    """
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT office_key FROM user_offices WHERE user_id=?", (user_id,))
    rows = c.fetchall()

    conn.close()
    return [r["office_key"] for r in rows]


# =====================================================
# DECORADORES DE PERMISSÃO (MIDDLEWARE)
# =====================================================

def login_required(f):
    """
    Decorador que exige login.

    Se não estiver logado → redireciona para /login.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login", next=request.path))

        user = get_user_by_id(session["user_id"])

        # Se usuário apagado ou inativo → resetar sessão
        if not user or user["active"] != 1:
            session.pop("user_id", None)
            flash("Sessão inválida. Faça login novamente.", "error")
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return wrapper


def require_roles(*roles):
    """
    Decorador que exige que o usuário tenha um dos papéis permitidos:

    Exemplo:
        @require_roles("ADMIN", "SUPERVISOR")

    ADMIN sempre tem permissão total.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:
                return redirect(url_for("auth.login"))

            user = get_user_by_id(session["user_id"])
            if not user:
                session.pop("user_id", None)
                return redirect(url_for("auth.login"))

            # ADMIN tem acesso a tudo
            if user["role"] == "ADMIN":
                return f(*args, **kwargs)

            # Se papel não está permitido
            if user["role"] not in roles:
                flash("Permissão negada.", "error")
                return redirect(url_for("main.index"))

            return f(*args, **kwargs)

        return wrapper

    return decorator


# =====================================================
# INJETAR current_user EM TODAS AS TELAS (TEMPLATES)
# =====================================================

@auth_bp.app_context_processor
def inject_current_user():
    """
    Esta função roda automaticamente em TODAS as renderizações de template.

    Ela injeta a variável `current_user`, que pode ser usada em qualquer HTML:

        {{ current_user }}
        {{ current_user.role }}

    Isso permite checar permissões diretamente no template.
    """
    user = None

    if "user_id" in session:
        user = get_user_by_id(session["user_id"])

    return {"current_user": user}


# =====================================================
# ROTAS DE AUTENTICAÇÃO
# =====================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Página de login.

    - Se GET → mostra o formulário
    - Se POST → valida usuário/senha
    """
    next_page = request.args.get("next") or url_for("main.index")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)

        if not user:
            flash("Usuário não encontrado.", "error")
            return render_template("login.html")

        if user["active"] != 1:
            flash("Usuário inativo.", "error")
            return render_template("login.html")

        if not check_password_hash(user["password_hash"], password):
            flash("Senha incorreta.", "error")
            return render_template("login.html")

        # Login OK → iniciar sessão
        session["user_id"] = user["id"]
        flash("Login efetuado com sucesso.", "success")
        return redirect(next_page)

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Finaliza sessão do usuário."""
    session.pop("user_id", None)
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))
