import io
import json
import pathlib
from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for, flash, send_file
from website.includes.database.database_models import ListMFC, TypesTemplate, Regions, PortalOrders, Users, \
    DelegateOrderUser
from ..extensions import database
from flask_login import login_user, login_required

orders = Blueprint('orders', __name__)

@orders.route('/order_portal', methods=["GET"])
@login_required
def main_orders():
    orders = PortalOrders.query.all()
    return render_template("/html_mfc/portal_orders/orders_mfc.html", orders=orders)

@orders.route('/order_portal/view_order', methods=["POST"])
@login_required
def view_order():
    id_order = request.form.get("id_order")
    id_region = request.form.get("id_region")
    order = PortalOrders.query.filter(PortalOrders.id == id_order, PortalOrders.region_mfc == id_region).first()
    if order:
        users = Users.query.filter(Users.id_region == id_region, Users.id_role != 1).all()
        return render_template("/html_mfc/portal_orders/view_order/modal_view_order.html",
                               order=order,
                               users=users)

@orders.route('/order_portal/get_user_list', methods=["POST"])
@login_required
def get_user_list():
    id_region = request.form.get("id_region")
    id_order = request.form.get("id_order")

    allDelegateUser = DelegateOrderUser.query.filter(DelegateOrderUser.id_order == id_order,
                                                     DelegateOrderUser.id_region == id_region).all()

    return render_template("/html_mfc/portal_orders/view_order/list_users_delegate.html",
                           allDelegateUser=allDelegateUser)

@orders.route('/order_portal/add_user_list', methods=["POST"])
@login_required
def add_user_list():
    id_region = request.form.get("id_region")
    id_order = request.form.get("id_order")
    id_user = request.form.get("id_user")

    delegateOrderUser = DelegateOrderUser.query.filter(DelegateOrderUser.id_user == id_user,
                                                       DelegateOrderUser.id_region == id_region,
                                                       DelegateOrderUser.id_order == id_order).first()
    if not delegateOrderUser:
        addDelegateOrderUser = DelegateOrderUser(id_user=id_user,
                                                 id_region=id_region,
                                                 notify=False,
                                                 id_order=id_order)
        database.session.add(addDelegateOrderUser)
        database.session.commit()
        return jsonify({"status": True})

    return jsonify({"status": False})
