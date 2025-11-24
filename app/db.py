"""
Módulo responsável pela criação e manutenção das tabelas do banco.
Inclui:
- função de inicialização automática
- criação das tabelas necessárias
- inserts básicos (admin padrão)
"""

from flask import current_app
from .extensions import get_conn


# ======================================================================
#  SCRIPT DE CRIAÇÃO DO BANCO
# ======================================================================
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS offices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    office_key TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_offices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    office_key TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    cpf TEXT,
    escritorio_dono TEXT,
    data_fechamento TEXT,
    excluido INTEGER DEFAULT 0,
    data_exclusao TEXT DEFAULT NULL
);
"""


# ======================================================================
#  FUNÇÃO DE CRIAÇÃO
# ======================================================================
def init_database(app):
    """
    Criado quando a aplicação inicializa.
    - Executa o schema
    - Cria admin padrão caso não exista
    - Prepara escritórios básicos caso necessário
    """

    with app.app_context():
        conn = get_conn()
        cur = conn.cursor()

        # Criação de todas as tabelas
        cur.executescript(SCHEMA_SQL)

        # Verifica se existe administrador
        cur.execute("SELECT * FROM users WHERE username='admin'")
        admin = cur.fetchone()

        if not admin:
            cur.execute("""
                INSERT INTO users (username, password, full_name, role, active)
                VALUES ('admin', '123456', 'Administrador do Sistema', 'ADMIN', 1)
            """)

        conn.commit()
