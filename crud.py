from sqlalchemy.orm import Session

import models, schema, auth


def get_user_mentor_by_email(db: Session, email: str):
    return db.query(models.Mentor).filter(models.Mentor.email == email).first()

def get_user_mentor_by_id(db: Session, user_id: int):
    return db.query(models.Mentor).filter(models.Mentor.id == user_id).first()

def create_user_mentor(db: Session, user: schema.MentorRegisterForm):
    hashed_password = auth.get_password_hash(user.raw_password)
    db_user = models.User(
        email=user.email, 
        nama_lengkap=user.nama_lengkap, 
        hashed_password=hashed_password
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    db_mentor = models.Mentor(
        uid = db_user.id,
        keahlian = user.keahlian,
        asal = user.asal
    )
    db.add(db_mentor)
    db.commit()
    return "done"

def create_user_pelajar(db: Session, user: schema.PelajarRegisterForm):
    hashed_password = auth.get_password_hash(user.raw_password)
    db_user = models.User(
        email=user.email, 
        nama_lengkap=user.nama_lengkap, 
        hashed_password=hashed_password
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    db_pelajar = models.Pelajar(
        uid = db_user.id,
        asal_sekolah = user.asal_sekolah,
        jurusan = user.jurusan
    )
    db.add(db_pelajar)
    db.commit()
    return "done"