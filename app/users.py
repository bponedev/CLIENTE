"""
Funções do módulo de usuários.
"""

from .db import query, execute

def list_users():
    return query("SELECT * FROM users")

def get_user(id):
    return query("SELECT * FROM users WHERE id=?", (id,))
