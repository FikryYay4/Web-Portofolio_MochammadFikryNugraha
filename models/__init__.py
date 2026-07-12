from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.profile import Profile
from models.skill import Skill
from models.project import Project
from models.project_image import ProjectImage
from models.message import Message
