from datetime import datetime
from services.upload_service import ALLOWED_EXTENSIONS


def format_date(dt):
    if not dt:
        return ''
    return dt.strftime('%B %d, %Y')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
