import io
import pathlib
from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for, flash, send_file
from website.includes.database.database_models import ListMFC, TypesTemplate, ListCameraMFC
from ..extensions import database
from flask_login import login_user, login_required

main_mfc = Blueprint('mfc', __name__)

@main_mfc.route('/main_mfc', methods=["GET"])
@login_required
def mfc():
    #html_user
    list_camera = ListCameraMFC.query.all()
    return render_template("/html_mfc/main_mfc.html", list_camera=list_camera)
