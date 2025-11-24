"""
db_helpers.py
--------------------------------
Módulo dedicado a operações diretas no banco de dados.

Inclui:
- Criação das tabelas
- Verificação de existência
- Inserções base
- Inicialização do sistema
"""

from datetime import datetime
from werkzeug.security import generate_password_hash

from .extensions import get_conn


def init_db():
    """
    Cria todas as tabelas necessárias caso não existam.
    Popula o banco com:
        - ADMIN padrão
        - Escritório CENTRAL
    """
    conn = get_conn()
    c = conn.cursor()

    # ------------------------ TABELAS ------------------------

    # Registros principais
    c.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cpf TEXT,
            escritorio_chave TEXT,
            escritorio_nome TEXT,
            tipo_acao TEXT,
            data_fechamento TEXT,
            pendencias TEXT,
            numero_processo TEXT,
            data_protocolo TEXT,
            observacoes TEXT,
            captador TEXT,
            created_at TEXT
        )
    """)

    # Registros excluídos (lixeira)
    c.execute("""
        CREATE TABLE IF NOT EXISTS excluidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cpf TEXT,
            escritorio_origem TEXT,
            escritorio_origem_chave TEXT,
            tipo_acao TEXT,
            data_fechamento TEXT,
            pendencias TEXT,
            numero_processo TEXT,
            data_protocolo TEXT,
            observacoes TEXT,
            captador TEXT,
            created_at TEXT,
            data_exclusao TEXT
        )
    """)

    # Tabela de escritórios
    c.execute("""
        CREATE TABLE IF NOT EXISTS offices (
            office_key TEXT PRIMARY KEY,
            display_name TEXT
        )
    """)

    # Usuários
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            full_name TEXT,
            password_hash TEXT,
            role TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT
        )
    """)

    # Escritórios atribuídos a um usuário
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_offices (
            user_id INTEGER,
            office_key TEXT,
            PRIMARY KEY (user_id, office_key)
        )
    """)

    conn.commit()

    # ------------------------ DADOS BASE ------------------------

    # Garantir escritório CENTRAL
    c.execute(
        "INSERT OR IGNORE INTO offices (office_key, display_name) VALUES (?, ?)",
        ("CENTRAL", "CENTRAL")
    )

    # Criar admin se banco estiver vazio
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        now = datetime.utcnow().isoformat()
        pw = generate_password_hash("admin")
        c.execute("""
            INSERT INTO users (username, full_name, password_hash, role, active, created_at)
            VALUES (?,?,?,?,?,?)
        """, ("admin", "Administrador Padrão", pw, "ADMIN", 1, now))

    conn.commit()
    conn.close()
