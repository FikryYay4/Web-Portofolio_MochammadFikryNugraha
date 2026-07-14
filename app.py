from flask import Flask
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
load_dotenv()
from config import Config
from models import db


def create_app():
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Vercel output directory structure: templates/ and static/ are in .vercel/output/
    template_dir = os.path.join(BASE_DIR, '.vercel', 'output', 'templates')
    static_dir = os.path.join(BASE_DIR, '.vercel', 'output', 'static')
    # Fallback to local development paths
    if not os.path.isdir(template_dir):
        template_dir = os.path.join(BASE_DIR, 'templates')
    if not os.path.isdir(static_dir):
        static_dir = os.path.join(BASE_DIR, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

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
        seed_data()

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
                description='Desain infrastruktur jaringan skala menengah. Status: Coming soon / In study.',
                technology='Cisco Packet Tracer, GNS3', thumbnail='projects/nw_arch.jpg', category='Network Engineering', year=2025, order=1),
        Project(title='Enterprise Web Application',
                description='Aplikasi manajemen sistem enterprise berbasis Python Flask. Status: Coming soon / In study.',
                technology='Flask, Python, SQLite', thumbnail='projects/enterprise_web.jpg', category='Programming', year=2025, order=2),
        Project(title='Creative AI Video Editing',
                description='Bahan pembuatan video dibuat dengan AI, Design_Graphic. Mengintegrasikan generative media dengan visual motion premium.',
                technology='Premiere Pro, After Effects, Runway AI', thumbnail='projects/WhatsApp Video 2026-07-10 at 17.17.06.mp4', category='Video Editor', year=2026, order=3),
        Project(title='Iklan Parfum Aerostreet Bundling',
                description='Video iklan kreatif untuk produk Aerostreet dengan teknik bundling visual dan motion graphics.',
                technology='Premiere Pro, After Effects', thumbnail='projects/Iklan_Parfum_Aerostreet_Bundling.mp4', category='Video Editor', year=2026, order=4),
        Project(title='Clip Ferry',
                description='Video klip pendek Ferry dengan efek transisi creative dan color grading.',
                technology='Premiere Pro, After Effects', thumbnail='projects/Clip Ferry.mp4', category='Video Editor', year=2026, order=5),
        Project(title='Ultra Realistic Luxury Visual',
                description='Create an ultra realistic luxury visual menggunakan generative AI dan compositing.',
                technology='Runway AI, Premiere Pro, After Effects', thumbnail='projects/Create_an_ultra_realistic_luxu.mp4', category='Video Editor', year=2026, order=6),
        Project(title='Data Analyst - Excel Dashboard',
                description='Dashboard analisis data menggunakan Microsoft Excel dengan visualisasi pivot table dan chart.',
                technology='Microsoft Excel', thumbnail='projects/WhatsApp Image 2026-07-10 at 17.54.35.jpeg', category='Data Analyst', year=2026, order=7),
        Project(title='Data Analyst - Google BigQuery',
                description='Analisis data skala besar menggunakan Google BigQuery dengan query SQL kompleks.',
                technology='Google BigQuery, SQL', thumbnail='projects/WhatsApp Image 2026-07-10 at 17.57.52.jpeg', category='Data Analyst', year=2026, order=8),
        Project(title='Data Analyst - Looker Studio',
                description='Visualisasi data interaktif menggunakan Google Looker Studio dengan dashboard real-time.',
                technology='Google Looker Studio', thumbnail='projects/WhatsApp Image 2026-07-10 at 17.52.24.jpeg', category='Data Analyst', year=2026, order=9),
        Project(title='Design Graphic Portfolio #1',
                description='Karya desain grafis kreatif menggunakan Adobe Photoshop dan Illustrator.',
                technology='Adobe Photoshop, Adobe Illustrator', thumbnail='projects/WhatsApp Image 2026-07-10 at 17.33.38.jpeg', category='Graphic Design', year=2026, order=10),
        Project(title='Design Graphic Portfolio #2',
                description='Karya desain grafis kreatif kedua menggunakan Adobe Photoshop.',
                technology='Adobe Photoshop', thumbnail='projects/WhatsApp Image 2026-07-10 at 17.33.39.jpeg', category='Graphic Design', year=2026, order=11),
        Project(title='Design Graphic Portfolio #3',
                description='Karya desain grafis kreatif ketiga dengan teknik typography dan layout.',
                technology='Adobe Photoshop, Adobe Illustrator', thumbnail='projects/WhatsApp Image 2026-07-10 at 17.34.16.jpeg', category='Graphic Design', year=2026, order=12),
        Project(title='Design Graphic Portfolio #4',
                description='Karya desain grafis keempat dengan fokus branding dan identitas visual.',
                technology='Adobe Photoshop', thumbnail='projects/WhatsApp Image 2026-07-10 at 17.35.08.jpeg', category='Graphic Design', year=2026, order=13),
    ]
    db.session.add_all(projects)
    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config.get('DEBUG', False))