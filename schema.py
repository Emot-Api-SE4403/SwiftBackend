"""
Schema digunakan untuk container data antara user dan sistem
"""

from typing import Union

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True


class MentorBase(BaseModel): 
    # Data harus wajib ada dalam object mentor
    # Data yang ada di sini dianggap sebagai identitas suatu object
    email: str
    

class MentorAuth(MentorBase): 
    # data tambahan yang diperlukan ketika auth
    # ketika digabung dengan Mentor base, isinya menjadi email dan password
    hashed_password: str

class Mentor(MentorBase):
    # semua data sisanya dari mentor
    # jika ada data yang ditambah di model, tambahkan juga ke sini
    id: int
    nama_lengkap: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel): # sama dengan Mentor
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User): # equal to MentorAuth
    hashed_password: str
