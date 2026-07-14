from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, Profile, Skill, Project, ProjectImage, Message
from services.auth_service import check_login, admin_required
from services.upload_service import save_file, delete_file, save_project_image, delete_project_image
from services.project_service import (
    get_all_projects, get_project, create_project, update_project, delete_project
)
from services.project_image_service import (
    get_images_for_project, create_image, delete_image, reorder_images
)
from utils.validators import validate_project
from utils.csrf import csrf_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Rate limiter for login endpoint - configured in app factory
login_limiter = Limiter(key_func=get_remote_address, default_limits=[])


@admin_bp.route('/login', methods=['GET'])
def login_redirect():
    """Redirect to the unified login page.
    If the query parameter ``auto=1`` is present, automatically log in as admin
    (useful for quick debugging or direct access links). This sets the
    ``admin_logged_in`` session flag and forwards to the admin dashboard.
    """
    if request.args.get('auto') == '1':
        session['admin_logged_in'] = True
        return redirect(url_for('admin.dashboard'))
    # Standard flow – unified login page; role will be indicated via query param
    return redirect(url_for('public.login', role='admin'))


@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('public_logged_in', None)
    session.pop('_csrf_token', None)
    return redirect(url_for('public.login'))


@admin_bp.route('/')
@admin_required
def dashboard():
    projects = get_all_projects()
    skills = Skill.query.order_by(Skill.order, Skill.id).all()
    messages = Message.query.order_by(Message.created_at.desc()).all()
    profile = Profile.query.first()
    messages_count = len(messages)
    # Count certificate files in static/uploads/certificates
    import os
    from flask import current_app
    cert_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates')
    try:
        certificates = [f for f in os.listdir(cert_dir) if os.path.isfile(os.path.join(cert_dir, f))]
        certificates_count = len(certificates)
    except Exception:
        certificates_count = 0
    return render_template('dashboard/index.html',
                           projects=projects, skills=skills,
                          messages=messages, messages_count=messages_count,
                          certificates_count=certificates_count, profile=profile)


@admin_bp.route('/profile', methods=['GET', 'POST'])
@admin_required
@csrf_required
def profile():
    profile = Profile.query.first()
    if request.method == 'POST':
        profile.name = request.form.get('name', profile.name)
        profile.headline = request.form.get('headline', profile.headline)
        profile.about = request.form.get('about', profile.about)
        profile.email = request.form.get('email', profile.email)
        profile.phone = request.form.get('phone', profile.phone)
        profile.location = request.form.get('location', profile.location)
        profile.github_url = request.form.get('github_url', profile.github_url)
        profile.linkedin_url = request.form.get('linkedin_url', profile.linkedin_url)
        profile.instagram_url = request.form.get('instagram_url', profile.instagram_url)
        profile.gmail = request.form.get('gmail', profile.gmail)

        photo = request.files.get('photo')
        if photo and photo.filename:
            if profile.photo:
                delete_file(profile.photo)
            filename = save_file(photo)
            if filename:
                profile.photo = filename

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('admin.profile'))
    return render_template('dashboard/profile.html', profile=profile)


@admin_bp.route('/projects')
@admin_required
def projects_list():
    projects = get_all_projects()
    return render_template('dashboard/projects.html', projects=projects)


