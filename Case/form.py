# cases/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, DecimalField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import datetime

class CaseForm(FlaskForm):
  title = StringField('Case Title', validators=[
      DataRequired(),
      Length(min=5, max=200)
  ])
  description = TextAreaField('Case Description (Optional)', validators=[
      Optional(),
      Length(max=1000)
  ])
  case_type = SelectField('Case Type', choices=[
      ('', 'Select Case Type'),
      ('criminal', 'Criminal Law'),
      ('civil', 'Civil Litigation'),
      ('family', 'Family Law'),
      ('corporate', 'Corporate Law'),
      ('real_estate', 'Real Estate'),
      ('intellectual_property', 'Intellectual Property'),
      ('employment', 'Employment Law'),
      ('personal_injury', 'Personal Injury'),
      ('immigration', 'Immigration Law'),
      ('other', 'Other')
  ], validators=[DataRequired()])
  court_name = StringField('Court Name', validators=[
      Optional(),
      Length(max=200)
  ])
  case_number = StringField('Case Number', validators=[
      Optional(),
      Length(max=100)
  ])
  opposing_party = StringField('Opposing Party', validators=[
      Optional(),
      Length(max=200)
  ])
  opposing_counsel = StringField('Opposing Counsel', validators=[
      Optional(),
      Length(max=200)
  ])

class CaseNoteForm(FlaskForm):
  content = TextAreaField('Case Note', validators=[
    DataRequired(),
    Length(min=1, max=2000)
  ])
  is_internal = SelectField('Note Type', choices=[
    ("False", 'Client Visible'),
    ("True", 'Internal Only')
  ], default='client_visible')

class PaymentForm(FlaskForm):
  amount = DecimalField('Amount', validators=[
      DataRequired(),
      NumberRange(min=0.01, message='Amount must be greater than 0')
  ], places=2)
  date_received = DateField('Date Received', validators=[
      DataRequired()
  ], default=datetime.now())
  payment_method = SelectField('Payment Method', choices=[
      ('cash', 'Cash'),
      ('check', 'Check'),
      ('bank_transfer', 'Bank Transfer'),
      ('card', 'Credit/Debit Card'),
      ('online', 'Online Payment')
  ], validators=[DataRequired()])
  reference = StringField('Reference/Check Number', validators=[
      Optional(),
      Length(max=100)
  ])
  notes = TextAreaField('Payment Notes', validators=[
      Optional(),
      Length(max=500)
  ])

class EventForm(FlaskForm):
  title = StringField('Event Title', validators=[
      DataRequired(),
      Length(min=5, max=200)
  ])
  description = TextAreaField('Event Description', validators=[
      Optional(),
      Length(max=1000)
  ])
  event_date = DateField('Event Date', validators=[
      DataRequired()
  ], default=datetime.utcnow)
  event_time = SelectField('Event Time', choices=[
      ('', 'Select Time'),
      ('08:00', '8:00 AM'),
      ('08:30', '8:30 AM'),
      ('09:00', '9:00 AM'),
      ('09:30', '9:30 AM'),
      ('10:00', '10:00 AM'),
      ('10:30', '10:30 AM'),
      ('11:00', '11:00 AM'),
      ('11:30', '11:30 AM'),
      ('12:00', '12:00 PM'),
      ('12:30', '12:30 PM'),
      ('13:00', '1:00 PM'),
      ('13:30', '1:30 PM'),
      ('14:00', '2:00 PM'),
      ('14:30', '2:30 PM'),
      ('15:00', '3:00 PM'),
      ('15:30', '3:30 PM'),
      ('16:00', '4:00 PM'),
      ('16:30', '4:30 PM'),
      ('17:00', '5:00 PM')
  ], validators=[Optional()])
  event_type = SelectField('Event Type', choices=[
      ('court_date', 'Court Date'),
      ('client_meeting', 'Client Meeting'),
      ('filing_deadline', 'Filing Deadline'),
      ('discovery_deadline', 'Discovery Deadline'),
      ('deposition', 'Deposition'),
      ('hearing', 'Hearing'),
      ('trial', 'Trial'),
      ('mediation', 'Mediation'),
      ('consultation', 'Consultation'),
      ('other', 'Other')
  ], validators=[DataRequired()])
