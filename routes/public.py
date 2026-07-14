from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from models import db, Profile, Skill, Project, Message
from utils.validators import validate_contact
from utils.csrf import csrf_required
from services.auth_service import login_required

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
@login_required
def home():
    profile = Profile.query.first()
    skills = Skill.query.order_by(Skill.order, Skill.id).all()
    projects = Project.query.order_by(Project.order, Project.id.desc()).all()
    project_count = Project.query.count()
    skill_count = Skill.query.count()
    return render_template('pages/home.html', profile=profile, skills=skills,
                           projects=projects, project_count=project_count,
                           skill_count=skill_count)

@public_bp.route('/contact', methods=['POST'])
@csrf_required
def contact():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()

    errors = validate_contact(name, email, subject, message)
    if errors:
        for err in errors:
            flash(err, 'error')
        return redirect(url_for('public.home') + '#contact')

    msg = Message(name=name, email=email, subject=subject, message=message)
    db.session.add(msg)
    db.session.commit()
    flash('Message sent successfully!', 'success')
    return redirect(url_for('public.home') + '#contact')

@public_bp.route('/login', methods=['GET', 'POST'])
@csrf_required
def login():
    role = request.args.get('role', 'public')
    if request.method == 'POST':
        # role may be submitted via hidden field
        role = request.form.get('role') or role
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if role == 'admin':
            cfg_user = current_app.config.get('ADMIN_USERNAME')
            cfg_pass = current_app.config.get('ADMIN_PASSWORD')
            if username == cfg_user and password == cfg_pass:
                session['admin_logged_in'] = True
                flash('Admin login successful', 'success')
                return redirect(url_for('admin.dashboard'))
        else:
            cfg_user = current_app.config.get('PUBLIC_USERNAME')
            cfg_pass = current_app.config.get('PUBLIC_PASSWORD')
            if username == cfg_user and password == cfg_pass:
                session['public_logged_in'] = True
                flash('Public login successful', 'success')
                return redirect(url_for('public.home'))
        flash('Invalid credentials', 'error')
    return render_template('pages/login.html', role=role)

@public_bp.route('/logout')
def logout():
    session.pop('public_logged_in', None)
    session.pop('admin_logged_in', None)
    return redirect(url_for('public.home'))
