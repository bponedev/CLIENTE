"""
Funções gerais de acesso ao banco.
"""

from .extensions import get_conn

def query(sql, params=()):
    conn = get_conn()
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    return rows

def execute(sql, params=()):
    conn = get_conn()
    conn.execute(sql, params)
    conn.commit()
