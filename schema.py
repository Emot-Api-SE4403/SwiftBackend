"""
Schema digunakan sebagai struktur data
"""
from typing import Optional
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

class UserNewPassword(UserAuth):
    new_password: str

class User(UserBase):
    id: int
    email: str
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
    


