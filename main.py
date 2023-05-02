

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import boto3

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
    return {"detail":"Hello world!"}



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
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Inactive account",
        )
    access_token = auth.create_access_token(data={"id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user/aktivasi")  
async def activate_user_account(id:int = -1, otp:str = "-1", db: Session = Depends(get_db)):
    if(id==-1 or otp == "-1"):
        raise HTTPException(status_code=400, detail="Bad request")
    try:
        result = crud.read_user_by_id_filter_activation_code(db,id, otp)
    except sqlalchemy.orm.exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Something went wrong",
            headers={"WWW-Authenticate": "Bearer"},
        )
    crud.update_user_is_active_by_id(db, id)
    return {"detail":"success"}

@app.post("/user/resetpassword")
async def permintaan_reset_password(email:str = "", db : Session = Depends(get_db)):
    if not email or email == "":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No email detected",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        crud.update_user_password_by_temp_password(db, email)
        return {"detail":"Silahkan cek email anda untuk password baru anda"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/user/newpassword")
async def ganti_password_baru(new_data:schema.UserNewPassword, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, new_data.email, new_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Inactive account",
        )
    crud.update_user_password_by_email(db, user, new_data.new_password)
    return({"detail":"password changed"})
        

@app.get("/pelajar/mydata/", response_model=schema.Pelajar)
async def read_users_pelajar(token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    """
    kalo mau dipake harus tambahin header "Authorization" (tanpa tanda petik) 
    dengan value "Bearer + (token dari /token)"
    """
    current_user = crud.read_user_pelajar_by_id(db, token_data.id)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return current_user

@app.get("/mentor/mydata/", response_model=schema.Mentor)
async def read_users_mentor(token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    """
    kalo mau dipake harus tambahin header "Authorization" (tanpa tanda petik) 
    dengan value "Bearer + (token dari /token)"
    """
    current_user = crud.read_user_mentor_by_id(db, token_data.id)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return current_user

@app.post("/pelajar/register/")
async def register_account_mentor(register_form: schema.PelajarRegisterForm, db: Session = Depends(get_db)):
    """
    Membuat akun pelajar baru
    """
    try:
        crud.create_user_pelajar(db,register_form)
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return {"detail":"ok"}

@app.post("/mentor/register/")
async def register_account_mentor(register_form: schema.MentorRegisterForm, db: Session = Depends(get_db)):
    """
    Membuat akun mentor baru
    """
    try:
        crud.create_user_mentor(db,register_form)
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return {"detail":"ok"}

@app.post("/mentor/uploadvideo")
async def upload_video_materi_baru(
    token_data: schema.TokenData = Depends(auth.get_token_data), 
    file: UploadFile = File(...),
    id_materi: int = Form(...),
    db: Session = Depends(get_db)):
    
    if not file.content_type.startswith('video/mp4'):
        raise HTTPException(status_code=400, detail="File must be in MP4 format.")
    if file.content_length > 524288000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ukuran file terlalu besar. Maksimal ukuran file adalah {} bytes".format(524288000)
        )
    try:
        data_materi = crud.read_materi_pembelajaran_by_id()
    except:
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Materi Pembelajaran tidak ditemukan")

    

    return {"a":"",}


@app.post("/admin/register/")
async def register_account_admin(register_form: schema.AdminRegisterForm, db: Session =Depends(get_db), admin_token_data = Depends(auth.get_admin_token)):
    try:
        crud.create_new_admin(db, register_form, admin_token_data.id)
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return{"detail":"ok"}

@app.post("/admin/login/", response_model=schema.Token)
async def login_for_admin(form_data: schema.AdminLoginForm, db: Session = Depends(get_db)):
    admin = auth.admin_auth(db, form_data.id, form_data.password)
    #admin = crud.read_admin_by_id(db, form_data.id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"id": admin.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/admin/mydata/", response_model=schema.AdminData)
async def read_users_admin(token_data: schema.AdminTokenData = Depends(auth.get_admin_token), db: Session = Depends(get_db)):
    current_user = crud.read_admin_by_id(db, token_data.id)
    
    return current_user

@app.post("/admin/pelajar/updatemember")
async def toggle_user_pelajar_is_member(pelajar: schema.UserBase, token_data: schema.AdminTokenData = Depends(auth.get_admin_token), db: Session = Depends(get_db)):
    try:
        crud.update_user_pelajar_toggle_is_member_by_email(db, pelajar.email)
    except sqlalchemy.orm.exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"detail":"ok"}