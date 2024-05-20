import datetime
import io
import pathlib
from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for, flash, send_file
from website.includes.database.database_models import ListMFC, TypesTemplate
from ..extensions import database
from flask_login import login_user, login_required

from ..includes.database.database_mfc import QueueStat

queue = Blueprint('queue', __name__)

@queue.route('/queue', methods=["GET"])
@login_required
def main_queue():
    all_queue = QueueStat.query.filter(QueueStat.dat_p > datetime.datetime.strptime("16.05.2024", "%d.%m.%Y")).all()
    return render_template("/html_mfc/queue/queue_mfc.html", all_queue=all_queue)
