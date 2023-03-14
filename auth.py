from datetime import datetime, timedelta
from typing import Union
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schema

# to get a string like this run:
# openssl rand -hex 32
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY_AUTH")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password): #dipakai
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password): # diapakai
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str): # dipakai
    """
    mencek jika user terdaftar di database
    """
    user = crud.get_user_mentor_by_email(db, email )
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict ): # dipakai
    to_encode = data.copy()
    time_now = datetime.utcnow()
    expire = time_now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"iat":time_now, "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_token_data(token: str = Depends(oauth2_scheme)):
    """
    Membaca data yang ada di token
    jika valid mereturn id yang ada dalam token
    jika invalid akan error
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("id")

        if id is None:
            raise credentials_exception
        return schema.TokenData(id=id)
    except JWTError:
        raise credentials_exception