@admin_bp.route('/projects/create', methods=['GET', 'POST'])
@admin_required
@csrf_required
def project_create():
    if request.method == 'POST':
        errors = validate_project(
            request.form.get('title', ''),
            request.form.get('description', '')
        )
        if errors:
            for err in errors:
                flash(err, 'error')
            return redirect(url_for('admin.project_create'))

        data = {
            'title': request.form.get('title', ''),
            'description': request.form.get('description', ''),
            'technology': request.form.get('technology', ''),
            'category': request.form.get('category', ''),
            'year': request.form.get('year', type=int),
            'featured': 'featured' in request.form,
            'order': request.form.get('order', 0, type=int),
            'link_demo': request.form.get('link_demo', ''),
            'link_github': request.form.get('link_github', ''),
        }

        thumbnail = request.files.get('thumbnail')
        if thumbnail and thumbnail.filename:
            filename = save_file(thumbnail)
            if filename:
                data['thumbnail'] = filename

        project = create_project(data)

        images = request.files.getlist('images')
        for img in images:
            if img and img.filename:
                fname = save_project_image(img)
                if fname:
                    create_image(project.id, fname)

        flash('Project created!', 'success')
        return redirect(url_for('admin.projects_list'))
    return render_template('dashboard/add_project.html', project=None)


@admin_bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@admin_required
@csrf_required
def project_edit(project_id):
    project = get_project(project_id)
    if request.method == 'POST':
        errors = validate_project(
            request.form.get('title', ''),
            request.form.get('description', '')
        )
        if errors:
            for err in errors:
                flash(err, 'error')
            return redirect(url_for('admin.project_edit', project_id=project_id))

        data = {
            'title': request.form.get('title', ''),
            'description': request.form.get('description', ''),
            'technology': request.form.get('technology', ''),
            'category': request.form.get('category', ''),
            'year': request.form.get('year', type=int),
            'featured': 'featured' in request.form,
            'order': request.form.get('order', 0, type=int),
            'link_demo': request.form.get('link_demo', ''),
            'link_github': request.form.get('link_github', ''),
        }

        thumbnail = request.files.get('thumbnail')
        if thumbnail and thumbnail.filename:
            if project.thumbnail:
                delete_file(project.thumbnail)
            filename = save_file(thumbnail)
            if filename:
                data['thumbnail'] = filename

        update_project(project_id, data)

        image_order = request.form.get('image_order', '')
        if image_order:
            try:
                ids = [int(x) for x in image_order.split(',') if x.strip()]
                reorder_images(project_id, ids)
            except ValueError:
                pass

        new_images = request.files.getlist('images')
        for img in new_images:
            if img and img.filename:
                fname = save_project_image(img)
                if fname:
                    create_image(project_id, fname)

        flash('Project updated!', 'success')
        return redirect(url_for('admin.projects_list'))
    return render_template('dashboard/edit_project.html', project=project)


@admin_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@admin_required
@csrf_required
def project_delete(project_id):
    project = get_project(project_id)
    if project.thumbnail:
        delete_file(project.thumbnail)
    for img in project.images.all():
        delete_project_image(img.filename)
    delete_project(project_id)
    flash('Project deleted!', 'success')
    return redirect(url_for('admin.projects_list'))


@admin_bp.route('/projects/<int:project_id>/images/<int:image_id>/delete', methods=['POST'])
@admin_required
@csrf_required
def project_image_delete(project_id, image_id):
    filename = delete_image(image_id)
    delete_project_image(filename)
    flash('Image deleted!', 'success')
    return redirect(url_for('admin.project_edit', project_id=project_id))


@admin_bp.route('/projects/<int:project_id>/images/reorder', methods=['POST'])
@admin_required
def project_images_reorder(project_id):
    data = request.get_json()
    if data and 'order' in data:
        reorder_images(project_id, data['order'])
        return jsonify({'ok': True})
    return jsonify({'ok': False}), 400


@admin_bp.route('/skills')
@admin_required
def skills_list():
    skills = Skill.query.order_by(Skill.order, Skill.id).all()
    return render_template('dashboard/skills.html', skills=skills, skill=None)


