"""
Extensões do sistema (ex.: conexão com banco).
Responsável por fornecer get_conn() para todos os módulos.
"""

import sqlite3
from flask import g, current_app


def get_conn():
    """Retorna conexão SQLite ativa."""
    if "_db" not in g:
        g._db = sqlite3.connect("database.db", check_same_thread=False)
        g._db.row_factory = sqlite3.Row
    return g._db


def init_extensions(app):
    """Inicializa extensões na aplicação Flask."""
    @app.teardown_appcontext
    def close_conn(exception):
        db = g.pop("_db", None)
        if db:
            db.close()
