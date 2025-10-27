from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random, pytz

db = SQLAlchemy()

def get_local_time():
  utc_timezone = datetime.now(pytz.utc)
  local_tz = pytz.timezone('Africa/Nairobi')
  return utc_timezone.astimezone(local_tz)

class BaseModel(db.Model):
  __abstract__ = True
  id = db.Column(db.Integer(), nullable=False, primary_key=True)
  unique_id = db.Column(db.Integer(), unique=True, nullable=False)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.unique_id = random.randint(10000000, 99999999)

  def __repr__(self):
    return f"{self.id} - {self.unique_id}"

class UserBaseModel(db.Model):
  __abstract__ = True
  first_name = db.Column(db.String(50), nullable=False)
  last_name = db.Column(db.String(50), nullable=False)
  email = db.Column(db.String(100), nullable=False, unique=True)
  created_at = db.Column(db.DateTime(), default=get_local_time())
  password = db.Column(db.String(80), nullable=False)

  def __repr__(self):
    return f"{self.first_name} {self.last_name}"
  
  def get_id(self):
    return self.unique_id
