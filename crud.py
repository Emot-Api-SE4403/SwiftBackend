from sqlalchemy.orm import Session

import models, schema, auth


def get_user_mentor_by_email(db: Session, email: str):
    return db.query(models.Mentor).filter(models.Mentor.email == email).first()

def get_user_mentor_by_id(db: Session, user_id: int):
    return db.query(models.Mentor).filter(models.Mentor.id == user_id).first()

def create_user_mentor(db: Session, user: schema.MentorRegisterForm):
    fake_hashed_password = auth.get_password_hash(user.raw_password)
    db_user = models.Mentor(email=user.email, nama_lengkap=user.nama_lengkap, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user