"""
Funções de registros gerais.
"""

from .db import query, execute

def list_records():
    return query("SELECT * FROM records")
