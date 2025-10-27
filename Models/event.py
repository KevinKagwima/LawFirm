from .base_model import db, BaseModel, get_local_time

class Event(BaseModel, db.Model):
    """Calendar events for cases (court dates, meetings, deadlines)"""
    __tablename__ = 'events'
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False, index=True)
    event_time = db.Column(db.Time, nullable=True)
    event_type = db.Column(db.Enum('court_date', 'client_meeting', 'filing_deadline', 'other'))
    
    # Foreign key
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=get_local_time())
    
    @property
    def ics_filename(self):
      """Generate filename for .ics calendar file"""
      return f"event_{self.id}_{self.event_date.strftime('%Y%m%d')}.ics"
    
    def __repr__(self):
      return f'<Event {self.title} - {self.event_date}>'