from datetime import datetime, timezone
from models import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    technology = db.Column(db.String(500))
    thumbnail = db.Column(db.String(200))
    link_demo = db.Column(db.String(200))
    link_github = db.Column(db.String(200))
    category = db.Column(db.String(50))
    year = db.Column(db.Integer)
    featured = db.Column(db.Boolean, default=False)
    is_hidden = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    images = db.relationship(
        'ProjectImage',
        backref='project',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='ProjectImage.order'
    )

    @property
    def all_images(self):
        result = []
        if self.thumbnail:
            result.append(self.thumbnail)
        for img in self.images:
            if img.filename != self.thumbnail:
                result.append(img.filename)
        return result
