"""
Models digunakan sebagai table database
"""

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
    judul = Column(String(255), nullable=False)
    id_materi = Column(Integer, ForeignKey("materi_pembelajaran.id"))

    s3_references = Column(String(255), nullable=False)

    # Relation
    creator = relationship(Mentor, backref="video_pembelajaran")
    materi = relationship(Materi, backref="video_pembelajaran")