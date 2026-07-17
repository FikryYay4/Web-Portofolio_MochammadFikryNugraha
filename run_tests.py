import os
from app import create_app

app = create_app()
app.config['TESTING'] = True
client = app.test_client()

# Helper to set CSRF token in session
def set_csrf(sess, token='testtoken'):
    sess['_csrf_token'] = token

# 1 Home page - should be accessible without login (public page)
resp = client.get('/')
assert resp.status_code == 200, 'Home page should be accessible without login'

# 2 Unauthenticated admin dashboard should redirect (302)
assert client.get('/admin/').status_code == 302, 'Unauthenticated admin should redirect'

# 3 Admin login page should load
assert client.get('/login').status_code == 200, 'Admin login page should load'

# 4 Admin login POST with CSRF -> redirect to dashboard
with client.session_transaction() as sess:
    set_csrf(sess, 'adm_good')
resp = client.post('/login', data={'username':'admin','password':'My_portofolio','_csrf_token':'adm_good'})
assert resp.status_code == 302, 'Admin login should redirect to dashboard'

# 5 Admin login without CSRF -> 403
assert client.post('/login', data={'username':'admin','password':'My_portofolio'}).status_code == 403, 'Admin login without CSRF should be 403'

# 6 Dashboard after admin login (200)
assert client.get('/admin/').status_code == 200, 'Dashboard after admin login should be accessible'

# 7 Contact without CSRF -> 403
assert client.post('/contact', data={'name':'a','email':'a@b.com','subject':'s','message':'m'}).status_code == 403, 'Contact without CSRF should be 403'

# 8 Contact with CSRF -> redirect (302)
with client.session_transaction() as sess:
    set_csrf(sess)
assert client.post('/contact', data={'name':'a','email':'a@b.com','subject':'s','message':'m','_csrf_token':'testtoken'}).status_code == 302, 'Contact with CSRF should redirect'

print("All tests passed!")