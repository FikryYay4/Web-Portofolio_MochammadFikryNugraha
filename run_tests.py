import os
from app import create_app

app = create_app()
app.config['TESTING'] = True
client = app.test_client()

# Helper to set CSRF token in session
def set_csrf(sess, token='testtoken'):
    sess['_csrf_token'] = token

# 1 Home page - should be accessible without authentication (public portfolio)
resp = client.get('/')
assert resp.status_code == 200, 'Home page should be accessible without authentication'

# 2 Unauthenticated admin dashboard should redirect (302)
assert client.get('/admin/').status_code == 302, 'Unauthenticated admin should redirect'

# 3 Public login page should load
assert client.get('/login?role=public').status_code == 200, 'Public login page should load'

# 4 Public login POST with CSRF -> redirect to home
with client.session_transaction() as sess:
    set_csrf(sess, 'pub_good')
resp = client.post('/login?role=public', data={'username':'public','password':'Public123','_csrf_token':'pub_good'})
assert resp.status_code == 302, 'Public login should redirect to home'

# 5 Home page after public login (200)
assert client.get('/').status_code == 200, 'Home page after public login should be accessible'

# 6 Public login wrong creds (200)
with client.session_transaction() as sess:
    set_csrf(sess, 'pub_wrong')
resp = client.post('/login?role=public', data={'username':'bad','password':'bad','_csrf_token':'pub_wrong'})
assert resp.status_code == 200, 'Public login wrong credentials should return 200 with flash'

# 7 Public login without CSRF -> 403
assert client.post('/login?role=public', data={'username':'public','password':'Public123'}).status_code == 403, 'Public login without CSRF should be 403'

# 8 Admin login page (unified) should load
assert client.get('/login?role=admin').status_code == 200, 'Admin login page should load'

# 9 Admin login POST with CSRF -> redirect to dashboard
with client.session_transaction() as sess:
    set_csrf(sess, 'adm_good')
resp = client.post('/login?role=admin', data={'username':'admin','password':'My_portofolio','_csrf_token':'adm_good'})
assert resp.status_code == 302, 'Admin login should redirect to dashboard'

# 10 Admin login without CSRF -> 403
assert client.post('/login?role=admin', data={'username':'admin','password':'My_portofolio'}).status_code == 403, 'Admin login without CSRF should be 403'

# 11 Dashboard after admin login (200)
assert client.get('/admin/').status_code == 200, 'Dashboard after admin login should be accessible'

# 12 Contact without CSRF -> 403
assert client.post('/contact', data={'name':'a','email':'a@b.com','subject':'s','message':'m'}).status_code == 403, 'Contact without CSRF should be 403'

# 13 Contact with CSRF -> redirect (302)
with client.session_transaction() as sess:
    set_csrf(sess)
assert client.post('/contact', data={'name':'a','email':'a@b.com','subject':'s','message':'m','_csrf_token':'testtoken'}).status_code == 302, 'Contact with CSRF should redirect'

# 14 Rate limiting test omitted (no limiter on unified admin login route)

print("All tests passed!")