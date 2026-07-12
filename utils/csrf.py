import secrets
from functools import wraps
from flask import session, abort, request


def generate_csrf_token():
    """Generate a CSRF token stored in session."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']


def csrf_required(f):
    """Decorator: require CSRF token match on POST/PUT/DELETE."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            token = request.form.get('_csrf_token') or request.headers.get('X-CSRF-Token')
            session_token = session.get('_csrf_token')
            if not token or not session_token or token != session_token:
                abort(403)
        return f(*args, **kwargs)
    return decorated