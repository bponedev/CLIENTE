"""
Inicialização do pacote Flask 'app'.
Responsável por criar a aplicação, registrar extensões e blueprints.
"""

from flask import Flask
from app.extensions import init_extensions
from app.routes.auth import auth_bp
from app.routes.registros import registros_bp
from app.routes.offices import offices_bp
from app.routes.users import users_bp


def create_app():
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.secret_key = "SECRET_KEY_AQUI"

    # Inicia SQLite, configs e conexões
    init_extensions(app)

    # Registra blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(registros_bp)
    app.register_blueprint(offices_bp)
    app.register_blueprint(users_bp)

    return app
