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

# Files/dirs to ignore when listing (e.g. certificates folder scans)
_IGNORE_NAMES = {'.gitkeep', '.gitignore', '.ds_store', 'thumbs.db'}

SUPABASE_BUCKET = os.environ.get('SUPABASE_STORAGE_BUCKET', 'uploads')


def allowed_file(filename):
    """Check file extension is in allowlist."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _check_mimetype(file):
    """Validate MIME type matches whitelist."""
    if not file.content_type or not file.content_type.startswith(('image/', 'video/')):
        return False
    return True


_supabase_client = None
_supabase_checked = False


def _get_supabase_client():
    """Lazily create (and cache) the Supabase client. Returns None if not configured,
    so the app can fall back to local disk (useful for local dev without Supabase)."""
    global _supabase_client, _supabase_checked
    if _supabase_checked:
        return _supabase_client
    _supabase_checked = True
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_KEY')
    if not url or not key:
        print("[UPLOAD] SUPABASE_URL/SUPABASE_SERVICE_KEY not set - using local disk storage", flush=True)
        return None
    try:
        from supabase import create_client
        _supabase_client = create_client(url, key)
        print("[UPLOAD] Supabase Storage client ready", flush=True)
    except Exception as e:
        print(f"[UPLOAD] Failed to init Supabase client: {e}", flush=True)
        _supabase_client = None
    return _supabase_client


def _storage_path(filename, subfolder=''):
    return f"{subfolder}/{filename}" if subfolder else filename


def save_file(file, subfolder=''):
    """Save an uploaded file. Returns a public URL (Supabase configured) or a bare
    filename (local disk fallback for dev), or None if the file is invalid/rejected."""
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
    file_bytes = file.read()
    if not file_bytes:
        return None

    client = _get_supabase_client()
    if client:
        storage_path = _storage_path(filename, subfolder)
        content_type = file.content_type or 'application/octet-stream'
        try:
            client.storage.from_(SUPABASE_BUCKET).upload(
                storage_path, file_bytes, {"content-type": content_type}
            )
        except Exception as e:
            print(f"[UPLOAD] Supabase upload failed for {storage_path}: {e}", flush=True)
            return None
        try:
            return client.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
        except Exception as e:
            print(f"[UPLOAD] Supabase get_public_url failed for {storage_path}: {e}", flush=True)
            return None

    # Local disk fallback (dev without Supabase configured)
    upload_path = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        upload_path = os.path.join(upload_path, subfolder)
    os.makedirs(upload_path, exist_ok=True)
    full_path = os.path.normpath(os.path.join(upload_path, filename))
    if not full_path.startswith(os.path.normpath(upload_path)):
        return None
    with open(full_path, 'wb') as f:
        f.write(file_bytes)
    return filename


def delete_file(value, subfolder=''):
    """Delete a previously-saved file. Accepts either a Supabase public URL
    (used by DB columns like Project.thumbnail/Profile.photo/Skill.icon) or a
    bare filename with a known subfolder (used by certificates, which are
    tracked by filesystem/storage listing rather than a DB column)."""
    if not value:
        return False

    client = _get_supabase_client()

    if value.startswith('http://') or value.startswith('https://'):
        if not client:
            return False
        marker = f"/object/public/{SUPABASE_BUCKET}/"
        idx = value.find(marker)
        if idx == -1:
            return False
        storage_path = value[idx + len(marker):].split('?')[0]
        try:
            client.storage.from_(SUPABASE_BUCKET).remove([storage_path])
            return True
        except Exception as e:
            print(f"[UPLOAD] Supabase delete failed for {storage_path}: {e}", flush=True)
            return False

    if client:
        storage_path = _storage_path(value, subfolder)
        try:
            client.storage.from_(SUPABASE_BUCKET).remove([storage_path])
            return True
        except Exception as e:
            print(f"[UPLOAD] Supabase delete failed for {storage_path}: {e}, trying local", flush=True)
            # fall through - might genuinely be a pre-migration local file

    # Legacy local file delete
    upload_path = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        upload_path = os.path.join(upload_path, subfolder)
    safe_name = secure_filename(value)
    if safe_name != value:
        return False
    filepath = os.path.normpath(os.path.join(upload_path, safe_name))
    if not filepath.startswith(os.path.normpath(upload_path)):
        return False
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def list_certificate_files():
    """Merge build-time bundled certificates (committed in static/uploads/certificates,
    e.g. toefl.jpg/toeic.jpg) with runtime-uploaded ones (Supabase Storage, or local
    UPLOAD_FOLDER when Supabase isn't configured). Returns a de-duplicated,
    sorted list of dicts: {'filename': str, 'size_display': str, 'url': str|None}.
    'url' is only set for Supabase-hosted files (full public URL); local/bundled
    files are None and should be resolved with upload_url() in templates.
    """
    results = {}

    static_base = os.path.join(current_app.config['STATIC_DIR'], 'uploads', 'certificates')
    if os.path.isdir(static_base):
        for f in os.listdir(static_base):
            if f.lower() in _IGNORE_NAMES:
                continue
            fp = os.path.join(static_base, f)
            if os.path.isfile(fp):
                results[f] = {'filename': f, 'size_display': _format_size(os.path.getsize(fp)), 'url': None}

    client = _get_supabase_client()
    if client:
        try:
            entries = client.storage.from_(SUPABASE_BUCKET).list('certificates')
            for e in entries:
                name = e.get('name')
                if not name or name.lower() in _IGNORE_NAMES:
                    continue
                meta = e.get('metadata') or {}
                size = meta.get('size')
                url = client.storage.from_(SUPABASE_BUCKET).get_public_url(f'certificates/{name}')
                results[name] = {'filename': name, 'size_display': _format_size(size), 'url': url}
        except Exception as e:
            print(f"[UPLOAD] Supabase certificate list failed: {e}", flush=True)
    else:
        upload_base = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates')
        if os.path.isdir(upload_base):
            for f in os.listdir(upload_base):
                if f.lower() in _IGNORE_NAMES:
                    continue
                fp = os.path.join(upload_base, f)
                if os.path.isfile(fp):
                    results[f] = {'filename': f, 'size_display': _format_size(os.path.getsize(fp)), 'url': None}

    return sorted(results.values(), key=lambda x: x['filename'])


def _format_size(size_bytes):
    if not size_bytes:
        return '-'
    size_bytes = int(size_bytes)
    if size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    return f'{size_bytes / (1024 * 1024):.1f} MB'


def save_project_image(file):
    return save_file(file, subfolder='project_images')


def delete_project_image(value):
    return delete_file(value, subfolder='project_images')