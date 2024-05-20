import io
import json
import pathlib
from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for, flash, send_file
from website.includes.database.database_models import ListMFC, TypesTemplate, Regions, ListCameraMFC
from ..extensions import database
from flask_login import login_user, login_required, current_user

settings = Blueprint('settings', __name__)

@settings.route('/settings', methods=["GET"])
@login_required
def main_settings():
    regions = Regions.query.all()
    list_camera = ListCameraMFC.query.filter(ListCameraMFC.id_region == current_user.region.id).all()

    return render_template("/html_mfc/settings/settings_mfc.html",
                           regions=regions,
                           list_camera=list_camera)

@settings.route('/settings/save_info_settings', methods=["POST"])
@login_required
def save_info_settings():
    id_region = request.form.get("id_region")
    data = request.form.get("data")

    region = Regions.query.filter(Regions.id == id_region).first()
    json_data = json.loads(data)
    for data in json_data:
        name = data['name']
        value = data['value']
        setattr(region, name, value)
    database.session.commit()
    return jsonify({"status": True})

@settings.route('/settings/get_info_settings', methods=["POST"])
@login_required
def get_info_settings():
    id_region = request.form.get("id_region")
    region = Regions.query.filter(Regions.id == id_region).first()
    return render_template("/html_mfc/settings/settings_view.html", region=region)

@settings.route('/settings/save_camera_settings', methods=["POST"])
@login_required
def save_camera_settings():
    id_region = request.form.get("id_region")
    data = request.form.get("data")

    region = Regions.query.filter(Regions.id == id_region).first()
    if region:
        j_data = json.loads(data)
        for data in j_data:
            find = ListCameraMFC.query.filter(ListCameraMFC.name_camera_mfc == data['name']).first()
            if not find:
                add_camera = ListCameraMFC(id_region=current_user.region.id,
                                           name_camera_mfc=data['name'],
                                           url_camera_mfc=data['url'])
                database.session.add(add_camera)
                database.session.commit()
            else:
                find.url_camera_mfc = data['url']
                database.session.commit()
        return jsonify({"status": True})
    return jsonify({"status": False})

@settings.route('/settings/save_portal_settings', methods=["POST"])
@login_required
def save_portal_settings():
    id_region = request.form.get("id_region")
    portal_login = request.form.get("portal_login")
    portal_password = request.form.get("portal_password")

    region = Regions.query.filter(Regions.id == id_region).first()
    if region:
        region.portal_login = portal_login
        region.portal_password = portal_password
        database.session.commit()
    return jsonify({"status": True})

@settings.route('/settings/save_vipnet_settings', methods=["POST"])
@login_required
def save_vipnet_settings():
    id_region = request.form.get("id_region")
    vipnet_login = request.form.get("vipnet_login")
    vipnet_password = request.form.get("vipnet_password")

    region = Regions.query.filter(Regions.id == id_region).first()
    if region:
        region.vipnet_login = vipnet_login
        region.vipnet_password = vipnet_password
        database.session.commit()
    return jsonify({"status": True})

@settings.route('/settings/change_settings_bool', methods=["POST"])
@login_required
def change_settings_bool():
    name = request.form.get("name")
    value = request.form.get("value")

    region = Regions.query.filter(Regions.id == current_user.region.id).first()
    if region:
        b_value = True if value == "true" else False
        setattr(region, name, b_value)
        database.session.commit()
    return jsonify({"status": True})
