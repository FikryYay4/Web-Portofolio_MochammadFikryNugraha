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

### 3. `models/project.py` — **Dihapus** kolom `is_hidden` (ganti dengan HiddenProject table)

**Alasan**: Migration `ALTER TABLE projects ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE` gagal di PostgreSQL (Vercel/Neon). Kolom tidak terbuat, query `SELECT projects.is_hidden` error `UndefinedColumn`.

**Solusi**: Pakai table `hidden_projects` (pattern sama kayak `hidden_certificates`). Hindari ALTER TABLE.

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

### 5. `models/hidden_project.py` — Model baru (FIX PostgreSQL)

**File baru**: `models/hidden_project.py`
```python
class HiddenProject(db.Model):
    __tablename__ = 'hidden_projects'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True)
```

**Tujuan**: Simpan daftar `project_id` yang di-hide. Hindari ALTER TABLE di PostgreSQL.

---

### 6. `models/__init__.py` — Import HiddenCertificate & HiddenProject

**Baris**: `__init__.py:9-10`
```python
from models.hidden_certificate import HiddenCertificate
from models.hidden_project import HiddenProject
```

---

### 7. `routes/admin.py` — Route `project_toggle_hidden` (pakai HiddenProject table)

**Baris**: `admin.py:224-232`
```python
@admin_bp.route('/projects/<int:project_id>/toggle-hidden', methods=['POST'])
def project_toggle_hidden(project_id):
    entry = HiddenProject.query.get(project_id)
    if entry:
        db.session.delete(entry)
        flash('Project visible.', 'success')
    else:
        db.session.add(HiddenProject(project_id=project_id))
        flash('Project hidden.', 'success')
    db.session.commit()
```
Toggle via `HiddenProject` table, bukan kolom `is_hidden`.

---

### 8. `routes/admin.py` — Route `certificates_toggle_hidden`

**Baris**: `admin.py:380-397`
```python
@admin_bp.route('/certificates/toggle-hidden', methods=['POST'])
def certificates_toggle_hidden():
    entry = HiddenCertificate.query.get(fname)
    if entry:
        db.session.delete(entry)
        flash('Certificate visible.', 'success')
    else:
        db.session.add(HiddenCertificate(filename=fname))
        flash('Certificate hidden.', 'success')
    db.session.commit()
```

---

### 9. `routes/admin.py` — Update `certificates_list` include hidden status

**Baris**: `admin.py:337-360`
- Query `HiddenCertificate.query.all()` → set `hidden = {h.filename}`.
- Setiap cert dict tambah key `'hidden': f in hidden`.

---

### 10. `routes/admin.py` — Update `projects_list` pass hidden_ids

**Baris**: `admin.py:100-104`
```python
@admin_bp.route('/projects')
def projects_list():
    projects = get_all_projects()
    hidden_ids = {h.project_id for h in HiddenProject.query.all()}
    return render_template('dashboard/projects.html', projects=projects, hidden_ids=hidden_ids)
```

---

### 11. `routes/public.py` — Filter hidden items di public route

**Baris**: `public.py:12-16, 29`
```python
hidden_project_ids = {h.project_id for h in HiddenProject.query.all()}
projects = Project.query.filter(Project.id.notin_(hidden_project_ids)).order_by(...)
project_count = Project.query.filter(Project.id.notin_(hidden_project_ids)).count()
```

**Baris**: `public.py:17, 27` — certificates filter via `HiddenCertificate`.

---

### 12. `templates/dashboard/projects.html` — Kolom Status + Hide/Show button

**Baris**: `projects.html:25` — `<th>Status</th>`.
**Baris**: `projects.html:41-47` — Badge "Hidden" (red) / "Visible" (green) pakai `project.id in hidden_ids`.
**Baris**: `projects.html:49-52` — Form toggle ke `admin.project_toggle_hidden`.

---

### 13. `templates/dashboard/certificates.html` — Kolom Status + Hide/Show button

**Baris**: `certificates.html:31` — `<th>Status</th>`.
**Baris**: `certificates.html:43-48` — Badge warna pakai `cert.hidden`.
**Baris**: `certificates.html:51-54` — Form toggle ke `admin.certificates_toggle_hidden`.

---

### 14. `app.py` — Hapus migrasi ALTER TABLE `is_hidden`

**Baris**: `app.py:87-95` (dihapus)
```python
# Sebelumnya:
try:
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    cols = [c['name'] for c in inspector.get_columns('projects')]
    if 'is_hidden' not in cols:
        db.session.execute('ALTER TABLE projects ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE')
except Exception as e:
    print(...)

# Sekarang hanya:
db.create_all()
seed_data()
```

---

### 15. `sections/certificates.html` — Caption label existing

Tidak diubah. Label untuk `IMG_20250604_0001_page-0001.jpg` dan `IMG_20250604_0001_page-0002.jpg` sudah ada di dictionary `labels` (line 20-21).

---

## Ringkasan File Diubah

| File | Tipe Perubahan |
|------|---------------|
| `app.py` | Edit (static route, hapus migration) |
| `routes/admin.py` | Edit (delete route + toggle routes + cert list + projects list) |
| `routes/public.py` | Edit (filter hidden via HiddenProject/HiddenCertificate) |
| `models/project.py` | Edit (hapus is_hidden) |
| `models/__init__.py` | Edit (import HiddenCertificate, HiddenProject) |
| `models/hidden_certificate.py` | **Baru** |
| `models/hidden_project.py` | **Baru** |
| `templates/dashboard/projects.html` | Edit (status kolom + toggle via hidden_ids) |
| `templates/dashboard/certificates.html` | Edit (status kolom + toggle) |

Total: 9 file (2 baru, 7 edit).

---

## Deployment History

| Commit | Message | Status |
|--------|---------|--------|
| `34f8452` | Fix: image upload path, delete logic, hidden toggle (is_hidden column) | Failed (PostgreSQL ALTER TABLE error) |
| `bfa0a61` | Fix: use HiddenProject table instead of is_hidden column | **Deployed** ✅ |

**Production URL**: `https://web-portofolio-mochammad-fikry-nugr.vercel.app`