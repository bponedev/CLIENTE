from flask import Blueprint, render_template
from app.users import list_users

users_bp = Blueprint("users", __name__)

@users_bp.route("/users")
def users_view():
    data = list_users()
    return render_template("admin_users.html", users=data)
