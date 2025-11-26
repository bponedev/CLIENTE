"""
SISTEMA MONOLÍTICO COMPLETO
- Login / Logout
- Usuários
- Escritórios
- Registros
- Exclusões
- PDF (export)
- Banco de dados SQLite interno
- Rotas centralizadas
"""

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_file
)
import sqlite3
from functools import wraps
from reportlab.pdfgen import canvas
import io

# ===========================================================
# CONFIGURAÇÕES PRINCIPAIS
# ===========================================================

app = Flask(__name__)
app.config["SECRET_KEY"] = "SUA_SECRET_KEY_AQUI"
app.config["DB_PATH"] = "database.db"


# ===========================================================
# BANCO DE DADOS
# ===========================================================

def get_db():
    conn = sqlite3.connect(app.config["DB_PATH"])
    conn.row_factory = sqlite3.Row
    return conn


def execute(sql, params=()):
    db = get_db()
    db.execute(sql, params)
    db.commit()
    db.close()


def query(sql, params=(), one=False):
    db = get_db()
    cur = db.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    db.close()
    return (rows[0] if rows else None) if one else rows


def init_db():
    """Cria as tabelas necessárias."""
    execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            role TEXT DEFAULT 'USER'
        )
    """)

    execute("""
        CREATE TABLE IF NOT EXISTS offices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        )
    """)

    execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cpf TEXT,
            escritorio TEXT,
            tipo_acao TEXT,
            data_fechamento TEXT,
            pendencias TEXT,
            numero_processo TEXT,
            data_protocolo TEXT,
            observacoes TEXT,
            captador TEXT
        )
    """)

    # ===========================================================
    # ADMIN PADRÃO AUTOMÁTICO
    # ===========================================================
    admin = query("SELECT * FROM users WHERE email='admin@admin.com'", one=True)
    if not admin:
        execute("""
            INSERT INTO users (nome, email, senha, role)
            VALUES ('Administrador', 'admin@admin.com', '123', 'ADMIN')
        """)
        print(">>> ADMIN criado automaticamente: admin@admin.com / 123")


# ===========================================================
# DECORATOR DE LOGIN
# ===========================================================

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrap


# ===========================================================
# ROTAS DE AUTENTICAÇÃO
# ===========================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        user = query(
            "SELECT * FROM users WHERE email=? AND senha=?",
            (email, senha),
            one=True
        )

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            flash("Login realizado!", "success")
            return redirect(url_for("home"))

        flash("Credenciais inválidas", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ===========================================================
# HOME
# ===========================================================

@app.route("/")
@login_required
def home():
    offices = query("SELECT nome FROM offices ORDER BY nome ASC")
    return render_template("index.html", offices=offices)


# ===========================================================
# REGISTROS
# ===========================================================

@app.route("/submit", methods=["POST"])
@login_required
def submit():
    data = (
        request.form["nome"],
        request.form["cpf"],
        request.form["escritorio"],
        request.form["tipo_acao"],
        request.form["data_fechamento"],
        request.form["pendencias"],
        request.form["numero_processo"],
        request.form["data_protocolo"],
        request.form["observacoes"],
        request.form["captador"],
    )

    execute("""
        INSERT INTO registros (
            nome, cpf, escritorio, tipo_acao, data_fechamento,
            pendencias, numero_processo, data_protocolo,
            observacoes, captador
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    flash("Registro salvo com sucesso!", "success")
    return redirect(url_for("home"))


@app.route("/registros")
@login_required
def registros():
    r = query("SELECT * FROM registros ORDER BY id DESC")
    return render_template("table.html", registros=r)


# ===========================================================
# USUÁRIOS (ADMIN)
# ===========================================================

@app.route("/admin/users")
@login_required
def users_list():
    if session["role"] != "ADMIN":
        return "Acesso negado."

    users = query("SELECT * FROM users ORDER BY id DESC")
    return render_template("admin_users.html", users=users)


@app.route("/admin/users/create", methods=["GET", "POST"])
@login_required
def users_create():
    if session["role"] != "ADMIN":
        return "Acesso negado."

    if request.method == "POST":
        data = (
            request.form["nome"],
            request.form["email"],
            request.form["senha"],
            request.form["role"]
        )
        execute("""
            INSERT INTO users (nome, email, senha, role)
            VALUES (?, ?, ?, ?)
        """, data)

        return redirect(url_for("users_list"))

    return render_template("admin_users_create.html")


@app.route("/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def users_edit(user_id):
    if session["role"] != "ADMIN":
        return "Acesso negado."

    user = query("SELECT * FROM users WHERE id=?", (user_id,), one=True)

    if request.method == "POST":
        data = (
            request.form["nome"],
            request.form["email"],
            request.form["senha"],
            request.form["role"],
            user_id
        )

        execute("""
            UPDATE users SET nome=?, email=?, senha=?, role=?
            WHERE id=?
        """, data)

        return redirect(url_for("users_list"))

    return render_template("admin_users_edit.html", user=user)


# ===========================================================
# ESCRITÓRIOS
# ===========================================================

@app.route("/offices")
@login_required
def offices_list():
    o = query("SELECT * FROM offices ORDER BY nome ASC")
    return render_template("offices.html", offices=o)


@app.route("/offices/create", methods=["POST"])
@login_required
def offices_create():
    name = request.form["office_name"]
    execute("INSERT INTO offices (nome) VALUES (?)", (name,))
    return redirect(url_for("offices_list"))


@app.route("/offices/edit/<int:office_id>", methods=["GET", "POST"])
@login_required
def offices_edit(office_id):
    office = query("SELECT * FROM offices WHERE id=?", (office_id,), one=True)

    if request.method == "POST":
        execute("UPDATE offices SET nome=? WHERE id=?", (request.form["nome"], office_id))
        return redirect(url_for("offices_list"))

    return render_template("office_edit.html", office=office)


# ===========================================================
# EXPORTAÇÃO EM PDF
# ===========================================================

@app.route("/export/pdf")
@login_required
def export_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    registros = query("SELECT * FROM registros ORDER BY id DESC")

    y = 800
    p.setFont("Helvetica", 12)
    p.drawString(50, y, "Relatório de Registros")
    y -= 30

    for r in registros:
        texto = f"{r['id']} - {r['nome']} - {r['cpf']} - {r['escritorio']}"
        p.drawString(50, y, texto)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="registros.pdf")


# ===========================================================
# INICIALIZAÇÃO DO BANCO AO INICIAR
# ===========================================================

with app.app_context():
    init_db()


# ===========================================================
# EXECUÇÃO LOCAL
# ===========================================================

if __name__ == "__main__":
    app.run(debug=True)
