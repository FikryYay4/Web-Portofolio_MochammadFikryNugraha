import re


def validate_contact(name, email, subject, message):
    errors = []
    if not name or len(name.strip()) < 2:
        errors.append('Name must be at least 2 characters.')
    if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        errors.append('Valid email is required.')
    if not subject or len(subject.strip()) < 3:
        errors.append('Subject must be at least 3 characters.')
    if not message or len(message.strip()) < 10:
        errors.append('Message must be at least 10 characters.')
    return errors


def validate_project(title, description):
    errors = []
    if not title or len(title.strip()) < 2:
        errors.append('Title must be at least 2 characters.')
    if not description or len(description.strip()) < 10:
        errors.append('Description must be at least 10 characters.')
    return errors
