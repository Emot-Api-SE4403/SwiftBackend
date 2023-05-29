"""
Models digunakan sebagai table database
"""
import os
import enum
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func, Enum
from sqlalchemy.orm import relationship, backref

from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True)
    nama_lengkap = Column(String(255))
    hashed_password =  Column(String(255))
    profile_picture = Column(String(255), default='default.png')
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=False)
    activation_code = Column(String(6))



class Mentor(User):
    __tablename__ = "mentor"

    uid = Column(Integer, ForeignKey("user.id"), primary_key=True)
    keahlian = Column(String(255))
    Asal = Column(String(255))

    user_data = relationship(User, backref='mentor')

class Pelajar(User):
    __tablename__ = "pelajar"

    uid = Column(Integer, ForeignKey("user.id"), primary_key=True)
    asal_sekolah = Column(String(255))
    jurusan = Column(String(255))
    is_member = Column(Boolean, default=False)

    user_data = relationship(User, backref='pelajar')


class Admin(Base):
    __tablename__ = "admin"

    id = Column(String(255), primary_key=True, unique=True)
    nama_lengkap = Column(String(255))
    hashed_password =  Column(String(255))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), ForeignKey('admin.id'))

    # One-to-Many relationship
    children = relationship("Admin", backref=backref('admin', remote_side=[id]))


class DaftarMapelSkolastik(enum.Enum):
    kuantitatif = 1
    penalaran_matematika = 2
    literasi_inggris = 3
    literasi_indonesia = 4
    penalaran_umum = 5
    membaca_dan_menulis = 6

class Materi(Base):
    __tablename__ = "materi_pembelajaran"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama = Column(String(255), unique=True) 
    mapel = Column(Enum(DaftarMapelSkolastik))

class VideoPembelajaran(Base):
    __tablename__ = "video_pembelajaran"

    # Metadata
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    creator_id = Column(Integer, ForeignKey("mentor.uid"))
    time_created = Column(DateTime(timezone=True), server_default=func.now())

    # Content
    judul = Column(String(127), nullable=False)
    id_materi = Column(Integer, ForeignKey("materi_pembelajaran.id"))
    id_tugas = Column(Integer, ForeignKey("tugas_pembelajaran.id"), unique=True)

    s3_key = Column(String(255))

    # Relation
    creator = relationship(Mentor, backref="video_pembelajaran")
    materi = relationship(Materi, backref="video_pembelajaran")
    tugas = relationship("TugasPembelajaran", backref="video_pembelajaran", uselist=False, viewonly=True)


class TugasPembelajaran(Base):
    __tablename__ = "tugas_pembelajaran"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # read: ada, post: tidak
    time_created = Column(DateTime(timezone=True), server_default=func.now()) # read: ada, post: tidak
    time_updated = Column(DateTime(timezone=True), onupdate=func.now()) # read: ada, post: tidak

    judul = Column(String(255))
    attempt_allowed = Column(Integer)

    # Relation
    video = relationship(VideoPembelajaran, backref="tugas_pembelajaran", uselist=False, viewonly=True) # read tidak, post ada
    soal = relationship("Soal", backref="tugas_pembelajaran")

class Soal(Base):
    __tablename__ = "soal"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pertanyaan = Column(String(512), nullable=False)
    type = Column(String(32))

    
    id_tugas = Column(Integer, ForeignKey('tugas_pembelajaran.id'))
    __mapper_args__ = {'polymorphic_on': type}

class SoalABC(Soal):
    __mapper_args__ = {'polymorphic_identity': 'pilihan_ganda'}
    __tablename__ = "soal_pilihan_ganda"

    id_soal = Column(Integer, ForeignKey('soal.id'), primary_key=True)

    kunci = Column(Integer, ForeignKey('jawaban_pilihan_ganda.id_soal')) 
    pilihan = relationship("JawabanABC", backref="soal_pilihan_ganda", \
            primaryjoin="SoalABC.id == foreign(JawabanABC.id_soal)")

class JawabanABC(Base):
    __tablename__ = "jawaban_pilihan_ganda"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_soal = Column(Integer, ForeignKey('soal_pilihan_ganda.id_soal'))
    jawaban = Column(String(127))

class SoalBenarSalah(Soal):
    __mapper_args__ = {'polymorphic_identity': 'benar_salah'}
    __tablename__ = "soal_benar_salah"

    id_soal = Column(Integer, ForeignKey('soal.id'), primary_key=True)
    benar = Column(String(32))
    salah = Column(String(32))

    pilihan = relationship("JawabanBenarSalah", backref="soal_benar_salah")

class JawabanBenarSalah(Base):
    __tablename__ = "jawaban_benar_salah"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_soal = Column(Integer, ForeignKey('soal_benar_salah.id_soal'))
    jawaban = Column(String(127))
    kunci = Column(Boolean)


class SoalMultiPilih(Soal):
    __mapper_args__ = {'polymorphic_identity': 'multi_pilih'}
    __tablename__ = "soal_multi_pilih"

    id_soal = Column(Integer, ForeignKey('soal.id'), primary_key=True)

    pilihan = relationship("JawabanMultiPilih", backref="soal_multi_pilih")


class JawabanMultiPilih(Base):
    __tablename__ = "jawaban_multi_pilih"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_soal = Column(Integer, ForeignKey('soal_multi_pilih.id_soal'))
    jawaban = Column(String(127))
    benar = Column(Boolean)