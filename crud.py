from sqlalchemy.orm import Session

import models, schema, auth

def read_user_by_email(db: Session, email:str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user_mentor(db: Session, user: schema.MentorRegisterForm):
    hashed_password = auth.get_password_hash(user.raw_password)
    db_mentor = models.Mentor(
        email=user.email, 
        nama_lengkap=user.nama_lengkap, 
        hashed_password=hashed_password,
        keahlian = user.keahlian,
        Asal = user.asal
    )
    db.add(db_mentor)
    db.commit()
    return "done"

def read_user_mentor_by_id(db: Session, user_id: int):
    
    return db.query(models.Mentor).filter(models.Mentor.uid == user_id).first()

def create_user_pelajar(db: Session, user: schema.PelajarRegisterForm):
    hashed_password = auth.get_password_hash(user.raw_password)
    db_pelajar = models.Pelajar(
        email=user.email, 
        nama_lengkap=user.nama_lengkap, 
        hashed_password=hashed_password,
        asal_sekolah = user.asal_sekolah,
        jurusan = user.jurusan
    )
    db.add(db_pelajar)
    db.commit()
    return "done"

def read_user_pelajar_by_id(db: Session, user_id: int):
    return db.query(models.Pelajar).filter(models.Pelajar.uid == user_id).first()


def create_new_admin(db: Session, user: schema.AdminRegisterForm, parent: str):
    hashed_password = auth.get_password_hash(user.new_password)
    db_admin = models.Admin(
        id = user.id,
        nama_lengkap = user.nama_lengkap,
        hashed_password = hashed_password,
        created_by = parent
    )
    db.add(db_admin)
    db.commit()
    db.refresh()
    return "done"

def read_admin_by_id(db: Session, admin_id: str):
    return db.query(models.Admin).filter(models.Admin.id==admin_id).first()
