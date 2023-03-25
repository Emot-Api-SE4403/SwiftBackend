import datetime
from sqlalchemy.orm import Session

import models, schema, auth

def read_user_by_email(db: Session, email:str):
    return db.query(models.User).filter(models.User.email == email).first()

def read_user_by_id_filter_activation_code(db: Session, id, code):
    return db.query(models.User).filter(models.User.id == id, models.User.activation_code == code).one()

def update_user_is_active_by_id(db: Session, id):
    db_user = db.query(models.User).filter(models.User.id == id).one()
    db_user.is_active = True
    db_user.time_updated = datetime.datetime.now()
    db.add(db_user)
    db.commit()
    return "done"

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

def update_user_pelajar_toggle_is_member_by_email(db: Session, user_email: str):
    db_pelajar = db.query(models.Pelajar).filter(models.Pelajar.email == user_email).one()
    db_pelajar.is_member = not db_pelajar.is_member
    db_pelajar.time_updated = datetime.datetime.now()
    db.add(db_pelajar)
    db.commit()
    return "success"

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
    db.refresh(db_admin)
    return "done"

def read_admin_by_id(db: Session, admin_id: str):
    return db.query(models.Admin).filter(models.Admin.id==admin_id).first()
