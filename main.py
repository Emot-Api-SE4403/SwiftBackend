

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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



@app.post("/pelajar/login", response_model=schema.Token)
@app.post("/mentor/login", response_model=schema.Token)
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

@app.get("/pelajar/mydata/", response_model=schema.Pelajar)
async def read_users_pelajar(token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    """
    kalo mau dipake harus tambahin header "Authorization" (tanpa tanda petik) 
    dengan value "Bearer + (token dari /token)"
    """
    current_user = crud.read_user_pelajar_by_id(db, token_data.id)
    return current_user

@app.get("/mentor/mydata/", response_model=schema.Mentor)
async def read_users_mentor(token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    """
    kalo mau dipake harus tambahin header "Authorization" (tanpa tanda petik) 
    dengan value "Bearer + (token dari /token)"
    """
    current_user = crud.read_user_mentor_by_id(db, token_data.id)
    return current_user

@app.post("/pelajar/register/")
async def register_account_mentor(register_form: schema.PelajarRegisterForm, db: Session = Depends(get_db)):
    """
    Membuat akun pelajar baru
    """
    try:
        crud.create_user_pelajar(db,register_form);
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return {"details":"ok"}

@app.post("/mentor/register/")
async def register_account_mentor(register_form: schema.MentorRegisterForm, db: Session = Depends(get_db)):
    """
    Membuat akun mentor baru
    """
    try:
        crud.create_user_mentor(db,register_form);
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return {"details":"ok"}


@app.post("/admin/register/")
async def register_account_admin(register_form: schema.AdminRegisterForm, db: Session =Depends(get_db), admin_token_data = Depends(auth.get_admin_token)):
    try:
        crud.create_new_admin(db, register_form, admin_token_data.id)
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return{"details":"ok"}

@app.post("/admin/login/", response_model=schema.Token)
async def login_for_admin(form_data: schema.AdminLoginForm, db: Session = Depends(get_db)):
    admin = auth.admin_auth(db, form_data.id, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"id": admin.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/admin/mydata/", response_model=schema.AdminData)
async def read_users_mentor(token_data: schema.AdminTokenData = Depends(auth.get_admin_token), db: Session = Depends(get_db)):
    current_user = crud.read_admin_by_id(db, token_data.id)
    
    return current_user