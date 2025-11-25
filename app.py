"""
APP PRINCIPAL – Versão simplificada e compatível com Render
Carrega a aplicação direto de /app, sem create_app()
"""

from flask import Flask
from app.extensions import init_extensions
from app.views import register_view_routes
from app.users import register_user_routes
from app.admin import register_admin_routes
from app.offices import register_office_routes
from app.records import register_record_routes
from app.deleted import register_deleted_routes
from app.auth import register_auth_routes

app = Flask(__name__)

# Inicializa DB, LoginManager etc.
init_extensions(app)

# Registra todos os blueprints
register_view_routes(app)
register_user_routes(app)
register_admin_routes(app)
register_office_routes(app)
register_record_routes(app)
register_deleted_routes(app)
register_auth_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
