# Memory — Web-Portofolio

Proyek: `C:\Users\Administrator\Documents\Web-Portofolio`
Stack: Flask + SQLAlchemy + Vercel deployment

---

## Perubahan & Perbaikan (Final)

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

### 3. Hidden/Visible Integration (Admin ↔ Public)

**Masalah**: User ingin sembunyikan project/certificate di admin → tidak muncul di public. Sebelumnya tidak ada fitur ini.

**Solusi awal** (v1): Tambah kolom `is_hidden` ke model `Project` + table `hidden_certificates` + migration `ALTER TABLE` di `app.py`.

**Masalah v1**: Migration `ALTER TABLE projects ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE` gagal di PostgreSQL (Vercel/Neon). Kolom tidak terbuat, query `SELECT projects.is_hidden` error `UndefinedColumn`.

**Solusi final** (v2): Pakai table terpisah pattern sama kayak `HiddenCertificate`. Hindari `ALTER TABLE` sama sekali.

#### a. `models/project.py` — **Dihapus** kolom `is_hidden`
```python
# Dihapus:
# is_hidden = db.Column(db.Boolean, default=False)
```

#### b. `models/hidden_project.py` — **Baru**
```python
class HiddenProject(db.Model):
    __tablename__ = 'hidden_projects'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True)
```

#### c. `models/hidden_certificate.py` — Tetap
```python
class HiddenCertificate(db.Model):
    __tablename__ = 'hidden_certificates'
    filename = db.Column(db.String(200), primary_key=True)
```

#### d. `models/__init__.py` — Import kedua model
```python
from models.hidden_certificate import HiddenCertificate
from models.hidden_project import HiddenProject
```

#### e. `routes/admin.py` — Toggle routes
```python
@admin_bp.route('/projects/<int:project_id>/toggle-hidden', methods=['POST'])
def project_toggle_hidden(project_id):
    entry = HiddenProject.query.get(project_id)
    if entry:
        db.session.delete(entry)  # Show
    else:
        db.session.add(HiddenProject(project_id=project_id))  # Hide
    db.session.commit()
```

```python
@admin_bp.route('/certificates/toggle-hidden', methods=['POST'])
def certificates_toggle_hidden():
    fname = request.form.get('filename')
    entry = HiddenCertificate.query.get(fname)
    if entry:
        db.session.delete(entry)  # Show
    else:
        db.session.add(HiddenCertificate(filename=fname))  # Hide
    db.session.commit()
```

#### f. `routes/admin.py` — `projects_list` pass `hidden_ids` ke template
```python
hidden_ids = {h.project_id for h in HiddenProject.query.all()}
return render_template('dashboard/projects.html', projects=projects, hidden_ids=hidden_ids)
```

#### g. `routes/admin.py` — `certificates_list` include `hidden` status
```python
hidden = {h.filename for h in HiddenCertificate.query.all()}
# ... certs.append({'filename': f, 'hidden': f in hidden})
```

#### h. `routes/public.py` — Filter hidden items
```python
# Projects
hidden_project_ids = {h.project_id for h in HiddenProject.query.all()}
projects = Project.query.filter(Project.id.notin_(hidden_project_ids)).order_by(...).all()

# Certificates
hidden_cert_filenames = {h.filename for h in HiddenCertificate.query.all()}
# skip if f in hidden_cert_filenames
```

#### i. `templates/dashboard/projects.html` — Status badge + Hide/Show button
```jinja
{% if project.id in hidden_ids %}<span class="tag tag--sm" style="...">Hidden</span>
{% else %}<span class="tag tag--sm" style="...">Visible</span>{% endif %}
<button type="submit">{{ 'Show' if project.id in hidden_ids else 'Hide' }}</button>
```

#### j. `templates/dashboard/certificates.html` — Status badge + Hide/Show button
```jinja
{% if cert.hidden %}Hidden{% else %}Visible{% endif %}
<button type="submit">{{ 'Show' if cert.hidden else 'Hide' }}</button>
```

#### k. `app.py` — Hapus migration `ALTER TABLE` (sudah tidak dipakai)
```python
# Dihapus:
# from sqlalchemy import inspect
# inspector = inspect(db.engine)
# cols = [c['name'] for c in inspector.get_columns('projects')]
# if 'is_hidden' not in cols:
#     db.session.execute('ALTER TABLE projects ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE')
#     db.session.commit()
```

---

### 4. `sections/certificates.html` — Caption label sudah benar

Tidak diubah. Label untuk `IMG_20250604_0001_page-0001.jpg` dan `IMG_20250604_0001_page-0002.jpg` sudah ada di dictionary `labels` (line 20-21).

---

## Ringkasan File Diubah

| File | Tipe Perubahan |
|------|---------------|
| `app.py` | Edit (static route + hapus migration) |
| `routes/admin.py` | Edit (delete route + 2 toggle routes + list queries) |
| `routes/public.py` | Edit (filter hidden projects + certificates) |
| `models/project.py` | Edit (hapus `is_hidden` kolom) |
| `models/__init__.py` | Edit (import HiddenCertificate + HiddenProject) |
| `models/hidden_certificate.py` | **Baru** |
| `models/hidden_project.py` | **Baru** |
| `templates/dashboard/projects.html` | Edit (status badge + toggle button) |
| `templates/dashboard/certificates.html` | Edit (status badge + toggle button) |

Total: 9 file (2 baru, 7 edit).

---

## Deploy History

1. **Commit `34f8452`** — Initial fixes: static route, cert delete, is_hidden column, HiddenCertificate, toggle routes, migration
2. **Commit `bfa0a61`** — Fix: ganti `is_hidden` kolom dengan `HiddenProject` table (PostgreSQL ALTER TABLE fix)
3. **Redeploy Vercel** — Production: `https://web-portofolio-mochammad-fikry-nugr.vercel.app` (READY)