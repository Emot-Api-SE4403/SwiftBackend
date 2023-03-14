from sqlalchemy.orm import Session

import models, schema, auth


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schema.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schema.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    #db.refresh(db_item)
    return db_item


def get_user_mentor_by_email(db: Session, email: str):
    return db.query(models.Mentor).filter(models.Mentor.email == email).first()

def get_user_mentor_by_id(db: Session, user_id: int):
    return db.query(models.Mentor).filter(models.Mentor.id == user_id).first()

def create_user_mentor(db: Session, user: schema.MentorRegisterForm):
    fake_hashed_password = auth.get_password_hash(user.raw_password)
    db_user = models.Mentor(email=user.email, nama_lengkap=user.nama_lengkap, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user