@admin_bp.route('/skills/create', methods=['GET', 'POST'])
@admin_required
@csrf_required
def skill_create():
    if request.method == 'POST':
        skill = Skill(
            name=request.form.get('name', ''),
            icon='',
            description=request.form.get('description', ''),
            software=request.form.get('software', ''),
            certificates=request.form.get('certificates', ''),
            year_started=request.form.get('year_started', type=int),
            order=request.form.get('order', 0, type=int),
        )
        # Handle logo upload
        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename:
            logo_name = save_file(logo_file)
            if logo_name:
                skill.icon = logo_name
        db.session.add(skill)
        db.session.commit()
        flash('Skill created!', 'success')
        return redirect(url_for('admin.skills_list'))
    return render_template('dashboard/skills.html', skill=None)


@admin_bp.route('/skills/<int:skill_id>/edit', methods=['GET', 'POST'])
@admin_required
@csrf_required
def skill_edit(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if request.method == 'POST':
        skill.name = request.form.get('name', skill.name)
        skill.icon = request.form.get('icon', skill.icon)
        skill.description = request.form.get('description', skill.description)
        skill.software = request.form.get('software', skill.software)
        skill.certificates = request.form.get('certificates', skill.certificates)
        skill.year_started = request.form.get('year_started', type=int)
        skill.order = request.form.get('order', 0, type=int)
        db.session.commit()
        flash('Skill updated!', 'success')
        return redirect(url_for('admin.skills_list'))
    return render_template('dashboard/skills.html', skill=skill)


@admin_bp.route('/skills/<int:skill_id>/delete', methods=['POST'])
@admin_required
@csrf_required
def skill_delete(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted!', 'success')
    return redirect(url_for('admin.skills_list'))


@admin_bp.route('/messages')
@admin_required
def messages_list():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    messages_count = len(messages)
    return render_template('dashboard/messages.html', messages=messages, messages_count=messages_count)


@admin_bp.route('/messages/count')
@admin_required
def messages_count_api():
    count = Message.query.count()
    return jsonify({'count': count})



@admin_bp.route('/certificates')
@admin_required
def certificates_list():
    import os
    from flask import current_app
    cert_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates')
    os.makedirs(cert_dir, exist_ok=True)
    certs = []
    for f in sorted(os.listdir(cert_dir)):
        fp = os.path.join(cert_dir, f)
        if os.path.isfile(fp):
            sz = os.path.getsize(fp)
            certs.append({'filename': f, 'size': f'{sz/1024:.1f} KB' if sz < 1048576 else f'{sz/1048576:.1f} MB'})
    return render_template('dashboard/certificates.html', certificates=certs)


@admin_bp.route('/certificates/upload', methods=['POST'])
@admin_required
@csrf_required
def certificates_upload():
    file = request.files.get('certificate')
    if file and file.filename:
        from services.upload_service import save_file
        fname = save_file(file, subfolder='certificates')
        if fname:
            flash('Certificate uploaded!', 'success')
        else:
            flash('Invalid file type.', 'error')
    else:
        flash('No file selected.', 'error')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificates/delete', methods=['POST'])
@admin_required
@csrf_required
def certificates_delete():
    fname = request.form.get('filename', '')
    if not fname:
        flash('No filename provided.', 'error')
        return redirect(url_for('admin.certificates_list'))
    import os
    from flask import current_app
    cert_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates')
    fpath = os.path.normpath(os.path.join(cert_dir, fname))
    if fpath.startswith(os.path.normpath(cert_dir)) and os.path.exists(fpath):
        os.remove(fpath)
        flash('Certificate deleted!', 'success')
    else:
        flash('File not found.', 'error')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/messages/<int:message_id>/read', methods=['POST'])
@admin_required
@csrf_required
def message_read(message_id):
    msg = Message.query.get_or_404(message_id)
    msg.is_read = True
    db.session.commit()
    return redirect(url_for('admin.messages_list'))


@admin_bp.route('/messages/<int:message_id>/delete', methods=['POST'])
@admin_required
@csrf_required
def message_delete(message_id):
    msg = Message.query.get_or_404(message_id)
    db.session.delete(msg)
    db.session.commit()
    return redirect(url_for('admin.messages_list') + '?deleted=1')