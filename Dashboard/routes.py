from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response
from Auth.form import ResetPasswordRequestForm, ResetPasswordForm

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def index():
  context = {
    "form": ResetPasswordRequestForm()
  }

  return render_template("Main/index.html", **context)