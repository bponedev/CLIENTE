"""
ROTAS PRINCIPAIS DOS REGISTROS
- criar
- listar
- editar
- excluir
- restaurar
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db_helpers import query, execute
from app.utils import parse_tags

registros_bp = Blueprint("registros", __name__)


def login_required():
    if "user" not in session:
        return False
    return True


@registros_bp.route("/")
def index():
    if not login_required():
        return redirect(url_for("auth.login"))
    return render_template("index.html")


@registros_bp.route("/submit", methods=["POST"])
def submit():
    nome = request.form["nome"]
    cpf = request.form["cpf"]
    tipo = request.form["tipo_acao"]
    data = request.form["data_fechamento"]
    tags = ",".join(parse_tags(request.form.get("tags", "")))

    execute("""
        INSERT INTO registros (nome, cpf, tipo_acao, data_fechamento, escritorio_dono, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, cpf, tipo, data, session["user"]["role"], tags))

    flash("Registro criado com sucesso!", "success")
    return redirect(url_for("registros.table"))


@registros_bp.route("/table")
def table():
    rows = query("SELECT * FROM registros WHERE ativo=1")
    return render_template("table.html", rows=rows)


@registros_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    reg = query("SELECT * FROM registros WHERE id=?", (id,), one=True)

    if request.method == "POST":
        execute("""
            UPDATE registros
               SET nome=?, cpf=?, tipo_acao=?, data_fechamento=?, tags=?
             WHERE id=?
        """, (
            request.form["nome"],
            request.form["cpf"],
            request.form["tipo_acao"],
            request.form["data_fechamento"],
            request.form["tags"],
            id
        ))
        flash("Alterado com sucesso!", "success")
        return redirect(url_for("registros.table"))

    return render_template("edit.html", reg=reg)


@registros_bp.route("/delete", methods=["POST"])
def delete():
    id = request.form["id"]

    reg = query("SELECT * FROM registros WHERE id=?", (id,), one=True)

    # armazena em excluídos
    execute("""
        INSERT INTO excluidos (id, nome, cpf, escritorio_dono, tipo_acao, data_fechamento)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (reg["id"], reg["nome"], reg["cpf"], reg["escritorio_dono"],
          reg["tipo_acao"], reg["data_fechamento"]))

    # marca como inativo
    execute("UPDATE registros SET ativo=0 WHERE id=?", (id,))

    flash("Registro movido para excluídos.", "warning")
    return redirect(url_for("registros.table"))


@registros_bp.route("/excluidos")
def excluidos():
    rows = query("SELECT * FROM excluidos")
    return render_template("excluidos.html", rows=rows)
