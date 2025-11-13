from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import sqlite3, io, csv, os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

app = Flask(__name__, static_folder='static', template_folder='templates')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    # load distinct office names for the select
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r['name'] for r in cur.fetchall()]
    conn.close()
    return render_template('index.html', tables=tables)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    office = data.get('escritorio', 'geral').strip()
    table = f"office_{office.replace(' ', '_')}"
    conn = get_conn()
    cur = conn.cursor()
    # create table if not exists
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        cpf TEXT,
        tipo_acao TEXT,
        data_fechamento TEXT,
        pendencias TEXT,
        numero_processo TEXT,
        data_protocolo TEXT,
        observacoes TEXT,
        captador TEXT,
        created_at TEXT
    )
    """)
    cur.execute(f"""INSERT INTO {table}
        (nome, cpf, tipo_acao, data_fechamento, pendencias, numero_processo, data_protocolo, observacoes, captador, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('nome'),
        data.get('cpf'),
        data.get('tipo_acao'),
        data.get('data_fechamento'),
        data.get('pendencias'),
        data.get('numero_processo'),
        data.get('data_protocolo'),
        data.get('observacoes'),
        data.get('captador'),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/table')
def table_view():
    office = request.args.get('office')
    conn = get_conn()
    cur = conn.cursor()
    if office:
        table = f"office_{office.replace(' ', '_')}"
        try:
            cur.execute(f"SELECT * FROM {table} ORDER BY id DESC")
            rows = [dict(r) for r in cur.fetchall()]
        except Exception as e:
            rows = []
        conn.close()
        return render_template('table.html', rows=rows, office=office)
    else:
        # show all tables summary
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r['name'] for r in cur.fetchall()]
        conn.close()
        return render_template('table.html', tables=tables, rows=None, office=None)

@app.route('/export/csv')
def export_csv():
    office = request.args.get('office')
    if not office:
        return "Missing office parameter", 400
    table = f"office_{office.replace(' ', '_')}"
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
    except Exception as e:
        return f"Erro ao ler a tabela: {e}", 500
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(cols)
    for r in rows:
        writer.writerow([r[c] for c in cols])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=f'{table}.csv')

def generate_pdf_from_rows(rows, cols, buffer, title='Export'):
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    y = h - 40
    c.setFont('Helvetica-Bold', 14)
    c.drawString(40, y, title)
    y -= 30
    c.setFont('Helvetica', 10)
    # simple table layout
    max_rows_per_page = 40
    row_count = 0
    # header row
    def draw_header():
        nonlocal y, row_count
        c.setFont('Helvetica-Bold', 9)
        x = 40
        for col in cols:
            c.drawString(x, y, str(col)[:15])
            x += 100
        y -= 14
        c.setFont('Helvetica', 9)
        row_count += 1

    draw_header()
    for r in rows:
        x = 40
        for col in cols:
            text = str(r[col]) if r[col] is not None else ''
            c.drawString(x, y, text[:18])
            x += 100
        y -= 12
        row_count += 1
        if row_count >= max_rows_per_page:
            c.showPage()
            y = h - 40
            row_count = 0
            draw_header()
    c.save()

@app.route('/export/pdf')
def export_pdf():
    office = request.args.get('office')
    # if office == 'all' we will export all tables into one PDF (with sections)
    conn = get_conn()
    cur = conn.cursor()
    if office == 'all':
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r['name'] for r in cur.fetchall()]
        buffer = io.BytesIO()
        for tbl in tables:
            try:
                cur.execute(f"SELECT * FROM {tbl}")
                rows = [dict(r) for r in cur.fetchall()]
                cols = [d[0] for d in cur.description]
            except:
                rows = []
                cols = []
            generate_pdf_from_rows(rows, cols, buffer, title=f'Tabela: {tbl}')
        buffer.seek(0)
        conn.close()
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='all_tables.pdf')
    else:
        if not office:
            return "Missing office parameter", 400
        table = f"office_{office.replace(' ', '_')}"
        try:
            cur.execute(f"SELECT * FROM {table}")
            rows = [dict(r) for r in cur.fetchall()]
            cols = [d[0] for d in cur.description]
        except Exception as e:
            return f"Erro ao ler a tabela: {e}", 500
        buffer = io.BytesIO()
        generate_pdf_from_rows(rows, cols, buffer, title=f'Tabela: {table}')
        buffer.seek(0)
        conn.close()
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'{table}.pdf')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
