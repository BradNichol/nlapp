from flask import redirect, flash, render_template, request, session
from functools import wraps
from app import app

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        if session.get('approved') == 'NO':
            flash ('Your account has not been approved. Please contact administrator.')
            return render_template("login.html")
        return f(*args, **kwargs)
    return decorated_function