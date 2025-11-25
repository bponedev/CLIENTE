"""
Gerencia registros excluídos.
"""

from .db import query

def list_deleted():
    return query("SELECT * FROM deleted")
