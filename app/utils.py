"""
utils.py
---------------------------
Funções auxiliares que não dependem de banco ou rotas específicas.

Inclui:
- Normalização de nomes de escritórios
- Criação automática de novos escritórios
- Funções reutilizáveis acessadas por várias rotas
"""

import re
from .extensions import get_conn


def normalize_office_key(name: str) -> str:
    """
    Converte um nome de escritório para um formato KEY padronizado.

    Exemplos:
        "São Paulo Centro" -> "SAO_PAULO_CENTRO"
        " unidade 1 " -> "UNIDADE_1"

    Args:
        name (str): Nome digitado pelo usuário.

    Returns:
        str: Chave padronizada em caixa alta sem símbolos.
    """
    if not name:
        return "CENTRAL"

    s = name.strip().upper()
    s = s.replace(" ", "_")
    s = re.sub(r"[^A-Z0-9_]", "", s)
    return s or "CENTRAL"


def register_office(key: str, display: str):
    """
    Registra um escritório no banco caso ainda não exista.

    Args:
        key  (str): office_key ("SAO_PAULO")
        display (str): Nome visível ("SÃO PAULO")
    """
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT OR IGNORE INTO offices (office_key, display_name)
        VALUES (?,?)
    """, (key, display))

    conn.commit()
    conn.close()


def list_offices():
    """
    Lista todos os escritórios cadastrados.

    Returns:
        list[dict]: Exemplo:
            [
                {"key": "CENTRAL", "display": "CENTRAL"},
                {"key": "SP", "display": "SÃO PAULO"}
            ]
    """
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT office_key, display_name FROM offices ORDER BY display_name")
    rows = c.fetchall()

    offices = [{"key": r["office_key"], "display": r["display_name"]} for r in rows]

    conn.close()
    return offices
