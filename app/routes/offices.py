"""
ROTAS PARA GERENCIAR ESCRITÓRIOS
"""

from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.db_helpers import query, execute

offices_bp = Blueprint("offices", __name__)


@offices_bp.route("/offices")
def list_offices():
    offices = query("SELECT * FROM offices")
    return render_template("offices.html", offices=offices)


@offices_bp.route("/offices/create", methods=["POST"])
def create():
    name = request.form["office_name"]
    key = name.upper().replace(" ", "_")

    execute("INSERT INTO offices (office_key, display_name) VALUES (?, ?)", (key, name))

    flash("Escritório criado!", "success")
    return redirect(url_for("offices.list_offices"))


@offices_bp.route("/offices/edit/<office_key>", methods=["GET", "POST"])
def office_edit(office_key):
    office = query("SELECT * FROM offices WHERE office_key=?", (office_key,), one=True)

    if request.method == "POST":
        execute("UPDATE offices SET display_name=? WHERE office_key=?",
                (request.form["display_name"], office_key))

        flash("Alterado!", "success")
        return redirect(url_for("offices.list_offices"))

    return render_template("office_edit.html", office=office)
