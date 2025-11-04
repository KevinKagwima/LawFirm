from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response
from flask_login import current_user, login_required
from Models.users import Client, Lawyers
from Models.case import Case, CaseNote
from Models.payment import Payment
from Models.event import Event
from decorator import role_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@dashboard_bp.route("/home")
@role_required(["Lawyer"])
@login_required
def index():
  context = {
    "clients": Client.query.filter_by(lawyer_id=current_user.id).all(),
    "cases": Case.query.filter_by(lawyer_id=current_user.id).all(),
  }

  return render_template("Main/index.html", **context)

@dashboard_bp.route("/client/dashboard")
@role_required(["Client"])
@login_required
def client_index():
  context = {
    "lawyer": Lawyers.query.get(current_user.lawyer_id),
    "cases": Case.query.filter_by(client_id=current_user.id).all(),
  }

  return render_template("Client/index.html", **context)
