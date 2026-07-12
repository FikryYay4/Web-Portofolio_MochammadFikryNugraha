import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "portfolio.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    # Session security hardening
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour idle timeout
    # Debug only when explicitly enabled
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    # Max login attempts per minute
    LOGIN_RATE_LIMIT = '5 per minute'
    # Public user credentials (optional)
    PUBLIC_USERNAME = os.getenv('PUBLIC_USERNAME', 'public')
    PUBLIC_PASSWORD = os.getenv('PUBLIC_PASSWORD', 'Public123')