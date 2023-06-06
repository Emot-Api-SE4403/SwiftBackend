"""
Schema digunakan sebagai struktur data
"""
from enum import Enum
from typing import Optional, Union, List
from datetime import datetime
from pydantic import BaseModel
import models


class Token(BaseModel):
    access_token: str
    token_type: str

class StandarResponse(BaseModel):
    detail: str

    class Config:
        orm_mode = True

class TokenData(BaseModel):
    id: int

class AdminTokenData(BaseModel):
    id: str

class UserLoginForm(BaseModel):
    email:str
    password: str

class UserRegisterForm(BaseModel):
    email:str
    nama_lengkap: str
    raw_password: str

class UserBase(BaseModel): #sebagai id user
    email: str

class UserAuth(UserBase): # template untuk pendaftaran
    password: str

class UserNewPassword(UserAuth):
    new_password: str

class User(UserBase):
    id: int
    email: str
    profile_picture: str
    nama_lengkap: str
    time_created: datetime
    time_updated: Optional[datetime]
    is_active: bool

    class Config:
        orm_mode = True

class Mentor(User):
    keahlian: str
    Asal: str


class MentorRegisterForm(UserRegisterForm):
    keahlian: str
    asal: str

class Pelajar(User):
    asal_sekolah: str
    jurusan: str
    is_member: bool
    


class PelajarRegisterForm(UserRegisterForm):
    asal_sekolah: str
    jurusan: str

class AdminBase(BaseModel):
    id: str

class AdminLoginForm(AdminBase):
    password: str

class AdminData(AdminBase):
    nama_lengkap: str
    time_created: datetime
    time_updated: Optional[datetime]
    created_by: Optional[str]

    class Config:
        orm_mode = True

class AdminRegisterForm(AdminBase):
    nama_lengkap: str
    new_password: str
    
class schema_pembuatan_materi_pembelajaran_baru(BaseModel):
    mapel: Union[int, str]
    nama_materi: str


class SoalABC(BaseModel):
    pertanyaan: str
    pilihan_jawaban: List[str]

    class Config:
        orm_mode = True

class SoalABCKunci(SoalABC):
    index_jawaban_benar: int

class JawabanBenarSalah(BaseModel):
    isi_jawaban: str

    class Config:
        orm_mode = True

class JawabanBenarSalahKunci(JawabanBenarSalah):
    jawaban_pernyataan_yang_benar: bool

class SoalBenarSalah(BaseModel):
    pertanyaan: str
    pernyataan_pada_benar: str
    pernyataan_pada_salah: str
    daftar_jawaban: List[Union[JawabanBenarSalahKunci, JawabanBenarSalah]]

    class Config:
        orm_mode = True

class JawabanMultiPilih(BaseModel):
    isi_jawaban: str

    class Config:
        orm_mode = True

class JawabanMultiPilihKunci(JawabanMultiPilih):
    jawaban_ini_benar: bool

class SoalMultiPilih(BaseModel):
    pertanyaan: str
    pilihan: List[Union[JawabanMultiPilihKunci, JawabanMultiPilih]]

    class Config:
        orm_mode = True

class TugasPembelajaran(BaseModel):
    judul: str
    jumlah_attempt: int
    daftar_soal: List[Union[SoalABCKunci, SoalABC, SoalBenarSalah, SoalMultiPilih]]

    class Config:
        orm_mode = True

class ReadTugasPembelajaran(TugasPembelajaran):
    id: int
    time_created: datetime
    time_updated: Optional[datetime]

    class Config:
        orm_mode = True

class TambahTugasPembelajaran(TugasPembelajaran):
    id_video: int

    class Config:
        orm_mode = True

class format_kirim_jawaban_tugas(BaseModel):
    id_tugas:int
    waktu_mulai: datetime
    waktu_selesai: datetime
    jawaban: List[Union[List[str], str]]

class video_metadata(BaseModel):
    id: int
    time_created: datetime
    id_materi:int
    s3_key: str
    creator_id: int
    judul: str
    id_tugas: Optional[int]

    class Config:
        orm_mode = True

class tugas_pembelajaran_metadata(BaseModel):
    id: int
    time_created: datetime
    time_updated: Optional[datetime]
    judul: str
    attempt_allowed: int

    class Config:
        orm_mode = True

class download_video_response(BaseModel):
    metadata: video_metadata
    download_link: str

    class Config:
        orm_mode = True

class attempt_mengerjakan_tugas(BaseModel):
    id: int
    waktu_mulai: Optional[datetime]
    waktu_selesai: Optional[datetime]
    nilai: Optional[float]
    id_pelajar: int
    id_tugas: int

    class Config:
        orm_mode = True

class Materi(BaseModel):
    id: int
    nama: str
    mapel: models.DaftarMapelSkolastik

    class Config:
        orm_mode = True

class UpdateMateri(StandarResponse):
    instance: Materi

    class Config:
        orm_mode = True

class DeleteMateri(StandarResponse):
    row_deleted: int

    class Config:
        orm_mode = True

class MateriDenganDaftarVideo(Materi):
    video_pembelajaran: List[video_metadata]

    class Config:
        orm_mode = True