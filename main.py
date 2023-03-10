

from fastapi import Depends, FastAPI, HTTPException, status

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud, schema, models, auth
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.get("/")
async def home():
    """
    Home page, return hello world
    """
    return {"message":"Hello world!"}

@app.post("/users/login", response_model=schema.Token)
async def login_for_access_token(form_data: schema.UserLoginForm, db: Session = Depends(get_db)):
    
    user = auth.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schema.Mentor)
async def read_users_me(token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    """
    kalo mau dipake harus tambahin header "Authorization" (tanpa tanda petik) 
    dengan value "Bearer + (token dari /token)"

    """
    current_user = crud.get_user_mentor_by_id(db, token_data.id)
    return current_user

@app.post("/users/register/mentor")
async def register_account_mentor(mentor_register_form: schema.MentorRegisterForm, db: Session = Depends(get_db)):
    """
    Membuat akun mentor baru
    """
    
    crud.create_user_mentor(db, mentor_register_form);
    
    return {"message":"ok"}



