#!/usr/bin/env python3
"""
Seed script for Railway deployment.
Run: railway run python seed_railway.py
Or in Railway shell: python seed_railway.py

This script seeds:
- Profile (name, headline, about, contacts)
- 5 Skills with icons, descriptions, software, certificates
- 13 Projects (thumbnails null - upload manually via /admin)
- Note: Certificates, profile photo, project thumbnails must be uploaded manually via /admin after deploy
"""

import os
import sys

# Ensure we're in the right directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('FLASK_DEBUG', 'false')

from app import create_app
from models import db, Profile, Skill, Project, ProjectImage, Message

app = create_app()

# ============================================================
# DATA DEFINITIONS
# ============================================================

PROFILE_DATA = {
    'name': 'Mochammad Fikry Nugraha',
    'headline': 'Programmer | Data Analyst | Graphic Designer | Video Editor',
    'about': (
        'Seorang mahasiswa Teknik Informatika di Universitas Bale Bandung yang passionate di bidang '
        'pengembangan web, analisis data, desain grafis, dan editing video. Berbekal pengalaman dari '
        'SMK Telkom Bandung jurusan TJKT, kini terus mengembangkan diri di dunia teknologi informasi '
        'dengan semangat belajar dan berinovasi.'
    ),
    'photo': 'profile.png',  # Upload manual via /admin
    'email': 'nugrahafikry2@gmail.com',
    'phone': 'Belum Ditentukan',
    'location': 'Bandung, Indonesia',
    'github_url': 'https://github.com/FikryYay4',
    'linkedin_url': 'https://www.linkedin.com/in/mochammad-fikry-nugraha-75636338a',
    'instagram_url': 'https://www.instagram.com/mochammadfikryn12?igsh=N3dmOWl6bTZ0MDlq',
    'gmail': 'nugrahafikry2@gmail.com',
}

SKILLS_DATA = [
    {
        'name': 'Programming',
        'icon': 'programming/python-svgrepo-com.svg',
        'description': 'Pengembangan aplikasi web full-stack dan software engineering.',
        'software': 'VS Code, Python, Apache NetBeans, Android Studio',
        'certificates': 'Sertifikat Pemrograman (In Study)',
        'order': 1,
    },
    {
        'name': 'Data Analyst',
        'icon': 'data-analyst/google-bigquery.svg',
        'description': 'Analisis data, visualisasi, dan pengambilan keputusan berbasis data. Kemampuan bahasa Inggris profesional.',
        'software': 'Excel, Google BigQuery, Looker Studio, Python',
        'certificates': 'Sertifikat TOEFL, Sertifikat TOEIC, Sertifikat Data Analyst KarirNext 2026',
        'order': 2,
    },
    {
        'name': 'Graphic Design',
        'icon': 'graphic-design/adobe-photoshop-svgrepo-com.svg',
        'description': 'Desain grafis kreatif untuk media sosial dan promosi.',
        'software': 'Adobe Photoshop, Adobe Illustrator',
        'certificates': 'BNSP Graphic Design, Sertifikat Graphic Design Telkom',
        'order': 3,
    },
    {
        'name': 'Video Editor',
        'icon': 'video-editor/adobe-premiere-svgrepo-com.svg',
        'description': 'Pengeditan video profesional dan motion graphics.',
        'software': 'Adobe Premiere Pro, Adobe After Effects',
        'certificates': 'Sertifikat Video Editing & Motion Graphics',
        'order': 4,
    },
    {
        'name': 'Network Engineering',
        'icon': 'programming/DeviconAndroidstudio.svg',
        'description': 'Desain, konfigurasi, dan troubleshooting infrastruktur jaringan.',
        'software': 'Cisco Packet Tracer, Mikrotik RouterOS',
        'certificates': 'BNSP Network Engineering',
        'order': 5,
    },
]

