"""
Funções utilitárias gerais do sistema.
"""

from flask import flash

def success(msg):
    flash(msg, "success")

def error(msg):
    flash(msg, "error")
