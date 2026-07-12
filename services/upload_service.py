import os
import secrets
from werkzeug.utils import secure_filename
from flask import current_app

# Allowed extensions by category
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
VIDEO_EXTENSIONS = {'mp4', 'webm'}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

# Allowed MIME patterns
ALLOWED_MIME = {
    'png', 'jpeg', 'jpg', 'gif', 'webp', 'svg',
    'mp4', 'webm',
}


def allowed_file(filename):
    """Check file extension is in allowlist."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _check_mimetype(file):
    """Validate MIME type matches whitelist."""
    mime = file.mimetype or ''
    if not mime:
        return False
    if not file.content_type or not file.content_type.startswith(('image/', 'video/')):
        return False
    return True


def save_file(file, subfolder=''):
    """Save uploaded file with validated filename and MIME type."""
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None
    if not _check_mimetype(file):
        return None

    # Preserve original extension but use secure random name
    ext = file.filename.rsplit('.', 1)[1].lower()
    original_base = secure_filename(file.filename).rsplit('.', 1)[0]
    if not original_base:
        original_base = 'file'
    # Truncate to avoid overly long filenames
    filename = f"{original_base[:32]}_{secrets.token_hex(8)}.{ext}"

    upload_path = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        upload_path = os.path.join(upload_path, subfolder)
    os.makedirs(upload_path, exist_ok=True)

    # Prevent path traversal via filename
    full_path = os.path.normpath(os.path.join(upload_path, filename))
    if not full_path.startswith(os.path.normpath(upload_path)):
        return None

    file.save(full_path)
    return filename


def delete_file(filename, subfolder=''):
    if not filename:
        return False
    upload_path = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        upload_path = os.path.join(upload_path, subfolder)
    # Sanitize filename before deletion
    safe_name = secure_filename(filename)
    if safe_name != filename:
        return False
    filepath = os.path.join(upload_path, safe_name)
    filepath = os.path.normpath(filepath)
    if not filepath.startswith(os.path.normpath(upload_path)):
        return False
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def save_project_image(file):
    return save_file(file, subfolder='project_images')


def delete_project_image(filename):
    return delete_file(filename, subfolder='project_images')