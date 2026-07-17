import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    # Support PostgreSQL (Neon/Supabase) via DATABASE_URL, fallback to SQLite for local
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        # Remove psycopg2-incompatible params; handle via engine options
        from urllib.parse import urlparse, urlencode, parse_qs
        parsed = urlparse(DATABASE_URL)
        qs = parse_qs(parsed.query)
        pgbouncer = qs.pop('pgbouncer', None)
        prepare = qs.pop('prepare_threshold', None)
        clean_qs = urlencode(qs, doseq=True) if qs else ''
        clean_url = f'{parsed.scheme}://{parsed.netloc}{parsed.path}'
        if clean_qs:
            clean_url += f'?{clean_qs}'
        DATABASE_URL = clean_url
    if not DATABASE_URL and os.environ.get('VERCEL') == '1':
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/portfolio.db'
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL or f'sqlite:///{os.path.join(BASE_DIR, "portfolio.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    # On Vercel, filesystem is read-only except /tmp/; store uploads there
    if os.environ.get('VERCEL') == '1':
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
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