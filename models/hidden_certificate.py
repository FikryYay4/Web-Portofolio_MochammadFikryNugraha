from models import db

class HiddenCertificate(db.Model):
    __tablename__ = 'hidden_certificates'

    filename = db.Column(db.String(200), primary_key=True)
