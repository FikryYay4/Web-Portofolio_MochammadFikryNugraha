from models import db, ProjectImage


def get_images_for_project(project_id):
    return ProjectImage.query.filter_by(project_id=project_id).order_by(ProjectImage.order).all()


def create_image(project_id, filename, order=None):
    if order is None:
        last = ProjectImage.query.filter_by(project_id=project_id).order_by(ProjectImage.order.desc()).first()
        order = (last.order + 1) if last else 0
    img = ProjectImage(project_id=project_id, filename=filename, order=order)
    db.session.add(img)
    db.session.commit()
    return img


def delete_image(image_id):
    img = ProjectImage.query.get_or_404(image_id)
    filename = img.filename
    db.session.delete(img)
    db.session.commit()
    return filename


def reorder_images(project_id, ordered_ids):
    for idx, img_id in enumerate(ordered_ids):
        img = ProjectImage.query.get(int(img_id))
        if img and img.project_id == project_id:
            img.order = idx
    db.session.commit()
