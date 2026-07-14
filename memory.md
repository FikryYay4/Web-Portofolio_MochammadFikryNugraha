# Memory — Web-Portofolio

Proyek: `C:\Users\Administrator\Documents\Web-Portofolio`
Stack: Flask + SQLAlchemy + Vercel deployment

---

## Perubahan & Perbaikan

### 1. `app.py` — Fix static route fallback (Vercel path mismatch)

**Masalah**: Di Vercel, `UPLOAD_FOLDER = /tmp/uploads/`. File upload disimpan di `/tmp/uploads/cert/x.jpg`. Tapi `url_for('static', filename='uploads/cert/x.jpg')` fallback ke `/tmp/uploads/uploads/cert/x.jpg` (double `uploads/`). Gambar tidak muncul.

**Perbaikan** (`app.py:44-58`):
- Static route `static_from_anywhere()` pertama cek `STATIC_DIR` (read-only).
- Fallback ke `UPLOAD_FOLDER` — strip `uploads/` prefix dari filename sebelum join.
- `path_components = filename.split('/')`, jika index[0] == 'uploads', ambil index[1:] sebagai `filename_clean`.

**File berimbas**: Semua template yang pakai `url_for('static', filename='uploads/...')` — project thumbnails, project_images, certificates.

---

### 2. `routes/admin.py` — Certificate delete hanya target UPLOAD_FOLDER

**Masalah**: Delete route sebelumnya coba `os.remove()` di `STATIC_DIR/uploads/certificates/`. Di Vercel, `/var/task/static/` read-only, `os.remove()` throw OSError. Di local, seeded file di `static/uploads/certificates/` bisa kehapus.

**Perbaikan** (`admin.py:400-420`):
- Hapus loop `bases` (STATIC_DIR + UPLOAD_FOLDER).
- Cuma target `os.path.join(UPLOAD_FOLDER, 'certificates')`.
- Jika file tidak ada di UPLOAD_FOLDER → flash "Bundled file cannot be deleted from here."
- Jika OSError → flash "Could not delete file (read-only?)."

---

### 3. `models/project.py` — Tambah kolom `is_hidden`

**Baris**: `project.py:18`
```python
is_hidden = db.Column(db.Boolean, default=False)
```

**Tujuan**: Kontrol visibilitas project dari admin. Public query filter `is_hidden=False`.

---

### 4. `models/hidden_certificate.py` — Model baru

**File baru**: `models/hidden_certificate.py`
```python
class HiddenCertificate(db.Model):
    __tablename__ = 'hidden_certificates'
    filename = db.Column(db.String(200), primary_key=True)
```

**Tujuan**: Simpan daftar certificate filename yang di-hide. Setiap entry = 1 file di-hide.

---

### 5. `models/__init__.py` — Import HiddenCertificate

**Baris**: `__init__.py:10`
```python
from models.hidden_certificate import HiddenCertificate
```

---

### 6. `routes/admin.py` — Route `project_toggle_hidden`

**Baris**: `admin.py:224-232`
```python
@admin_bp.route('/projects/<int:project_id>/toggle-hidden', methods=['POST'])
def project_toggle_hidden(project_id):
    project.is_hidden = not project.is_hidden
```
Toggle `is_hidden` boolean, commit, redirect ke projects_list.

---

### 7. `routes/admin.py` — Route `certificates_toggle_hidden`

**Baris**: `admin.py:380-397`
```python
@admin_bp.route('/certificates/toggle-hidden', methods=['POST'])
def certificates_toggle_hidden():
```
Cek entry `HiddenCertificate.query.get(fname)`. Jika ada → delete (show). Jika tidak ada → add (hide).

---

### 8. `routes/admin.py` — Update `certificates_list` include hidden status

**Baris**: `admin.py:337-360`
- Query `HiddenCertificate.query.all()` → set `hidden = {h.filename}`.
- Setiap cert dict tambah key `'hidden': f in hidden`.
- Template render `certificates.html` dengan status hidden.

---

### 9. `routes/public.py` — Filter hidden items di public route

**Baris**: `public.py:16`
```python
projects = Project.query.filter_by(is_hidden=False).order_by(...)
```
**Baris**: `public.py:17,27`
```python
hidden_cert_filenames = {h.filename for h in HiddenCertificate.query.all()}
# skip if f in hidden_cert_filenames
```

---

### 10. `templates/dashboard/projects.html` — Tambah kolom Status + Hide/Show button

**Baris**: `projects.html:25-26` — `<th>Status</th>`.
**Baris**: `projects.html:41-47` — Badge "Hidden" (red) / "Visible" (green).
**Baris**: `projects.html:49-52` — Form toggle: `url_for('admin.project_toggle_hidden', ...)`.
- Button text: "Show" jika hidden, "Hide" jika visible.

---

### 11. `templates/dashboard/certificates.html` — Tambah kolom Status + Hide/Show button

**Baris**: `certificates.html:31-32` — `<th>Status</th>`.
**Baris**: `certificates.html:43-48` — Badge warna.
**Baris**: `certificates.html:51-54` — Form toggle: `url_for('admin.certificates_toggle_hidden')`.

---

### 12. `app.py` — Auto-migrasi kolom `is_hidden`

**Baris**: `app.py:89-98`
```python
from sqlalchemy import inspect
inspector = inspect(db.engine)
cols = [c['name'] for c in inspector.get_columns('projects')]
if 'is_hidden' not in cols:
    db.session.execute('ALTER TABLE projects ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE')
```
Jalan setiap app startup. Hanya tambah kolom jika belum ada. Support SQLite + PostgreSQL.

---

### 13. `sections/certificates.html` — Perbaiki caption label (tidak disentuh)

Tidak diubah. Tapi pastikan label untuk `IMG_20250604_0001_page-0001.jpg` dan `IMG_20250604_0001_page-0002.jpg` sudah ada di dictionary `labels` (line 20-21).

---

## Ringkasan File Diubah

| File | Tipe Perubahan |
|------|---------------|
| `app.py` | Edit (static route + migration) |
| `routes/admin.py` | Edit (delete route + toggle routes + cert list) |
| `routes/public.py` | Edit (filter hidden) |
| `models/project.py` | Edit (tambah is_hidden) |
| `models/__init__.py` | Edit (import HiddenCertificate) |
| `models/hidden_certificate.py` | **Baru** |
| `templates/dashboard/projects.html` | Edit (status kolom + toggle) |
| `templates/dashboard/certificates.html` | Edit (status kolom + toggle) |

Total: 8 file (1 baru, 7 edit).
