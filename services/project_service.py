from models import db, Project


def get_all_projects():
    return Project.query.order_by(Project.order, Project.id.desc()).all()


def get_project(project_id):
    return Project.query.get_or_404(project_id)


def create_project(data):
    project = Project(**data)
    db.session.add(project)
    db.session.commit()
    return project


def update_project(project_id, data):
    project = Project.query.get_or_404(project_id)
    for key, value in data.items():
        setattr(project, key, value)
    db.session.commit()
    return project


def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
