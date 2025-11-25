"""
Funções de escritório (nível de serviço).
"""

from .db import query, execute

def list_offices():
    return query("SELECT * FROM offices")

def get_office(id):
    return query("SELECT * FROM offices WHERE id=?", (id,))
