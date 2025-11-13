from flask import Flask, request, send_file, redirect, url_for
import sqlite3, csv, io, os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__, static_folder='.', static_url_path='/static')


DB_FILE = 'database.db'


# ----------------------------------------
# 🔧 Inicialização do banco
# ----------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS office_Central (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, cpf TEXT, escritorio TEXT, tipo_acao TEXT,
            data_fechamento TEXT, pendencias TEXT, numero_processo TEXT,
            data_protocolo TEXT, observacoes TEXT, captador TEXT, created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS excluidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, cpf TEXT, escritorio TEXT, tipo_acao TEXT,
            data_fechamento TEXT, pendencias TEXT, numero_processo TEXT,
            data_protocolo TEXT, observacoes TEXT, captador TEXT,
            created_at TEXT, data_exclusao TEXT
        )
    """)
    conn.commit()
    conn.close()


# ----------------------------------------
# 🏠 Rotas principais
# ----------------------------------------
@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/table.html')
def table():
    return app.send_static_file('table.html')

@app.route('/excluidos.html')
def excluidos():
    return app.send_static_file('excluidos.html')



# ----------------------------------------
# 💾 Cadastro de novo cliente
# ----------------------------------------
@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    office = data.get('escritorio', 'Central')
    table_name = f"office_{office.replace(' ', '_')}"

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, cpf TEXT, escritorio TEXT, tipo_acao TEXT,
            data_fechamento TEXT, pendencias TEXT, numero_processo TEXT,
            data_protocolo TEXT, observacoes TEXT, captador TEXT, created_at TEXT
        )
    """)

    c.execute(f"""
        INSERT INTO {table_name}
        (nome, cpf, escritorio, tipo_acao, data_fechamento, pendencias,
        numero_processo, data_protocolo, observacoes, captador, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data['nome'], data['cpf'], office,
        data.get('tipo_acao'), data.get('data_fechamento'),
        data.get('pendencias'), data.get('numero_processo'),
        data.get('data_protocolo'), data.get('observacoes'),
        data.get('captador'), datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()
    return redirect(url_for('table'))


# ----------------------------------------
# 🗑️ Exclusões (único e múltiplos)
# ----------------------------------------
def move_to_excluidos(row):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO excluidos
        (nome, cpf, escritorio, tipo_acao, data_fechamento, pendencias,
        numero_processo, data_protocolo, observacoes, captador,
        created_at, data_exclusao)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (*row[1:], datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


@app.route('/delete', methods=['POST'])
def delete_client():
    office = request.form.get('office', 'Central')
    client_id = request.form.get('id')
    table_name = f"office_{office.replace(' ', '_')}"

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name} WHERE id=?", (client_id,))
    row = c.fetchone()
    if row:
        move_to_excluidos(row)
        c.execute(f"DELETE FROM {table_name} WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('table'))


@app.route('/delete_selected', methods=['POST'])
def delete_selected():
    ids = request.form.getlist('ids')
    office = request.form.get('office', 'Central')
    table_name = f"office_{office.replace(' ', '_')}"

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for client_id in ids:
        c.execute(f"SELECT * FROM {table_name} WHERE id=?", (client_id,))
        row = c.fetchone()
        if row:
            move_to_excluidos(row)
            c.execute(f"DELETE FROM {table_name} WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('table'))


# ----------------------------------------
# ♻️ Restaurações
# ----------------------------------------
@app.route('/restore', methods=['POST'])
def restore_client():
    client_id = request.form.get('id')

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM excluidos WHERE id=?", (client_id,))
    row = c.fetchone()
    if row:
        office = row[3] or 'Central'
        table_name = f"office_{office.replace(' ', '_')}"
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT, cpf TEXT, escritorio TEXT, tipo_acao TEXT,
                data_fechamento TEXT, pendencias TEXT, numero_processo TEXT,
                data_protocolo TEXT, observacoes TEXT, captador TEXT, created_at TEXT
            )
        """)
        c.execute(f"""
            INSERT INTO {table_name}
            (nome, cpf, escritorio, tipo_acao, data_fechamento, pendencias,
            numero_processo, data_protocolo, observacoes, captador, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, row[1:12])
        c.execute("DELETE FROM excluidos WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('excluidos'))


@app.route('/restore_selected', methods=['POST'])
def restore_selected():
    ids = request.form.getlist('ids')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for client_id in ids:
        c.execute("SELECT * FROM excluidos WHERE id=?", (client_id,))
        row = c.fetchone()
        if row:
            office = row[3] or 'Central'
            table_name = f"office_{office.replace(' ', '_')}"
            c.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT, cpf TEXT, escritorio TEXT, tipo_acao TEXT,
                    data_fechamento TEXT, pendencias TEXT, numero_processo TEXT,
                    data_protocolo TEXT, observacoes TEXT, captador TEXT, created_at TEXT
                )
            """)
            c.execute(f"""
                INSERT INTO {table_name}
                (nome, cpf, escritorio, tipo_acao, data_fechamento, pendencias,
                numero_processo, data_protocolo, observacoes, captador, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, row[1:12])
            c.execute("DELETE FROM excluidos WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('excluidos'))


# ----------------------------------------
# 📤 Exportações CSV e PDF
# ----------------------------------------
@app.route('/export/csv')
def export_csv():
    office = request.args.get('office', 'Central')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if office.lower() == 'all':
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    else:
        tables = [f"office_{office.replace(' ', '_')}"] if office != 'excluidos' else ['excluidos']

    output = io.StringIO()
    writer = csv.writer(output)

    for t in tables:
        writer.writerow([f"Tabela: {t}"])
        try:
            for row in c.execute(f"SELECT * FROM {t}"):
                writer.writerow(row)
        except Exception:
            writer.writerow(['<tabela vazia ou inexistente>'])
        writer.writerow([])

    conn.close()
    mem = io.BytesIO(output.getvalue().encode('utf-8'))
    return send_file(mem, as_attachment=True, download_name=f"{office}_export.csv", mimetype='text/csv')


@app.route('/export/pdf')
def export_pdf():
    office = request.args.get('office', 'Central')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if office.lower() == 'all':
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    else:
        tables = [f"office_{office.replace(' ', '_')}"] if office != 'excluidos' else ['excluidos']

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 80

    logo_path = os.path.join('logo', 'logo.png')
    if os.path.exists(logo_path):
        try:
            p.drawImage(logo_path, 40, y - 20, width=60, preserveAspectRatio=True)
        except Exception:
            pass

    p.setFont("Helvetica-Bold", 14)
    p.drawString(120, y, "Sistema de Registro de Clientes")
    p.setFont("Helvetica", 10)
    p.drawString(120, y - 16, f"Geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 40

    for t in tables:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(40, y, f"Tabela: {t}")
        y -= 16
        try:
            for row in c.execute(f"SELECT nome, cpf, escritorio, tipo_acao, data_fechamento FROM {t}"):
                if y < 80:
                    p.showPage()
                    y = height - 80
                p.setFont("Helvetica", 9)
                p.drawString(50, y, " | ".join(str(r) for r in row))
                y -= 12
        except Exception:
            p.setFont("Helvetica", 9)
            p.drawString(50, y, "(tabela vazia ou inexistente)")
            y -= 12
        y -= 16

    p.showPage()
    p.save()
    conn.close()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{office}_export.pdf", mimetype='application/pdf')


# ----------------------------------------
# ▶️ Inicialização
# ----------------------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
