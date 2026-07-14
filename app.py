import os
from flask import Flask, send_from_directory, current_app
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
load_dotenv()
from config import Config
from models import db


def create_app():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Vercel: files at /var/task/ (project root)
    # Local dev: templates/, static/ at project root
    is_vercel = os.environ.get('VERCEL') == '1'
    
    if is_vercel:
        template_dir = os.path.join('/var/task', 'templates')
        static_dir = os.path.join('/var/task', 'static')
    else:
        template_dir = os.path.join(BASE_DIR, 'templates')
        static_dir = os.path.join(BASE_DIR, 'static')

    # Debug: print resolved paths (visible in Vercel function logs)
    print(f"[VERCEL DEBUG] is_vercel={is_vercel}", flush=True)
    print(f"[VERCEL DEBUG] template_dir={template_dir} exists={os.path.isdir(template_dir)}", flush=True)
    print(f"[VERCEL DEBUG] static_dir={static_dir} exists={os.path.isdir(static_dir)}", flush=True)
    print(f"[VERCEL DEBUG] BASE_DIR={BASE_DIR}", flush=True)
    print(f"[VERCEL DEBUG] cwd={os.getcwd()}", flush=True)
    print(f"[VERCEL DEBUG] VERCEL env={os.environ.get('VERCEL')}", flush=True)
    if os.path.isdir('/var/task'):
        print(f"[VERCEL DEBUG] /var/task contents: {os.listdir('/var/task')}", flush=True)
    if os.path.isdir('/var/task/templates'):
        print(f"[VERCEL DEBUG] /var/task/templates contents: {os.listdir('/var/task/templates')}", flush=True)
    else:
        print(f"[VERCEL DEBUG] /var/task/templates NOT FOUND", flush=True)

    app = Flask(__name__, template_folder=template_dir, static_folder=None)
    app.config.from_object(Config)
    app.config['STATIC_DIR'] = static_dir

    @app.route('/static/<path:filename>', endpoint='static')
    def static_from_anywhere(filename):
        static_path = os.path.join(static_dir, filename)
        if os.path.exists(static_path):
            return send_from_directory(static_dir, filename)
        upload_dir = current_app.config['UPLOAD_FOLDER']
        path_components = filename.split('/')
        if path_components and path_components[0] == 'uploads':
            filename_clean = '/'.join(path_components[1:])
        else:
            filename_clean = filename
        upload_path = os.path.join(upload_dir, filename_clean)
        if os.path.exists(upload_path):
            return send_from_directory(upload_dir, filename_clean)
        return ('Not found', 404)

    db.init_app(app)
    Migrate(app, db)

    # Rate limiter (global default)
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[],
        storage_uri='memory://',
    )
    limiter.init_app(app)

    # Init login-specific limiter from routes.admin
    from routes.admin import login_limiter
    login_limiter.init_app(app)

    # CSRF token available in all templates
    from utils.csrf import generate_csrf_token

    @app.context_processor
    def inject_csrf():
        return {'csrf_token': generate_csrf_token}

    from routes.public import public_bp
    from routes.admin import admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            cols = [c['name'] for c in inspector.get_columns('projects')]
            if 'is_hidden' not in cols:
                db.session.execute('ALTER TABLE projects ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE')
                db.session.commit()
                print('[MIGRATE] Added is_hidden to projects', flush=True)
        except Exception as e:
            print(f'[MIGRATE] is_hidden column check failed: {e}', flush=True)
        try:
            seed_data()
        except Exception as e:
            print(f'[WARN] seed_data failed: {e}', flush=True)

    return app


