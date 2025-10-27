from .base_model import db, BaseModel, get_local_time
from .payment import Payment
from .event import Event

class Case(BaseModel, db.Model):
  """Represents a legal case"""
  __tablename__ = 'cases'  
  title = db.Column(db.String(200), nullable=False)
  description = db.Column(db.Text())
  status = db.Column(db.Enum('active', 'closed', 'pending'), default='active', nullable=False)
  case_type = db.Column(db.String(100))  # e.g., 'Criminal', 'Civil', 'Family Law'
  
  # Foreign keys
  client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
  lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), nullable=False)
  
  # Timestamps
  opened_date = db.Column(db.DateTime, default=get_local_time())
  closed_date = db.Column(db.DateTime, nullable=True)
  
  # Relationships
  notes = db.relationship('CaseNote', backref='case', lazy='dynamic', cascade='all, delete-orphan')
  payments = db.relationship('Payment', backref='case', lazy='dynamic', cascade='all, delete-orphan')
  events = db.relationship('Event', backref='case', lazy='dynamic', cascade='all, delete-orphan')
  
  def __repr__(self):
    return f'<Case {self.title} - {self.status}>'

class CaseNote(BaseModel, db.Model):
  """Timeline notes/updates for a case"""
  __tablename__ = 'case_notes'
  content = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime, default=get_local_time(), index=True)
  
  # Foreign key
  case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
  
  # For future client portal: internal notes vs client-visible notes
  is_internal = db.Column(db.Boolean, default=False)
  
  def __repr__(self):
    return f'<CaseNote {self.id} - Case {self.case_id}>'