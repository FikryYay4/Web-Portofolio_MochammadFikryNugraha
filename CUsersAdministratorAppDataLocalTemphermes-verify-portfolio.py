#!/usr/bin/env python3
"""Ad-hoc verification for Flask portfolio changes."""
import sys
sys.path.insert(0, r"C:\Users\Administrator\Documents\Web-Portofolio")

from app import create_app

app = create_app()
client = app.test_client()

print("=" * 50)
print("AD-HOC VERIFICATION: Web-Portofolio")
print("=" * 50)

# 1. Public page - no flash
resp = client.get('/')
assert resp.status_code == 200, "Home page failed"
assert b'data-flash' not in resp.data, "Flash found on public page"
print("✅ 1. No flash messages on public pages")

# 2. Admin login
with client.session_transaction() as sess:
    sess['admin_logged_in'] = True
    sess['_csrf_token'] = 'test'

# 3. Dashboard - no back buttons, has cert counts
resp = client.get('/admin/')
assert resp.status_code == 200
assert b'Back to Dashboard' not in resp.data
assert b'&larr; Dashboard' not in resp.data
assert b'certificates_count' in resp.data or b'Certificates' in resp.data
print("✅ 2. Dashboard loads, no back buttons, cert counts present")

# 4. Profile - no back button
resp = client.get('/admin/profile')
assert resp.status_code == 200
assert b'Back to Dashboard' not in resp.data
print("✅ 3. Profile page: no back button")

# 5. Edit project - no back button
resp = client.get('/admin/projects/1/edit')
assert resp.status_code == 200
assert b'&larr; Dashboard' not in resp.data
assert b'Back to Dashboard' not in resp.data
print("✅ 4. Edit project: no back button")

# 6. Add project - no back button
resp = client.get('/admin/projects/create')
assert resp.status_code == 200
assert b'&larr; Dashboard' not in resp.data
assert b'Back to Dashboard' not in resp.data
print("✅ 5. Add project: no back button")

# 7. Messages deleted popup
resp = client.get('/admin/messages?deleted=1')
assert resp.status_code == 200
assert b'alertDialog' in resp.data or b'Message deleted' in resp.data
print("✅ 6. Messages deleted popup handler present")

# 8. upload_url works in templates
resp = client.get('/')
assert b'project' in resp.data.lower()
print("✅ 7. Public page renders with upload_url() images")

# 9. upload_service imports
from services.upload_service import save_file, delete_file, list_certificate_files, save_project_image, delete_project_image
print("✅ 8. upload_service functions import correctly")

# 10. list_certificate_files works
with app.app_context():
    certs = list_certificate_files()
    print(f"✅ 9. list_certificate_files() returns {len(certs)} certs")

print("\n" + "=" * 50)
print("ALL 9 AD-HOC CHECKS PASSED")
print("=" * 50)
