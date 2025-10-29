from flask import Flask, flash, abort
from flask_login import login_manager, LoginManager
from flask_migrate import Migrate
from Admin.routes import admin_bp
from Case.routes import case_bp
from Dashboard.routes import dashboard_bp
from Clients.routes import client_bp
from Auth.routes import auth_bp
from Errors.handlers import errors_bp
from Models.base_model import db
from Models.users import Lawyers
from config import Config
import os

def create_app():
  app = Flask(__name__)
  app.config.from_object(Config)
  # print(os.environ.get("DATABASE_URL"))

  db.init_app(app)
  migrate = Migrate(app, db)

  app.register_blueprint(case_bp)
  app.register_blueprint(admin_bp)
  app.register_blueprint(auth_bp)
  app.register_blueprint(errors_bp)
  app.register_blueprint(dashboard_bp)
  app.register_blueprint(client_bp)

  login_manager = LoginManager()
  login_manager.blueprint_login_views = {
    'dashboard': '/auth/login',
    'case': '/auth/login',
    'client': '/auth/login',
  }
  login_manager.login_message = "Please login to access this page"
  login_manager.login_message_category = "danger"
  login_manager.init_app(app)

  @login_manager.user_loader
  def load_user(user_id):
    try:
      return Lawyers.query.filter_by(unique_id=user_id).first()
    except:
      flash("Unable to load user", category="danger")
      abort(500)
  
  return app

app = create_app()

if __name__ == "__main__":
  app = create_app()
  app.run(debug=True)
