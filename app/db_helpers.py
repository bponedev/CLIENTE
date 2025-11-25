"""
Funções auxiliares de CRUD.
"""

from .db import query, execute

def fetch_one(sql, params=()):
    rows = query(sql, params)
    return rows[0] if rows else None
