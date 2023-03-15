"""
Schema digunakan sebagai struktur data
"""

from datetime import datetime
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str

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

class User(UserBase):
    id: int
    email: str
    nama_lengkap: str
    time_created: datetime
    time_updated: datetime
    is_active: bool

    class Config:
        orm_mode = True

class Mentor(User):
    keahlian: str
    Asal: str
    is_verified: bool


class MentorRegisterForm(UserRegisterForm):
    keahlian: str
    asal: str

class Pelajar(User):
    asal_sekolah: str
    jurusan: str

    class Config:
        orm_mode = True

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
    time_updated: datetime
    created_by: str

    class Config:
        orm_mode = True

class AdminRegisterForm(AdminData):
    new_password: str
