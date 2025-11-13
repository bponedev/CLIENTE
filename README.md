# Client Registry (Simple Flask)

Estrutura mínima para testar localmente / publicar.

## Como rodar (local)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
```
## Funcionalidades
- Formulário de cadastro (página inicial)
- Tabelas por escritório (cada escritório vira uma tabela `office_<nome>`)
- Exportar CSV por escritório
- Exportar PDF por escritório ou todas as tabelas em um único PDF
