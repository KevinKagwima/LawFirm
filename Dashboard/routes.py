from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response
from flask_login import current_user, login_required
from Auth.form import ResetPasswordRequestForm, ResetPasswordForm
from Models.users import Client, Lawyers
from Models.case import Case, CaseNote
from Models.payment import Payment
from Models.event import Event

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@dashboard_bp.route("/home")
@login_required
def index():
  context = {
    "form": ResetPasswordRequestForm(),
    "clients": Client.query.filter_by(lawyer_id=current_user.id).all(),
    "cases": Case.query.filter_by(lawyer_id=current_user.id).all(),
  }

  return render_template("Main/index.html", **context)
