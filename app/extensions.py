"""
Extensões globais (ex.: DB connection pool).
"""

import sqlite3
from flask import g

DATABASE = "database.db"

def get_conn():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_extensions(app):
    @app.teardown_appcontext
    def close_connection(_):
        db = g.pop("db", None)
        if db:
            db.close()
