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

### 5. UI/UX Improvements (Latest)

#### a. Navbar Login/Logout Logic (`templates/layouts/navbar.html`)
- **Guest**: Shows "Login" button (primary style)
- **Public login**: Shows "Admin" link + "Logout"
- **Admin login**: Shows "Dashboard" link + "Logout"
- Fixed: Logout button now appears correctly after any login

#### b. Flash Messages + Alert Dialog (`templates/base.html`, `templates/components/alert_dialog.html`)
- Added global flash message container in `base.html` (fixed top-right, slide-in animation)
- Updated `alert_dialog.html` to handle all flash categories (error, success, warning, info)
- Login page (`templates/pages/login.html`) now includes flash message elements for alert dialog
- All CRUD operations (skills, certificates, messages) show animated toast notifications

#### c. Network Engineering Logo Fix
- **Problem**: Skill "Network Engineering" used wrong icon (`programming/DeviconAndroidstudio.svg`)
- **Fix**: Updated `app.py` seed_data + database record to use `network-engineering/cisco_logo_logoquake.svg`
- **Vercel Static Routing**: Added `/static/(.*)` rewrite in `vercel.json` for SVG assets
- **Files**: `app.py` (seed), `vercel.json` (rewrite), database updated

#### d. Skills CRUD Enhancements (`templates/dashboard/skills.html`)
- Added **Icon Path** input field (text) to both Create and Edit forms
- User can now specify icon path manually OR upload logo file
- Example: `network-engineering/cisco_logo_logoquake.svg`

#### e. Certificates UX (`routes/admin.py`)
- **Toggle Hide/Show**: Works perfectly with flash confirmation
- **Delete**: Shows helpful error "Cannot delete: file system is read-only (Vercel). Hide it instead." instead of generic OSError

#### f. Gmail Mailto Links (`templates/sections/contact.html`, `templates/layouts/footer.html`)
- Pre-filled subject: `"Collab / I'd like to invite you to join my company."`
- Pre-filled body: Full bilingual template (English + Indonesian) with proper URL encoding
- Clicking Gmail icon opens email client with ready-to-send message

#### g. Flowing Logos Animation (`templates/sections/flowing_logos.html`)
- Added Cisco logo (`cisco_logo_logoquake.svg`) to the infinite marquee scroll

---

### 6. Ringkasan File Diubah (Total)

| File | Tipe Perubahan |
|------|---------------|
| `app.py` | Edit (static route + hapus migration + seed icon fix) |
| `routes/admin.py` | Edit (delete route + 2 toggle routes + list queries + cert delete error msg) |
| `routes/public.py` | Edit (filter hidden projects + certificates) |
| `models/project.py` | Edit (hapus `is_hidden` kolom) |
| `models/__init__.py` | Edit (import HiddenCertificate + HiddenProject) |
| `models/hidden_certificate.py` | **Baru** |
| `models/hidden_project.py` | **Baru** |
| `templates/dashboard/projects.html` | Edit (status badge + toggle button) |
| `templates/dashboard/certificates.html` | Edit (status badge + toggle button) |
| `templates/layouts/navbar.html` | Edit (Login/Logout logic) |
| `templates/base.html` | Edit (flash message container) |
| `templates/components/alert_dialog.html` | Edit (all flash categories) |
| `templates/pages/login.html` | Edit (flash elements) |
| `templates/dashboard/skills.html` | Edit (Icon Path input) |
| `templates/sections/contact.html` | Edit (Gmail mailto subject+body) |
| `templates/layouts/footer.html` | Edit (Gmail mailto subject+body) |
| `templates/sections/flowing_logos.html` | Edit (add Cisco logo) |
| `vercel.json` | Edit (static file rewrite) |

**Total: 19 file (2 baru, 17 edit)**

---

### Deploy History

1. **Commit `34f8452`** — Initial fixes: static route, cert delete, is_hidden column, HiddenCertificate, toggle routes, migration
2. **Commit `bfa0a61`** — Fix: ganti `is_hidden` kolom dengan `HiddenProject` table (PostgreSQL ALTER TABLE fix)
3. **Commit `66c18e4`** — Fix: Gmail mailto with subject + Cisco logo in flowing logos
4. **Commit `6eabbd1`** — Fix: Gmail mailto with full subject + body template in footer & contact
5. **Redeploy Vercel** — Production: `https://web-portofolio-mochammad-fikry-nugr.vercel.app` (READY)

---

### Quick Verification Commands

```bash
# Check live deployment
curl -s https://web-portofolio-mochammad-fikry-nugr.vercel.app/ | grep -c "cisco_logo_logoquake.svg"
# Should return > 0

# Check mailto link
curl -s https://web-portofolio-mochammad-fikry-nugr.vercel.app/ | grep -o 'mailto:[^"]*' | head -1
# Should show full subject+body encoded URL

# Check admin login
# admin / admin123
# public / Public123
```

---

### Environment Variables (Vercel)

| Variable | Value | Scope |
|----------|-------|-------|
| `ADMIN_USERNAME` | `admin` | Production, Preview |
| `ADMIN_PASSWORD` | `admin123` | Production, Preview |
| `PUBLIC_USERNAME` | `public` | Production, Preview |
| `PUBLIC_PASSWORD` | `Public123` | Production, Preview |
| `SECRET_KEY` | (auto-generated) | Production, Preview |
| `SESSION_SECURE` | `true` | Production |
| `DATABASE_URL` | (PostgreSQL/Neon) | Production, Preview |

---

### Known Limitations

1. **Vercel read-only filesystem** — Cannot delete certificate files from `/var/task/static/`. Use "Hide" instead.
2. **Mailto length** — Body template is ~1500 chars. Some email clients may truncate. Test on target clients.
3. **SQLite on Vercel** — Uses `/tmp/portfolio.db` (ephemeral). For persistence, use PostgreSQL (Neon/Supabase) via `DATABASE_URL`.
4. **No rate limit storage** — Uses in-memory `memory://`. Resets on cold start. For production, add Redis via `RATELIMIT_STORAGE_URI`.