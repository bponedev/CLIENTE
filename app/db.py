"""
Funções gerais de acesso ao banco.
"""

import sqlite3
from flask import g, current_app

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


def init_database(app):
    """Cria o banco de dados e tabelas se não existirem."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Exemplo de criação de tabela, adicione as suas aqui
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
