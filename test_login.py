from app import create_app
import re

app = create_app()
with app.test_client() as client:
    # First get login page to get CSRF token
    r = client.get('/login')
    print('Login page:', r.status_code)
    
    # Extract CSRF token from the page
    csrf_match = re.search(r'name="_csrf_token" value="([^"]+)"', r.get_data(as_text=True))
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print('CSRF token:', csrf_token[:20] + '...')
        
        # Now try login with CSRF token, using same client (session persists)
        r = client.post('/login', data={'username':'admin','password':'admin123','role':'admin','_csrf_token':csrf_token}, follow_redirects=True)
        print('Login:', r.status_code)
        print('Login redirect location:', r.location if hasattr(r, 'location') else 'N/A')
        
        # Test admin pages
        r = client.get('/admin/skills')
        print('Skills page:', r.status_code)
        
        r = client.get('/admin/certificates')
        print('Certificates page:', r.status_code)
        
        r = client.get('/admin/projects')
        print('Projects page:', r.status_code)
    else:
        print('No CSRF token found')