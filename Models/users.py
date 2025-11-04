from .base_model import BaseModel, UserBaseModel, db
from flask_login import UserMixin
from .case import Case

class Lawyers(BaseModel, UserBaseModel, db.Model, UserMixin):
  __tablename__ = 'lawyers'
  is_active = db.Column(db.Boolean, default=True)
  role_name = db.Column(db.String(10), default="Lawyer")
  clients = db.relationship('Client', backref='lawyer', lazy='dynamic')
  cases = db.relationship('Case', backref='managing_lawyer', lazy='dynamic')
  
  @property
  def full_name(self):
    return f'{self.first_name} {self.last_name}'
  
  def __repr__(self):
    return f'<User {self.name} - {self.email}>'
  
class Client(BaseModel, UserBaseModel, db.Model, UserMixin):
  __tablename__ = 'clients'
  lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), nullable=False)
  is_active = db.Column(db.Boolean, default=True)
  address = db.Column(db.Text())
  role_name = db.Column(db.String(10), default="Client")
  client_type = db.Column(db.String(20), nullable=False)
  cases = db.relationship('Case', backref='client', lazy='dynamic', cascade='all, delete-orphan')
  
  @property
  def full_name(self):
    return f'{self.first_name} {self.last_name}'
  
  def __repr__(self):
    return f'<Client {self.full_name}>'
