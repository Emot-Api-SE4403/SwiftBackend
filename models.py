"""
Models digunakan sebagai table database
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
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



class Mentor(User):
    __tablename__ = "mentor"

    uid = Column(Integer, ForeignKey("user.id"), primary_key=True)
    keahlian = Column(String(255))
    Asal = Column(String(255))
    is_verified = Column(Boolean, default=False)

    user_data = relationship(User, backref='mentor')



class Pelajar(User):
    __tablename__ = "pelajar"

    uid = Column(Integer, ForeignKey("user.id"), primary_key=True)
    asal_sekolah = Column(String(255))
    jurusan = Column(String(255))

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