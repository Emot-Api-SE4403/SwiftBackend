from datetime import datetime
from typing import Union
import secrets
from fastapi import UploadFile
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from database import s3

import models, schema, auth


load_dotenv()
DOMAIN_URL = os.getenv("DOMAIN")


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

def update_user_password_by_email(db: Session, db_user: models.User, newPassword: str):
    db_user.hashed_password = auth.get_password_hash(newPassword)
    db_user.time_updated = datetime.datetime.now()
    db.add(db_user)
    db.commit()
    return "done"

def update_user_password_by_temp_password(db: Session, email: str):
    user = read_user_by_email(db, email)
    if not user:
        raise Exception("Wrong email or User not found")

    if not user.is_active:
        raise Exception("Mohon aktifkan akun anda terlebih dahulu")

    temp_password = secrets.token_hex(8)[:8]
    user.hashed_password = auth.get_password_hash(temp_password)
    user.time_updated = datetime.datetime.now()
    db.add(user)
    db.commit()

    # TODO send notification of new password to user
    print(temp_password)
    return "done"

def create_user_mentor(db: Session, user: schema.MentorRegisterForm):
    hashed_password = auth.get_password_hash(user.raw_password)
    activation_code = secrets.token_urlsafe(4)
    
    
    db_mentor = models.Mentor(
        email=user.email, 
        nama_lengkap=user.nama_lengkap, 
        hashed_password=hashed_password,
        activation_code = activation_code,
        keahlian = user.keahlian,
        Asal = user.asal
    )
    db.add(db_mentor)
    db.commit()
    db.refresh(db_mentor)

    activation_string = DOMAIN_URL + "/user/aktivasi?id=" + str(db_mentor.id) + "&otp=" + activation_code
    # TODO Send mail with verification code
    print(activation_string)
    return "done"

def read_user_mentor_by_id(db: Session, user_id: int):
    
    return db.query(models.Mentor).filter(models.Mentor.uid == user_id).one()

def create_user_pelajar(db: Session, user: schema.PelajarRegisterForm):
    hashed_password = auth.get_password_hash(user.raw_password)
    activation_code = secrets.token_urlsafe(4)

    db_pelajar = models.Pelajar(
        email=user.email, 
        nama_lengkap=user.nama_lengkap, 
        hashed_password=hashed_password,
        activation_code = activation_code,
        asal_sekolah = user.asal_sekolah,
        jurusan = user.jurusan
    )
    db.add(db_pelajar)
    db.commit()
    db.refresh(db_pelajar)

    activation_string = DOMAIN_URL + "/user/aktivasi?id=" + str(db_pelajar.id) + "&otp=" + activation_code
    # TODO Send mail with verification code
    print(activation_string)
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


def create_materi_pembelajaran(db:Session, mapel: Union[str, int, models.DaftarMapelSkolastik], nama_materi: str):
    if isinstance(mapel, int):
        db_materi = models.MateriPembelajaran(
            nama = nama_materi,
            mapel = models.DaftarMapelSkolastik(mapel),
        )
    elif isinstance(mapel, models.DaftarMapelSkolastik):
        db_materi = models.MateriPembelajaran(
            nama = nama_materi,
            mapel = mapel,
        )
    elif isinstance(mapel, str):   
        db_materi = models.Materi(
            nama = nama_materi,
            mapel = models.DaftarMapelSkolastik[mapel]
        )
    else:
        raise Exception("Unsupported type")

    db.add(db_materi)
    db.commit()
    db.refresh(db_materi)
    return db_materi
    

def read_materi_pembelajaran_by_id(db:Session, id:int):
    return db.query(models.Materi).filter(models.Materi.id == id).one()

def read_materi_pembelajaran_by_mapel(db:Session,  mapel: Union[str, int, models.DaftarMapelSkolastik]):
    if isinstance(mapel, int):
        return db.query(models.Materi).filter(models.Materi.mapel == models.DaftarMapelSkolastik(mapel)).all()
    elif isinstance(mapel, models.DaftarMapelSkolastik):
        return db.query(models.Materi).filter(models.Materi.mapel == mapel).all()
    elif isinstance(mapel, str):   
        return db.query(models.Materi).filter(models.Materi.mapel == models.DaftarMapelSkolastik[mapel]).all()
    else:
        raise Exception("Unsupported type")

def update_nama_materi_pembelajaran_by_id(db: Session, id: int, mapel:str, nama_materi: str):
    if mapel in models.DaftarMapelSkolastik.__members__:
        mapel_value = models.DaftarMapelSkolastik[mapel].value
    else:
        raise Exception("invalid mapel")
    
    db_materi = db.query(models.Materi).filter(models.Materi.id == id).one()
    db_materi.nama = nama_materi
    db_materi.mapel = mapel_value
    db.commit()
    return "done"

def delete_materi_pembelajaran_by_id(db: Session, id: int):
    db.query(models.Materi).filter(models.Materi.id == id).delete()
    db.commit()
    return "done"

def create_video_pembelajaran(db:Session, creator: int, judul: str, materi: int, file: UploadFile):
    db_video = models.VideoPembelajaran(
        creator_id= creator,
        judul=judul,
        id_materi = materi,
        s3_key = str(creator)+datetime.now().strftime("/%Y/%m/%d/%S%f_")+file.filename
    )

    contents = file.file.read()
    file.file.seek(0)
    # Upload the file to to your S3 service
    s3.upload_fileobj(file.file,"video-pembelajaran", db_video.s3_key)
    file.file.close()

    db.add(db_video)
    db.commit()
    db.refresh(db_video)