"""
Funções auxiliares de banco de dados.
Centraliza SELECTs, INSERTs e UPDATEs.
"""

from app.extensions import get_conn


def query(sql, params=(), one=False):
    conn = get_conn()
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql, params=()):
    conn = get_conn()
    cur = conn.execute(sql, params)
    conn.commit()
    return cur.lastrowid
