from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, BooleanField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from Models.users import Lawyers

class RegistrationForm(FlaskForm):
  first_name = StringField(label="First Name", validators=[DataRequired(message="First Name field required")])
  last_name = StringField(label="Last Name", validators=[DataRequired(message="Last Name field required")])
  email = EmailField(label="Email Address", validators=[Email(), DataRequired(message="Email Address field required")])
  password = PasswordField('Password', validators=[DataRequired(message="Password field is required"), Length(min=8, message='Password must be at least 8 characters long')])
  confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message="Confirm password field is required"), EqualTo('password', message='Passwords must match')])

  def validate_phone_number(self, phone_number_to_validate):
    phone_number = phone_number_to_validate.data
    if phone_number[0] != str(0):
      raise ValidationError("Invalid phone number. Phone number must begin with 0")
    elif phone_number[1] != str(7) and phone_number[1] != str(1):
      raise ValidationError("Invalid phone number. Phone number must begin with 0 followed by 7 or 1")
    elif Lawyers.query.filter_by(phone=phone_number_to_validate.data).first():
      raise ValidationError("Phone Number already exists, Please try another one")

  def validate_email_address(self, email_to_validate):
    email = Lawyers.query.filter_by(email=email_to_validate.data).first()
    if email:
      raise ValidationError("Email Address already exists, Please try another one")

class LoginForm(FlaskForm):
  email = EmailField(label="Email Address", validators=[DataRequired(message="Email address field required")])
  password = PasswordField(label="Password", validators=[DataRequired(message="Password field required")])
  remember_me = BooleanField('Remember Me')

class ResetPasswordRequestForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email()])

class ResetPasswordForm(FlaskForm):
  new_password = PasswordField(label="New Password", validators=[DataRequired(message="Password field required")])
  confirm_password = PasswordField(label="Confirm Password", validators=[EqualTo("new_password", message="Passwords do not match"), DataRequired(message="Confirm Password field required")])
