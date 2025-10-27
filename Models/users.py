from .base_model import BaseModel, UserBaseModel, db
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from .case import Case

bcrypt = Bcrypt()

class Lawyers(BaseModel, UserBaseModel, db.Model, UserMixin):
  __tablename__ = 'lawyers'
  is_active = db.Column(db.Boolean, default=True)
  clients = db.relationship('Client', backref='lawyer', lazy='dynamic')
  cases = db.relationship('Case', backref='managing_lawyer', lazy='dynamic')
  
  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)
  
  def __repr__(self):
    return f'<User {self.name} - {self.email}>'
  
class Client(BaseModel, UserBaseModel, db.Model):
  __tablename__ = 'clients'
  lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), nullable=False)
  address = db.Column(db.Text())
  cases = db.relationship('Case', backref='client', lazy='dynamic', cascade='all, delete-orphan')
  
  @property
  def full_name(self):
    return f'{self.first_name} {self.last_name}'
  
  def __repr__(self):
    return f'<Client {self.full_name}>'
