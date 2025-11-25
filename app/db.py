"""
Criação das tabelas do sistema.
Executado automaticamente caso o banco não exista.
"""

from app.extensions import get_conn


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    # TABELA DE USUÁRIOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            full_name TEXT,
            password TEXT,
            role TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # TABELA DE ESCRITÓRIOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS offices (
            office_key TEXT PRIMARY KEY,
            display_name TEXT
        );
    """)

    # TABELA VINCULAR USER → OFFICES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_offices (
            user_id INTEGER,
            office_key TEXT
        );
    """)

    # TABELA DE REGISTROS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cpf TEXT,
            escritorio_dono TEXT,
            tipo_acao TEXT,
            data_fechamento TEXT,
            tags TEXT,
            ativo INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # TABELA DE REGISTROS EXCLUÍDOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS excluidos (
            id INTEGER,
            nome TEXT,
            cpf TEXT,
            escritorio_dono TEXT,
            tipo_acao TEXT,
            data_fechamento TEXT,
            data_exclusao TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # SEED: cria admin se não existir
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (username, full_name, password, role)
            VALUES ('admin', 'Administrador', 'admin', 'ADMIN')
        """)

    conn.commit()