def seed_data():
    from models import Profile, Skill, Project

    if Profile.query.first():
        return

    profile = Profile(
        name='Mochammad Fikry Nugraha',
        headline='Programmer | Data Analyst | Graphic Designer | Video Editor',
        about='Seorang mahasiswa Teknik Informatika di Universitas Bale Bandung yang passionate di bidang pengembangan web, analisis data, desain grafis, dan editing video. Berbekal pengalaman dari SMK Telkom Bandung jurusan TJKT, kini terus mengembangkan diri di dunia teknologi informasi dengan semangat belajar dan berinovasi.',
        photo='profile.png',
        email='nugrahafikry2@gmail.com',
        phone='Belum Ditentukan',
        location='Bandung, Indonesia',
        github_url='https://github.com/FikryYay4',
        linkedin_url='https://www.linkedin.com/in/mochammad-fikry-nugraha-75636338a',
        instagram_url='https://www.instagram.com/mochammadfikryn12?igsh=N3dmOWl6bTZ0MDlq',
        gmail='nugrahafikry2@gmail.com'
    )
    db.session.add(profile)

    skills = [
        Skill(name='Programming', icon='programming/python-svgrepo-com.svg',
              description='Pengembangan aplikasi web full-stack dan software engineering.',
              software='VS Code, Python, Apache NetBeans, Android Studio',
              certificates='Sertifikat Pemrograman (In Study)', order=1),
        Skill(name='Data Analyst', icon='data-analyst/google-bigquery.svg',
              description='Analisis data, visualisasi, dan pengambilan keputusan berbasis data. Kemampuan bahasa Inggris profesional.',
              software='Excel, Google BigQuery, Looker Studio, Python',
              certificates='Sertifikat TOEFL, Sertifikat TOEIC, Sertifikat Data Analyst KarirNext 2026', order=2),
        Skill(name='Graphic Design', icon='graphic-design/adobe-photoshop-svgrepo-com.svg',
              description='Desain grafis kreatif untuk media sosial dan promosi.',
              software='Adobe Photoshop, Adobe Illustrator',
              certificates='BNSP Graphic Design, Sertifikat Graphic Design Telkom', order=3),
        Skill(name='Video Editor', icon='video-editor/adobe-premiere-svgrepo-com.svg',
              description='Pengeditan video profesional dan motion graphics.',
              software='Adobe Premiere Pro, Adobe After Effects',
              certificates='Sertifikat Video Editing & Motion Graphics', order=4),
        Skill(name='Network Engineering', icon='programming/DeviconAndroidstudio.svg',
              description='Desain, konfigurasi, dan troubleshooting infrastruktur jaringan.',
              software='Cisco Packet Tracer, Mikrotik RouterOS',
              certificates='BNSP Network Engineering', order=5),
    ]
    db.session.add_all(skills)

    projects = [
        Project(title='Network Architecture Blueprint',
                description='Desain infrastruktur jaringan skala menengah.',
                technology='Cisco Packet Tracer, GNS3', thumbnail='nw_arch.jpg', category='Network Engineering', year=2025, order=1),
        Project(title='Enterprise Web Application',
                description='Aplikasi manajemen sistem enterprise berbasis Python Flask.',
                technology='Flask, Python, SQLite', thumbnail='enterprise_web.jpg', category='Programming', year=2025, order=2),
        Project(title='Creative AI Video Editing',
                description='Bahan pembuatan video dibuat dengan AI, Design_Graphic. Mengintegrasikan generative media dengan visual motion premium.',
                technology='Premiere Pro, After Effects, Runway AI', thumbnail='video_edit.jpg', category='Video Editor', year=2026, order=3),
        Project(title='Iklan Parfum Aerostreet Bundling',
                description='Video iklan kreatif untuk produk Aerostreet dengan teknik bundling visual dan motion graphics.',
                technology='Premiere Pro, After Effects', thumbnail='video_edit.jpg', category='Video Editor', year=2026, order=4),
        Project(title='Clip Ferry',
                description='Video klip pendek Ferry dengan efek transisi creative dan color grading.',
                technology='Premiere Pro, After Effects', thumbnail='video_edit.jpg', category='Video Editor', year=2026, order=5),
        Project(title='Ultra Realistic Luxury Visual',
                description='Create an ultra realistic luxury visual menggunakan generative AI dan compositing.',
                technology='Runway AI, Premiere Pro, After Effects', thumbnail='video_edit.jpg', category='Video Editor', year=2026, order=6),
        Project(title='Data Analyst - Excel Dashboard',
                description='Dashboard analisis data menggunakan Microsoft Excel dengan visualisasi pivot table dan chart.',
                technology='Microsoft Excel', thumbnail='projects/excel.jpg', category='Data Analyst', year=2026, order=7),
        Project(title='Data Analyst - Google BigQuery',
                description='Analisis data skala besar menggunakan Google BigQuery dengan query SQL kompleks.',
                technology='Google BigQuery, SQL', thumbnail='projects/bigquery.jpg', category='Data Analyst', year=2026, order=8),
        Project(title='Data Analyst - Looker Studio',
                description='Visualisasi data interaktif menggunakan Google Looker Studio dengan dashboard real-time.',
                technology='Google Looker Studio', thumbnail='projects/looker.jpg', category='Data Analyst', year=2026, order=9),
        Project(title='Design Graphic Portfolio #1',
                description='Karya desain grafis kreatif menggunakan Adobe Photoshop dan Illustrator.',
                technology='Adobe Photoshop, Adobe Illustrator', thumbnail='projects/design1.jpg', category='Graphic Design', year=2026, order=10),
        Project(title='Design Graphic Portfolio #2',
                description='Karya desain grafis kreatif kedua menggunakan Adobe Photoshop.',
                technology='Adobe Photoshop', thumbnail='projects/design2.jpg', category='Graphic Design', year=2026, order=11),
        Project(title='Design Graphic Portfolio #3',
                description='Karya desain grafis kreatif ketiga dengan teknik typography dan layout.',
                technology='Adobe Photoshop, Adobe Illustrator', thumbnail='projects/design3.jpg', category='Graphic Design', year=2026, order=12),
        Project(title='Design Graphic Portfolio #4',
                description='Karya desain grafis keempat dengan fokus branding dan identitas visual.',
                technology='Adobe Photoshop', thumbnail='projects/design4.jpg', category='Graphic Design', year=2026, order=13),
    ]
    db.session.add_all(projects)
    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config.get('DEBUG', False))