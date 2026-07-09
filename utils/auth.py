from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def expert_required(f):
    """
    A decorator that checks if the current user is a verified expert
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_expert:
            flash('You need to be a verified expert to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    A decorator that checks if the current user is an admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
