# clients/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, TelField, EmailField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional
from Models.users import Client

class ClientForm(FlaskForm):
  first_name = StringField('First Name', validators=[
    DataRequired(),
    Length(min=1, max=50)
  ])
  last_name = StringField('Last Name', validators=[
    DataRequired(),
    Length(min=1, max=50)
  ])
  email = EmailField('Email Address', validators=[
    Email(),
    Length(max=120)
  ])
  phone = TelField('Phone Number', validators=[
    Optional(),
    Length(max=20)
  ])
  address = TextAreaField('Address', validators=[
    Optional(),
    Length(max=500)
  ])
  client_type = SelectField('Client Type', choices=[
    ('individual', 'Individual'),
    ('business', 'Business'),
    ('organization', 'Organization')
  ], default='individual')
