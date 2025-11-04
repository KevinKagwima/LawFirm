from functools import wraps
from flask import request, redirect, url_for, flash
from flask_login import current_user

def role_required(role_name):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      if current_user.is_authenticated and current_user.role_name in role_name:
        return f(*args, **kwargs)
      else:
        flash("You don't have the required credentials to view that page", "warning")
        return redirect(url_for('auth.login'))
    return decorated_function
  return decorator
