"""
Funções gerais de acesso ao banco.
"""

import sqlite3
from flask import g, current_app


# ============================================================
# Conexão com o banco
# ============================================================

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DB_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ============================================================
# Funções utilitárias (usadas pelas rotas)
# ============================================================

def query(sql, params=(), one=False):
    db = get_db()
    cur = db.execute(sql, params)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute(sql, params=()):
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    cur.close()
    return True


# ============================================================
# Inicializar banco e tabelas
# ============================================================

def init_database(app):
    """Cria o banco de dados e suas tabelas se não existirem."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS offices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            descricao TEXT,
            data TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)

        db.commit()

    app.teardown_appcontext(close_db)
