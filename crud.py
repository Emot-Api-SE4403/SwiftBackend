import datetime
from typing import List, Union
import secrets
from fastapi import UploadFile
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from database import s3

import models, schema, auth, email_api


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

def update_user_profile_picture_by_id(db: Session, new_profile_picture: UploadFile, id: int):
    db_user = db.query(models.User).filter(models.User.id == id).one()
    db_user.time_updated = datetime.datetime.now()
    db_user.profile_picture = str(db_user.id)+'-'+db_user.time_updated.strftime("%Y%m%d%S") + '-' + new_profile_picture.filename

    s3.upload_fileobj(new_profile_picture.file, 'profile-picture', str(db_user.profile_picture))
    db.commit()

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
    email_api.kirim_password_baru(user.email, user.nama_lengkap, temp_password)
    # print(temp_password)
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
    email_api.kirim_konfimasi_email(user.email, user.nama_lengkap, activation_string)
    # print(activation_string)
    return "done"

def read_user_mentor_by_id(db: Session, user_id: int):
    db_mentor = db.query(models.Mentor).filter(models.Mentor.uid == user_id).one()
    db_mentor.profile_picture = s3.generate_presigned_url(
        'get_object',
        Params = {'Bucket': 'profile-picture', 'Key': db_mentor.profile_picture},
        ExpiresIn = 86400
    )
    return db_mentor
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
    email_api.kirim_konfimasi_email(user.email, user.nama_lengkap, activation_string)
    # print(activation_string)
    return "done"

