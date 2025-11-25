from flask import Blueprint, render_template
from app.records import list_records

registros_bp = Blueprint("registros", __name__)

@registros_bp.route("/registros")
def registros_view():
    data = list_records()
    return render_template("table.html", rows=data)
