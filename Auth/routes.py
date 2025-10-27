from flask import Blueprint, render_template, redirect, url_for, flash, request, session, make_response
from flask_login import login_required, login_user, logout_user, fresh_login_required, current_user
from flask_bcrypt import Bcrypt
from Models.base_model import db, get_local_time
from Models.users import Lawyers
from .form import RegistrationForm, LoginForm, ResetPasswordForm, ResetPasswordRequestForm
from datetime import timedelta
# from Utils.email import send_email
# from Utils.notification_service import NotificationService
import secrets, string

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
bcrypt = Bcrypt()

def generate_reset_token():
  """Generate a secure random token for password reset"""
  alphabet = string.ascii_letters + string.digits
  return ''.join(secrets.choice(alphabet) for i in range(32))

# Simple in-memory token storage (use Redis in production)
password_reset_tokens = {}

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
  # if current_user.is_authenticated:
  #   return redirect(url_for('dashboard.index'))
  
  form = RegistrationForm()
  
  if form.validate_on_submit():
    try:
      existing_user = Lawyers.query.filter_by(email=form.email.data).first()
      if existing_user:
        flash('Email already registered. Please use a different email', 'danger')
        return redirect(url_for('auth.register'))
      
      user = Lawyers(
        first_name = form.first_name.data,
        last_name = form.last_name.data,
        email=form.email.data.lower().strip(),
        passwords = form.password.data
      )
      db.session.add(user)
      db.session.commit()
      
      flash('Registration successful! Please log in.', 'success')
      return redirect(url_for('auth.login'))
        
    except Exception as e:
      db.session.rollback()
      flash(f'Error: {str(e)}', 'danger')
      return redirect(url_for('auth.register'))

  context = {
    "form": form
  }
  
  return render_template('Auth/register.html', **context)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
  # if current_user.is_authenticated:
  #   return redirect(url_for('dashboard.index'))
  
  form = LoginForm()
  
  if form.validate_on_submit():
    try:
      email = form.email.data.lower().strip()
      user = Lawyers.query.filter_by(email=email, is_active=True).first()

      if not user:
        flash("No user with that email address", "danger")
        return redirect(url_for('auth.login'))
      
      if user and user.check_password_correction(form.password.data):
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to next page if it exists and is safe
        next_page = request.args.get('next')
        if not next_page:
          next_page = url_for('dashboard.index')
        
        flash(f'Welcome back, {user.first_name}, {user.last_name}!', 'success')
        return redirect(next_page)
      else:
        flash('Invalid password.', 'danger')
        return redirect(url_for('auth.login'))
            
    except Exception as e:
      flash(f'Error: {str(e)}', 'danger')
      return redirect(url_for('auth.login'))
      # Log the error in production
  
  context = {
    "form": form
  }

  return render_template('Auth/login.html', **context)

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
  # if current_user.is_authenticated:
  #   return redirect(url_for('dashboard.index'))
  
  form = ResetPasswordRequestForm()
  
  if form.validate_on_submit():
    try:
      email = form.email.data.lower().strip()
      user = Lawyers.query.filter_by(email=email, is_active=True).first()
      
      if user:
        # Generate reset token (in production, use itsdangerous)
        token = generate_reset_token()
        password_reset_tokens[token] = {
          'user_id': user.id,
          'expires': get_local_time() + timedelta(hours=1)
        }
        
        # In production: Send email with reset link
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        print(reset_url)
        
        # For MVP, we'll just show the link (remove this in production!)
        flash(f'Password reset link: {reset_url}', 'info')
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
      else:
        # Don't reveal if email exists for security
        flash('No user found with that email address', 'danger')
        return redirect(url_for('auth.reset_password_request'))
        
    except Exception as e:
      flash(f'Error: {str(e)}', 'danger')
      return redirect(url_for('auth.reset_password_request'))
  
  context = {
    "form": form
  }

  return render_template('auth/reset_password_request.html', **context)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
  # if current_user.is_authenticated:
  #   return redirect(url_for('dashboard.index'))
  
  # Validate token
  token_data = password_reset_tokens.get(token)
  if not token_data or token_data['expires'] < get_local_time():
    flash('Invalid or expired reset token.', 'error')
    return redirect(url_for('auth.reset_password_request'))
  
  user = Lawyers.query.get(token_data['user_id'])
  if not user:
    flash('Invalid reset token.', 'danger')
    return redirect(url_for('auth.reset_password_request'))
  
  form = ResetPasswordForm()
  
  if form.validate_on_submit():
    try:
      user.set_password(form.password.data)
      db.session.commit()
      
      # Remove used token
      password_reset_tokens.pop(token, None)
      
      flash('Your password has been reset successfully. Please log in.', 'success')
      return redirect(url_for('auth.login'))
        
    except Exception as e:
      db.session.rollback()
      flash(f'Error: {str(e)}', 'danger')
      return redirect(url_for('auth.reset_password_request'))
  
  context = {
    "form": form
  }

  return render_template('auth/reset_password.html', **context)

@auth_bp.route('/logout')
@login_required
def logout():
  try:
    logout_user()
  except Exception as e:
    flash(f'Error: {str(e)}', 'danger')
  return redirect(url_for('auth.login'))