from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from website.includes.database.database_models import Regions, Users
from flask_login import login_user

auth = Blueprint('auth', __name__)

@auth.route('/', methods=["GET"])
@auth.route('/auth', methods=["GET"])
def user_auth():
    regions = Regions.query.all()
    return render_template("/html_auth/auth.html", regions=regions)

@auth.route('/auth/get_user_region', methods=["POST"])
def get_user_region():
    id_region = request.form.get("id_region")
    all_user = Users.query.filter(Users.id_region == id_region).all()

    result = []
    for user in all_user:
        result.append({"username": user.user_login, "role": user.role.name_role, "id_user": user.id})
    return jsonify({"status": True, "data": result})

@auth.route('/auth/login', methods=["GET"])
def login():
    id_region = request.args.get("id_region")
    id_user = request.args.get("id_user")
    password = request.args.get("password")

    user = Users.query.filter(Users.id == id_user,
                              Users.id_region == id_region).first()
    if not user:
        flash('Пользователь не найден!')
        return redirect(url_for("auth.user_auth"))
    if not password or len(password) < 3:
        flash('Неверный пароль!')
        return redirect(url_for("auth.user_auth"))

    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for("mfc.mfc"))
    else:
        flash('Неверный пароль!')
        return redirect(url_for("auth.user_auth"))
