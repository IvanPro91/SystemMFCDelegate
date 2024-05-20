import io
import json
import pathlib
from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for, flash, send_file
from website.includes.database.database_models import ListMFC, TypesTemplate, Regions, Users
from ..extensions import database
from flask_login import login_user, login_required, current_user

from ..includes.database.database_mfc import Userst

user_org = Blueprint('user_org', __name__)

@user_org.route('/org_users', methods=["GET"])
@login_required
def main_user_org():
    regions = Regions.query.all()
    users_ais = Userst.query.filter(Userst.validbefore == None).all()
    users = Users.query.filter(Users.id_region == current_user.region.id).all()
    return render_template("/html_mfc/user_org/user_org.html", regions=regions,
                           users_ais=users_ais,
                           users=users)

@user_org.route('/org_users/add_user', methods=["POST"])
@login_required
def add_user():
    tn = request.form.get("tn")
    user_ais = Userst.query.filter(Userst.tn == tn).first()
    if user_ais:
        user = Users.query.filter(Users.tn == tn, Users.id_region == current_user.region.id).first()
        if not user:
            add_user = Users(tn=user_ais.tn,
                         job=user_ais.job,
                         user_login=user_ais.fio,
                         id_region=current_user.region.id,
                         id_role=2)
            database.session.add(add_user)
            database.session.commit()
            database.session.flush()
            add_user.set_password("1234567890")
            database.session.commit()

            return jsonify({"status": True, "user_ais": {
                "tn": user_ais.tn,
                "fio": user_ais.fio,
                "job": user_ais.job
            }})
    return jsonify({"status": False})