def read_user_pelajar_by_id(db: Session, user_id: int):
    db_pelajar = db.query(models.Pelajar).filter(models.Pelajar.uid == user_id).first()
    db_pelajar.profile_picture = s3.generate_presigned_url(
        'get_object',
        Params = {'Bucket': 'profile-picture', 'Key': db_pelajar.profile_picture},
        ExpiresIn = 86400
    )
    return db_pelajar

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
        db_materi = models.Materi(
            nama = nama_materi,
            mapel = models.DaftarMapelSkolastik(mapel),
        )
    elif isinstance(mapel, models.DaftarMapelSkolastik):
        db_materi = models.Materi(
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
    
def read_materi_pembelajaran_all_data(db: Session):
    return db.query(models.Materi).all()

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

def update_materi_pembelajaran_by_id(db: Session, id: int, mapel:Union[str,int], nama_materi: str):
    
    db_materi = db.query(models.Materi).filter(models.Materi.id == id).one()
    db_materi.nama = nama_materi
    if isinstance(mapel, int):
        db_materi.mapel = models.DaftarMapelSkolastik(mapel)
    else:
        db_materi.mapel = models.DaftarMapelSkolastik[mapel]
    db.commit()
    db.refresh(db_materi)
    return db_materi

def delete_materi_pembelajaran_by_id(db: Session, id: int):
    hasil = db.query(models.Materi).filter(models.Materi.id == id).delete()
    db.commit()
    return hasil

def create_video_pembelajaran(db:Session, creator: int, judul: str, materi: int, file: UploadFile):
    db_video = models.VideoPembelajaran(
        creator_id= creator,
        judul=judul,
        id_materi = materi,
        s3_key = str(creator)+datetime.datetime.now().strftime("/%Y/%m/%d/%S%f_")+file.filename
    )

    contents = file.file.read()
    file.file.seek(0)
    # Upload the file to to your S3 service
    s3.upload_fileobj(file.file,"video-pembelajaran", db_video.s3_key)
    file.file.close()

    db.add(db_video)
    db.commit()
    db.refresh(db_video)

def read_video_pembelajaran_metadata_by_id(db: Session, id : int):
    return db.query(models.VideoPembelajaran).filter_by(id = id).one()

def read_video_pembelajaran_download_url_by_id(db: Session, id: int):
    db_video = db.query(models.VideoPembelajaran).filter(models.VideoPembelajaran.id == id).one()

    return s3.generate_presigned_url(
        'get_object',
        Params = {'Bucket': 'video-pembelajaran', 'Key': db_video.s3_key},
        ExpiresIn = 10800
    )

def update_video_pembelajaran_metadata_by_id(db:Session, video_id:int, id_materi:int, judul_video:str):
    db_video = db.query(models.VideoPembelajaran).filter(models.VideoPembelajaran.id == video_id).one()
    db_video.id_materi = id_materi
    db_video.judul = judul_video
    db.commit()
    db.refresh(db_video)
    return "ok"

def delete_video_pembelajaran_by_id(db:Session, video_id: int):
    db_video = db.query(models.VideoPembelajaran)\
    .filter(models.VideoPembelajaran.id == video_id).one()

    s3.delete_object(Bucket='video-pembelajaran', key=db_video.s3_key)
    db.query(models.VideoPembelajaran).filter(models.VideoPembelajaran.id == video_id).delete()
    db.commit()
    return "ok"

def create_tugas_pembelajaran(db:Session, judul, attempt:int, id_video:int):
    # print("read video db")
    db_video = db.query(models.VideoPembelajaran).filter(models.VideoPembelajaran.id == id_video).one()

    # print("make tugas db")
    db_tugas = models.TugasPembelajaran(judul=judul, attempt_allowed=attempt)
    db.add(db_tugas)
    db.commit()
    db.refresh(db_tugas)

    # print("update video db")
    db_video.id_tugas = db_tugas.id
    db.commit()
    db.refresh(db_video)
    
    return db_tugas

def create_soal_abc(db:Session, pertanyaan, id_tugas):
    db_soal = models.SoalABC(
        pertanyaan=pertanyaan,
        type="pilihan_ganda",
        id_tugas=id_tugas
    )
    db.add(db_soal)
    db.commit()
    db.refresh(db_soal)
    return db_soal

def create_jawaban_abc(db:Session, id_soal, jawaban):
    db_jawaban = models.JawabanABC(
        id_soal=id_soal,
        jawaban=jawaban
    )
    db.add(db_jawaban)
    db.commit()
    db.refresh(db_jawaban)
    return db_jawaban

def update_soal_abc_add_kunci_by_ids(db:Session, id_soal, id_kunci):
    print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy 1")

    soal = db.query(models.SoalABC).filter(models.SoalABC.id == id_soal).one()
    print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy 2")

    soal.kunci = id_kunci
    print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy 3")

    db.commit()
    print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy 4")

    db.refresh(soal)
    print("okokokokokokokokokokokokokokokokokokokokokokok")
    return soal

def create_soal_benar_salah(db:Session, pertanyaan, id_tugas, pernyataan_true, pernyataan_false):
    db_soal = models.SoalBenarSalah(
        pertanyaan=pertanyaan,
        type="benar_salah",
        id_tugas=id_tugas,
        benar=pernyataan_true,
        salah=pernyataan_false
    )
    db.add(db_soal)
    db.commit()
    db.refresh(db_soal)
    return db_soal

def create_jawaban_benar_salah(db:Session, id_soal, jawaban, pernyataan_yg_benar):
    print("membuat jawaban benar salah")
    db_jawaban = models.JawabanBenarSalah(
        id_soal=id_soal,
        jawaban=jawaban,
        kunci=pernyataan_yg_benar
    )
    db.add(db_jawaban)
    db.commit()
    db.refresh(db_jawaban)
    print("selesai membuat jawaban benar salah")
    return db_jawaban


def create_soal_multi_pilih(db:Session, pertanyaan, id_tugas):
    db_soal = models.SoalMultiPilih(
        pertanyaan=pertanyaan,
        type="multi_pilih",
        id_tugas=id_tugas
    )
    db.add(db_soal)
    db.commit()
    db.refresh(db_soal)
    return db_soal

def create_jawaban_multi_pilih(db:Session, id_soal, jawaban, benar):
    db_jawaban = models.JawabanMultiPilih(
        id_soal=id_soal,
        jawaban=jawaban,
        benar=benar
    )

    db.add(db_jawaban)
    db.commit()
    db.refresh(db_jawaban)
    return db_jawaban


def update_video_pembelajaran_remove_tugas(db:Session, id_video:int):
    db_video = db.query(models.VideoPembelajaran).filter(models.VideoPembelajaran.id == id_video).one()
    db_video.id_tugas = None
    db.commit()


def delete_tugas_pembelajaran_by_id(db: Session, tugas_pembelajaran_id: int):
    # Get the TugasPembelajaran object
    tugas_pembelajaran:models.TugasPembelajaran = db.query(models.TugasPembelajaran).get(tugas_pembelajaran_id)

    if tugas_pembelajaran:
        # Delete the associated Soal objects and their answers
        for soal in tugas_pembelajaran.soal:
            if isinstance(soal, models.SoalABC):
                for jawaban in soal.pilihan:
                    db.delete(jawaban)
                db.delete(soal)
            elif isinstance(soal, models.SoalBenarSalah):
                for jawaban in soal.pilihan:
                    db.delete(jawaban)
                db.delete(soal)
            elif isinstance(soal, models.SoalMultiPilih):
                for jawaban in soal.pilihan:
                    db.delete(jawaban)
                db.delete(soal)
        update_video_pembelajaran_remove_tugas(db, tugas_pembelajaran.video.id)
        db.delete(tugas_pembelajaran)
        db.commit()

        return True

    return False


def read_tugas_pembelajaran_by_id(db:Session, id_tugas):
    return db.query(models.TugasPembelajaran).filter(models.TugasPembelajaran.id == id_tugas).one()

def read_attempt_mengerjakan_tugas(db:Session, id_tugas, id_pelajar):
    return db.query(models.AttemptMengerjakanTugas)\
           .filter(models.AttemptMengerjakanTugas.id_pelajar == id_pelajar, \
                   models.AttemptMengerjakanTugas.id_tugas == id_tugas).all()

def create_new_attempt_mengerjakan_tugas(db:Session, id_pelajar, id_tugas, nilai, start, stop):
    if(nilai//10 == 0):
        nilai = nilai * 10
    
    db_attemp = models.AttemptMengerjakanTugas(
        id_pelajar = id_pelajar,
        id_tugas = id_tugas,
        nilai = nilai,
        waktu_mulai=start,
        waktu_selesai=stop
    )
    db.add(db_attemp)
    db.commit()
    db.refresh(db_attemp)
    return db_attemp


