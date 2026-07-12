from datetime import datetime, timezone
from models import db


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(200))
    description = db.Column(db.Text)
    software = db.Column(db.String(500))
    certificates = db.Column(db.Text)
    year_started = db.Column(db.Integer)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
