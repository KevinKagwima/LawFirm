from flask import Flask
from Models.base_model import db
from Models.users import *
from Models.case import *
from Models.event import *
from Models.payment import *
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def drop_tables():
  db.drop_all()
  print("Tables dropped successully")

def create_tables():
  db.create_all()
  print("Tables created successully")

if __name__ == "__main__":
  with app.app_context():
    drop_tables()
    create_tables()
