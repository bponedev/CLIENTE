"""
WSGI entrypoint — usado pelo Gunicorn no Render.
Este arquivo importa a aplicação Flask real dentro do pacote /app.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