PROJECTS_DATA = [
    {
        'title': 'Network Architecture Blueprint',
        'description': 'Desain infrastruktur jaringan skala menengah. Status: Coming soon / In study.',
        'technology': 'Cisco Packet Tracer, GNS3',
        'thumbnail': None,
        'category': 'Network Engineering',
        'year': 2025,
        'order': 1,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Enterprise Web Application',
        'description': 'Aplikasi manajemen sistem enterprise berbasis Python Flask. Status: Coming soon / In study.',
        'technology': 'Flask, Python, SQLite',
        'thumbnail': None,
        'category': 'Programming',
        'year': 2025,
        'order': 2,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Creative AI Video Editing',
        'description': 'Bahan pembuatan video dibuat dengan AI, Design_Graphic. Mengintegrasikan generative media dengan visual motion premium.',
        'technology': 'Premiere Pro, After Effects, Runway AI',
        'thumbnail': None,
        'category': 'Video Editor',
        'year': 2026,
        'order': 3,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Iklan Parfum Aerostreet Bundling',
        'description': 'Video iklan kreatif untuk produk Aerostreet dengan teknik bundling visual dan motion graphics.',
        'technology': 'Premiere Pro, After Effects',
        'thumbnail': None,
        'category': 'Video Editor',
        'year': 2026,
        'order': 4,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Clip Ferry',
        'description': 'Video klip pendek Ferry dengan efek transisi creative dan color grading.',
        'technology': 'Premiere Pro, After Effects',
        'thumbnail': None,
        'category': 'Video Editor',
        'year': 2026,
        'order': 5,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Ultra Realistic Luxury Visual',
        'description': 'Create an ultra realistic luxury visual menggunakan generative AI dan compositing.',
        'technology': 'Runway AI, Premiere Pro, After Effects',
        'thumbnail': None,
        'category': 'Video Editor',
        'year': 2026,
        'order': 6,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Data Analyst - Excel Dashboard',
        'description': 'Dashboard analisis data menggunakan Microsoft Excel dengan visualisasi pivot table dan chart.',
        'technology': 'Microsoft Excel',
        'thumbnail': None,
        'category': 'Data Analyst',
        'year': 2026,
        'order': 7,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Data Analyst - Google BigQuery',
        'description': 'Analisis data skala besar menggunakan Google BigQuery dengan query SQL kompleks.',
        'technology': 'Google BigQuery, SQL',
        'thumbnail': None,
        'category': 'Data Analyst',
        'year': 2026,
        'order': 8,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Data Analyst - Looker Studio',
        'description': 'Visualisasi data interaktif menggunakan Google Looker Studio dengan dashboard real-time.',
        'technology': 'Google Looker Studio',
        'thumbnail': None,
        'category': 'Data Analyst',
        'year': 2026,
        'order': 9,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Design Graphic Portfolio #1',
        'description': 'Karya desain grafis kreatif menggunakan Adobe Photoshop dan Illustrator.',
        'technology': 'Adobe Photoshop, Adobe Illustrator',
        'thumbnail': None,
        'category': 'Graphic Design',
        'year': 2026,
        'order': 10,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Design Graphic Portfolio #2',
        'description': 'Karya desain grafis kreatif kedua menggunakan Adobe Photoshop.',
        'technology': 'Adobe Photoshop',
        'thumbnail': None,
        'category': 'Graphic Design',
        'year': 2026,
        'order': 11,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Design Graphic Portfolio #3',
        'description': 'Karya desain grafis kreatif ketiga dengan teknik typography dan layout.',
        'technology': 'Adobe Photoshop, Adobe Illustrator',
        'thumbnail': None,
        'category': 'Graphic Design',
        'year': 2026,
        'order': 12,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
    {
        'title': 'Design Graphic Portfolio #4',
        'description': 'Karya desain grafis keempat dengan fokus branding dan identitas visual.',
        'technology': 'Adobe Photoshop',
        'thumbnail': None,
        'category': 'Graphic Design',
        'year': 2026,
        'order': 13,
        'link_demo': '',
        'link_github': '',
        'images': [],
    },
]


def seed_profile():
    """Create or update profile."""
    profile = Profile.query.first()
    if profile:
        print('  Profile already exists, updating...')
        for key, value in PROFILE_DATA.items():
            setattr(profile, key, value)
    else:
        print('  Creating profile...')
        profile = Profile(**PROFILE_DATA)
        db.session.add(profile)
    db.session.flush()
    return profile


def seed_skills():
    """Create skills."""
    count = 0
    for skill_data in SKILLS_DATA:
        skill = Skill.query.filter_by(name=skill_data['name']).first()
        if skill:
            print(f'  Skill "{skill_data["name"]}" exists, updating...')
            for key, value in skill_data.items():
                setattr(skill, key, value)
        else:
            print(f'  Creating skill: {skill_data["name"]}')
            skill = Skill(**skill_data)
            db.session.add(skill)
        count += 1
    db.session.flush()
    return count


def seed_projects():
    """Create projects."""
    count = 0
    for proj_data in PROJECTS_DATA:
        project = Project.query.filter_by(title=proj_data['title']).first()
        if project:
            print(f'  Project "{proj_data["title"]}" exists, updating...')
            for key, value in proj_data.items():
                if key != 'images':
                    setattr(project, key, value)
        else:
            print(f'  Creating project: {proj_data["title"]}')
            project = Project(
                title=proj_data['title'],
                description=proj_data['description'],
                technology=proj_data['technology'],
                thumbnail=proj_data['thumbnail'],
                category=proj_data['category'],
                year=proj_data['year'],
                order=proj_data['order'],
                link_demo=proj_data['link_demo'],
                link_github=proj_data['link_github'],
            )
            db.session.add(project)
            db.session.flush()

        # Handle project images (currently empty for all)
        images_data = proj_data.get('images', [])
        if images_data:
            # Clear existing images
            for img in project.images:
                db.session.delete(img)
            # Add new images
            for idx, img_data in enumerate(images_data):
                img = ProjectImage(
                    project_id=project.id,
                    filename=img_data['filename'],
                    order=img_data.get('order', idx),
                )
                db.session.add(img)

        count += 1
    db.session.flush()
    return count


def main():
    print('=' * 60)
    print('🌱 RAILWAY SEED SCRIPT')
    print('=' * 60)

    with app.app_context():
        # Create tables if not exist
        print('\n📦 Creating tables...')
        db.create_all()
        print('  ✓ Tables ready')

        # Seed data
        print('\n👤 Seeding Profile...')
        seed_profile()

        print('\n🛠️  Seeding Skills...')
        skill_count = seed_skills()

        print('\n📁 Seeding Projects...')
        project_count = seed_projects()

        # Commit all
        print('\n💾 Committing to database...')
        db.session.commit()

        print('\n' + '=' * 60)
        print('✅ SEED COMPLETED SUCCESSFULLY!')
        print('=' * 60)
        print(f'  • Profile: 1')
        print(f'  • Skills: {skill_count}')
        print(f'  • Projects: {project_count}')
        print('\n📋 NEXT STEPS (manual via /admin):')
        print('  1. Login to /admin with ADMIN_PASSWORD')
        print('  2. Profile → Upload profile photo (profile.png)')
        print('  3. Projects → Edit each → Upload thumbnail')
        print('  4. Certificates → Upload 12 certificate files')
        print('  5. Projects → Edit → Upload additional images if needed')
        print('\n🔗 Admin URL: https://your-app.up.railway.app/admin')
        print('=' * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)