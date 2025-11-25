from flask import Blueprint, render_template
from app.offices import list_offices

offices_bp = Blueprint("offices", __name__)

@offices_bp.route("/offices")
def offices_view():
    data = list_offices()
    return render_template("offices.html", offices=data)
