from typing import Union

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import crud, schema, models, auth, analytics
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

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return RedirectResponse(url='/docs')



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
    except NoResultFound:
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
        
@app.post("/mentor/updateprofilepicture")
@app.post("/pelajar/updateprofilepicture")
async def update_profile_picture(
    file: UploadFile = File(...), 
    token_data:schema.TokenData = Depends(auth.get_token_data), 
    db: Session = Depends(get_db)):
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ukuran file terlalu besar. Maksimal ukuran file adalah {} bytes".format(5 * 1024 * 1024)
        )
    try:
        crud.update_user_profile_picture_by_id(db, file, token_data.id)
    except Exception as e:
        raise HTTPException(500, detail='Something went wrong, details: '+str(e))
    return {
        'detail':'ok'
    }



@app.get("/pelajar/mydata", response_model=schema.Pelajar)
async def read_users_pelajar(token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    """
    kalo mau dipake harus tambahin header "Authorization" (tanpa tanda petik) 
    dengan value "Bearer + (token dari /token)"
    """
    current_user = crud.read_user_pelajar_by_id(db, token_data.id)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return current_user

@app.get("/mentor/mydata", response_model=schema.Mentor)
async def read_users_mentor(token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    """
    kalo mau dipake harus tambahin header "Authorization" (tanpa tanda petik) 
    dengan value "Bearer + (token dari /token)"
    """
    current_user = crud.read_user_mentor_by_id(db, token_data.id)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return current_user

@app.post("/pelajar/register")
async def register_account_pelajar(register_form: schema.PelajarRegisterForm, db: Session = Depends(get_db)):
    """
    Membuat akun pelajar baru
    """
    try:
        crud.create_user_pelajar(db,register_form)
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return {"detail":"ok"}

@app.post("/mentor/register")
async def register_account_mentor(register_form: schema.MentorRegisterForm, db: Session = Depends(get_db)):
    """
    Membuat akun mentor baru
    """
    try:
        crud.create_user_mentor(db,register_form)
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return {"detail":"ok"}

@app.post("/materi/tambah")
async def buat_materi_pembelajaran_baru(materi_baru: schema.schema_pembuatan_materi_pembelajaran_baru, token_data:schema.TokenData = Depends(auth.get_token_data), db = Depends(get_db)):
    auth.check_if_user_is_mentor(db, token_data.id)
    
    try:
        if isinstance(materi_baru.mapel, int):
            if materi_baru.mapel > 6 or materi_baru.mapel < 1:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mapel invalid")
            crud.create_materi_pembelajaran(db, materi_baru.mapel, materi_baru.nama_materi)          
        elif isinstance(materi_baru.mapel, str):
            try:
                crud.create_materi_pembelajaran(db, materi_baru.mapel, materi_baru.nama_materi)
            except KeyError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mapel invalid")

        return{"detail":"ok"}
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Materi sudah ada")


@app.get("/materi/daftar")
async def baca_daftar_materi_pembelajaran(mapel:Union[str, int], db=Depends(get_db)):
    try:
        mapel = int(mapel)
        if mapel > 6 or mapel < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mapel invalid")
        return crud.read_materi_pembelajaran_by_mapel(db, mapel)
    except ValueError:
        try:
            return crud.read_materi_pembelajaran_by_mapel(db, mapel)
        except KeyError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mapel invalid")

@app.post("/video/upload")
async def upload_video_materi_baru(
    token_data: schema.TokenData = Depends(auth.get_token_data), 
    file: UploadFile = File(...),
    id_materi: int = Form(...),
    judul_video: str = Form(...),
    db: Session = Depends(get_db)):
    
    # Check jika user adalah mentor
    auth.check_if_user_is_mentor(db, token_data.id)

    # check jika video valid
    if not file.content_type.startswith('video/mp4'):
        raise HTTPException(status_code=400, detail="File must be in MP4 format.")
    if file.size > 524288000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ukuran file terlalu besar. Maksimal ukuran file adalah {} bytes".format(524288000)
        )
    
    # check jika id materi valid
    try:
        crud.read_materi_pembelajaran_by_id(db, id_materi)
        crud.create_video_pembelajaran(db, token_data.id, judul_video, id_materi, file)

    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Materi Pembelajaran tidak ditemukan")
    except Exception as e:
        raise HTTPException(status_code=500, detail='Something went wrong ->'+str(e))

    return {"detail":"ok",}

@app.get("/video/download")
async def read_video_pembelajaran(videoid:int, token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    metadata = crud.read_video_pembelajaran_metadata_by_id(db, videoid)
    download_url = crud.read_video_pembelajaran_download_url_by_id(db, videoid)
    return {"metadata":metadata, "download link":download_url}

@app.put("/video/update")
async def update_video_pembelajaran(
    video_id:int = Form(...),
    id_materi: int = Form(...),
    judul_video: str = Form(...), 
    token_data: schema.TokenData = Depends(auth.get_token_data), 
    db: Session = Depends(get_db)):

    auth.check_if_user_is_mentor(db, token_data.id)
    crud.update_video_pembelajaran_metadata_by_id(db, video_id, id_materi, judul_video)

@app.delete("/video/delete")
async def delete_video_pembelajaran(
    video_id:int = Form(...),
    token_data: schema.TokenData = Depends(auth.get_token_data), 
    db: Session = Depends(get_db)):

    auth.check_if_user_is_mentor(db, token_data.id)
    crud.delete_video_pembelajaran_by_id(db, video_id)


@app.post("/admin/register")
async def register_account_admin(register_form: schema.AdminRegisterForm, db: Session =Depends(get_db), admin_token_data = Depends(auth.get_admin_token)):
    try:
        crud.create_new_admin(db, register_form, admin_token_data.id)
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return{"detail":"ok"}

@app.post("/admin/login", response_model=schema.Token)
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

@app.get("/admin/mydata", response_model=schema.AdminData)
async def read_users_admin(token_data: schema.AdminTokenData = Depends(auth.get_admin_token), db: Session = Depends(get_db)):
    current_user = crud.read_admin_by_id(db, token_data.id)
    
    return current_user

@app.patch("/admin/pelajar/updatemember")
async def toggle_user_pelajar_is_member(pelajar: schema.UserBase, token_data: schema.AdminTokenData = Depends(auth.get_admin_token), db: Session = Depends(get_db)):
    try:
        crud.update_user_pelajar_toggle_is_member_by_email(db, pelajar.email)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"detail":"ok"}

@app.get("/admin/materi/get/all")
async def read_daftar_materi_all(token_data: schema.AdminTokenData = Depends(auth.get_admin_token), db:Session = Depends(get_db)):
    return crud.read_materi_pembelajaran_all_data(db)

@app.get("/admin/materi/get/bymapelname")
async def read_daftar_materi_filter_nama(name: str, token_data: schema.AdminTokenData = Depends(auth.get_admin_token), db:Session = Depends(get_db)):
    return crud.read_materi_pembelajaran_by_mapel(db, name)

@app.get("/admin/materi/get/bymapelid")
async def read_daftar_materi_filter_id(id: str, token_data: schema.AdminTokenData = Depends(auth.get_admin_token), db:Session = Depends(get_db)):
    try:
        return crud.read_materi_pembelajaran_by_mapel(db, int(id))
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found, check your input")
    
@app.post("/admin/materi/add")
async def add_new_materi(
    materi_baru: schema.schema_pembuatan_materi_pembelajaran_baru, 
    token_data: schema.AdminTokenData = Depends(auth.get_admin_token), 
    db:Session = Depends(get_db)):
    if isinstance(materi_baru.mapel, int):
        if materi_baru.mapel > 6 or materi_baru.mapel < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mapel invalid")
    
    try:
        result=crud.create_materi_pembelajaran(db, materi_baru.mapel, materi_baru.nama_materi)
        return{"detail":"ok", "instance":result}
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mapel invalid")
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Materi sudah ada")
    
@app.put("/admin/materi/update")
async def update_materi(
    id: int,
    materi_baru: schema.schema_pembuatan_materi_pembelajaran_baru, 
    token_data: schema.AdminTokenData = Depends(auth.get_admin_token), 
    db:Session = Depends(get_db)):
    
    try:
        try:
            if int(materi_baru.mapel) > 6 or int(materi_baru.mapel) < 1:
                raise HTTPException(status_code=400, detail="invalid mapel id")
            else:
                hasil = crud.update_materi_pembelajaran_by_id(db, id, int(materi_baru.mapel),materi_baru.nama_materi)
            
        except ValueError:
            if materi_baru.mapel in models.DaftarMapelSkolastik.__members__:
                hasil = crud.update_materi_pembelajaran_by_id(db, id, materi_baru.mapel, materi_baru.nama_materi)
            else:
                raise HTTPException(status_code=400, detail="invalid mapel name")
            
        return {"detail":"ok", "instance":hasil}
    except NoResultFound:
        raise HTTPException(status_code=400, detail="Invalid materi id")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something else went wrong, see="+str(e))
    

@app.delete("/admin/materi/delete")
async def delete_materi_menggunakan_id(id:int, _ : schema.AdminTokenData=Depends(auth.get_admin_token), db=Depends(get_db) ):
    try:
        return {"detail":"ok", "row deleted":crud.delete_materi_pembelajaran_by_id(db, id)}
    except:
        raise HTTPException(500, "something went wrong")
    
analytics.load_main_analytics(app)