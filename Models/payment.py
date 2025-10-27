from .base_model import db, BaseModel, get_local_time

class Payment(BaseModel, db.Model):
  """Payment records for cases"""
  __tablename__ = 'payments'
  amount = db.Column(db.Integer(), nullable=False)
  date_received = db.Column(db.Date, nullable=False, default=get_local_time())
  payment_method = db.Column(db.Enum('cash', 'check', 'bank_transfer', 'card'), nullable=False)
  reference = db.Column(db.String(100))  # Check number, transaction ID, etc.
  notes = db.Column(db.Text)
  case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
  created_at = db.Column(db.DateTime, default=get_local_time())
  
  def __repr__(self):
    return f'<Payment ${self.amount} - Case {self.case_id}>'