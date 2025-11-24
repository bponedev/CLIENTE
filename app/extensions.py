"""
Extensões globais da aplicação.
Aqui ficam funções ou objetos que precisam ser utilizados em múltiplos módulos,
como conexões de banco ou controladores de autenticação.
"""

import sqlite3
from flask import g, current_app


# ======================================================================
#  FUNÇÃO DE CONEXÃO COM O BANCO
# ======================================================================
def get_conn():
    """
    Fornece uma conexão SQLite por requisição.
    - Abre a conexão somente quando necessário
    - Armazena em g (objeto de contexto do Flask)
    - Garante fechamento automático ao final
    """

    if "db_conn" not in g:
        g.db_conn = sqlite3.connect(
            current_app.config["DB_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db_conn.row_factory = sqlite3.Row  # retorna dict-like
    return g.db_conn


def close_conn(e=None):
    """
    Fecha a conexão ao final da requisição.
    O Flask chamará automaticamente via teardown_appcontext.
    """

    conn = g.pop("db_conn", None)
    if conn:
        conn.close()


# ======================================================================
#  INICIALIZAÇÃO
# ======================================================================
def init_extensions(app):
    """
    Registra funções automáticas no ciclo da app:
    - abertura/fechamento de conexão
    - outras extensões no futuro
    """

    app.teardown_appcontext(close_conn)
