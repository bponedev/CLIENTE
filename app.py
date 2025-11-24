"""
Arquivo de compatibilidade.
Se o servidor tentar rodar "app:app", este arquivo garante
que a aplicação real (pacote /app) seja carregada corretamente.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
