from functools import wraps
from flask import session, redirect, url_for, current_app


def check_login(username, password):
    """Cek login admin dengan kredensial dari config."""
    cfg_username = current_app.config.get('ADMIN_USERNAME')
    cfg_password = current_app.config.get('ADMIN_PASSWORD')
    if not cfg_password:
        return False
    return (username == cfg_username and password == cfg_password)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('public.login'))
        return f(*args, **kwargs)
    return decorated


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('public.login'))
        return f(*args, **kwargs)
    return decorated

# login_required lama untuk public (cek 'public_logged_in') - tidak digunakan lagi