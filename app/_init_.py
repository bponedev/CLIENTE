"""
Inicializa a aplicação Flask, registra blueprints
e configura extensões.
"""

from flask import Flask
from .extensions import init_extensions
from .routes.auth import auth_bp
from .routes.offices import offices_bp
from .routes.users import users_bp
from .routes.registros import registros_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "supersecretkey"

    init_extensions(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(offices_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(registros_bp)

    return app
