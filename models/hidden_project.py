from models import db

class HiddenProject(db.Model):
    __tablename__ = 'hidden_projects'

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True)