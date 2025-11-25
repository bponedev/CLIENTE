"""
Inicializa a aplicação Flask, registra blueprints
e configura extensões.
"""

"""
Módulo principal do pacote Flask.
"""

from flask import Flask
from .extensions import init_extensions
from .db import init_database

from .routes.auth import auth_bp
from .routes.users import users_bp
from .routes.offices import offices_bp
from .routes.registros import registros_bp

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "SUA_SECRET_KEY_SUPER_SECRETA_AQUI"
    app.config["DB_PATH"] = "database.db"

    init_extensions(app)
    init_database(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(offices_bp)
    app.register_blueprint(registros_bp)

    return app
