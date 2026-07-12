from datetime import datetime, timezone
from models import db


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    headline = db.Column(db.String(200))
    about = db.Column(db.Text)
    photo = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    github_url = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    gmail = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
