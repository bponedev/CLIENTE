"""
Views auxiliares do sistema.
"""

from flask import render_template

def home():
    return render_template("index.html")
