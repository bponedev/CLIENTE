"""
Módulo principal do pacote Flask.
Responsável por:
- criar a aplicação (Factory Pattern)
- registrar extensões
- registrar rotas
- inicializar banco
- configurar sessão e segurança
"""

from flask import Flask
from .extensions import init_extensions
from .db import init_database

# Importação das blueprints (rotas)
from .routes.auth import auth_bp
from .routes.users import users_bp
from .routes.offices import offices_bp
from .routes.registros import registros_bp


def create_app():
    """
    Função fábrica da aplicação.
    É chamada pelo wsgi.py e também pelo gunicorn.
    Torna o projeto modular, organizado e compatível com servidores de produção.
    """

    app = Flask(__name__)

    # Configurações essenciais
    app.config["SECRET_KEY"] = "SUA_SECRET_KEY_SUPER_SECRETA_AQUI"
    app.config["DB_PATH"] = "database.db"

    # Inicialização das Extensões
    init_extensions(app)

    # Inicialização do Banco de Dados
    init_database(app)

    # Registro de Blueprints (Rotas)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(offices_bp)
    app.register_blueprint(registros_bp)

    return app
