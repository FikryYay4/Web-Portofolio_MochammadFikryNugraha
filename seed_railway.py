# seed_railway.py
# Jalankan di Railway shell: railway run python seed_railway.py
# Atau di Railway Dashboard → Shell → python seed_railway.py

import os
os.environ.setdefault('FLASK_DEBUG', 'false')

from app import create_app
from models import db, Profile, Skill, Project

app = create_app()

with app.app_context():
    # Cek sudah ada data?
    if Profile.query.first():
        print("⚠️  Data sudah ada, skip seed")
        exit()

    print("🌱 Seeding data awal...")

    # 1. Profile
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
    print("  ✅ Profile")

    # 2. Skills
    skills = [
        Skill(
            name='Programming',
            icon='programming/python-svgrepo-com.svg',
            description='Pengembangan aplikasi web full-stack dan software engineering.',
            software='VS Code, Python, Apache NetBeans, Android Studio',
            certificates='Sertifikat Pemrograman (In Study)',
            order=1
        ),
        Skill(
            name='Data Analyst',
            icon='data-analyst/google-bigquery.svg',
            description='Analisis data, visualisasi, dan pengambilan keputusan berbasis data. Kemampuan bahasa Inggris profesional.',
            software='Excel, Google BigQuery, Looker Studio, Python',
            certificates='Sertifikat TOEFL, Sertifikat TOEIC, Sertifikat Data Analyst KarirNext 2026',
            order=2
        ),
        Skill(
            name='Graphic Design',
            icon='graphic-design/adobe-photoshop-svgrepo-com.svg',
            description='Desain grafis kreatif untuk media sosial dan promosi.',
            software='Adobe Photoshop, Adobe Illustrator',
            certificates='BNSP Graphic Design, Sertifikat Graphic Design Telkom',
            order=3
        ),
        Skill(
            name='Video Editor',
            icon='video-editor/adobe-premiere-svgrepo-com.svg',
            description='Pengeditan video profesional dan motion graphics.',
            software='Adobe Premiere Pro, Adobe After Effects',
            certificates='Sertifikat Video Editing & Motion Graphics',
            order=4
        ),
        Skill(
            name='Network Engineering',
            icon='programming/DeviconAndroidstudio.svg',
            description='Desain, konfigurasi, dan troubleshooting infrastruktur jaringan.',
            software='Cisco Packet Tracer, Mikrotik RouterOS',
            certificates='BNSP Network Engineering',
            order=5
        ),
    ]
    db.session.add_all(skills)
    print(f"  ✅ {len(skills)} Skills")

    # 3. Projects (thumbnail diupload manual nanti via /admin)
    projects = [
        Project(
            title='Network Architecture Blueprint',
            description='Desain infrastruktur jaringan skala menengah. Status: Coming soon / In study.',
            technology='Cisco Packet Tracer, GNS3',
            thumbnail=None,  # upload manual
            category='Network Engineering',
            year=2025,
            order=1
        ),
        Project(
            title='Enterprise Web Application',
            description='Aplikasi manajemen sistem enterprise berbasis Python Flask. Status: Coming soon / In study.',
            technology='Flask, Python, SQLite',
            thumbnail=None,
            category='Programming',
            year=2025,
            order=2
        ),
        Project(
            title='Creative AI Video Editing',
            description='Bahan pembuatan video dibuat dengan AI, Design_Graphic. Mengintegrasikan generative media dengan visual motion premium.',
            technology='Premiere Pro, After Effects, Runway AI',
            thumbnail=None,
            category='Video Editor',
            year=2026,
            order=3
        ),
        Project(
            title='Iklan Parfum Aerostreet Bundling',
            description='Video iklan kreatif untuk produk Aerostreet dengan teknik bundling visual dan motion graphics.',
            technology='Premiere Pro, After Effects',
            thumbnail=None,
            category='Video Editor',
            year=2026,
            order=4
        ),
        Project(
            title='Clip Ferry',
            description='Video klip pendek Ferry dengan efek transisi creative dan color grading.',
            technology='Premiere Pro, After Effects',
            thumbnail=None,
            category='Video Editor',
            year=2026,
            order=5
        ),
        Project(
            title='Ultra Realistic Luxury Visual',
            description='Create an ultra realistic luxury visual menggunakan generative AI dan compositing.',
            technology='Runway AI, Premiere Pro, After Effects',
            thumbnail=None,
            category='Video Editor',
            year=2026,
            order=6
        ),
        Project(
            title='Data Analyst - Excel Dashboard',
            description='Dashboard analisis data menggunakan Microsoft Excel dengan visualisasi pivot table dan chart.',
            technology='Microsoft Excel',
            thumbnail=None,
            category='Data Analyst',
            year=2026,
            order=7
        ),
        Project(
            title='Data Analyst - Google BigQuery',
            description='Analisis data skala besar menggunakan Google BigQuery dengan query SQL kompleks.',
            technology='Google BigQuery, SQL',
            thumbnail=None,
            category='Data Analyst',
            year=2026,
            order=8
        ),
        Project(
            title='Data Analyst - Looker Studio',
            description='Visualisasi data interaktif menggunakan Google Looker Studio dengan dashboard real-time.',
            technology='Google Looker Studio',
            thumbnail=None,
            category='Data Analyst',
            year=2026,
            order=9
        ),
        Project(
            title='Design Graphic Portfolio #1',
            description='Karya desain grafis kreatif menggunakan Adobe Photoshop dan Illustrator.',
            technology='Adobe Photoshop, Adobe Illustrator',
            thumbnail=None,
            category='Graphic Design',
            year=2026,
            order=10
        ),
        Project(
            title='Design Graphic Portfolio #2',
            description='Karya desain grafis kreatif kedua menggunakan Adobe Photoshop.',
            technology='Adobe Photoshop',
            thumbnail=None,
            category='Graphic Design',
            year=2026,
            order=11
        ),
        Project(
            title='Design Graphic Portfolio #3',
            description='Karya desain grafis kreatif ketiga dengan teknik typography dan layout.',
            technology='Adobe Photoshop, Adobe Illustrator',
            thumbnail=None,
            category='Graphic Design',
            year=2026,
            order=12
        ),
        Project(
            title='Design Graphic Portfolio #4',
            description='Karya desain grafis keempat dengan fokus branding dan identitas visual.',
            technology='Adobe Photoshop',
            thumbnail=None,
            category='Graphic Design',
            year=2026,
            order=13
        ),
    ]
    db.session.add_all(projects)
    print(f"  ✅ {len(projects)} Projects (thumbnail upload manual via /admin)")

    db.session.commit()
    print("\n🎉 Seed berhasil! Data profil, skills, projects siap.")
    print("📝 Next: Login /admin → upload sertifikat, foto profil, thumbnail project")

if __name__ == '__main__':
    pass