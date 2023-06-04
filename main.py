import json
from typing import Union, Optional, List
from urllib import response

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
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

@app.get("/user/aktivasi",
        response_model=HTMLResponse,
        responses={
            400: {"description": "Bad Request"},
            404: {"description": "Something went wrong"}
        }
        )  
async def activate_user_account(id:int = -1, otp:str = "-1", db: Session = Depends(get_db)):
    if(id==-1 or otp == "-1"):
        raise HTTPException(status_code=400, detail="Bad request")
    try:
        result = crud.read_user_by_id_filter_activation_code(db,id, otp)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Something went wrong",
        )
    crud.update_user_is_active_by_id(db, id)
    response = ''' \
<!DOCTYPE html>
<html>
<head>
  <title>Account Activation</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f2f2f2;
    }
    .container {
      max-width: 400px;
      margin: 0 auto;
      padding: 40px;
      background-color: #fff;
      border-radius: 5px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
      text-align: center;
    }
    h1 {
      color: #333;
      margin-top: 0;
    }
    p {
      color: #666;
      margin-bottom: 20px;
    }
    .success-message {
      color: #2ecc71;
      font-size: 24px;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Account Activation</h1>
    <p>Selamat! Akun anda telah berhasil diaktifkan.</p>
    <p class="success-message">Selamat menikmati layanan kami!</p>
  </div>
</body>
</html> \
        '''
    return HTMLResponse(content=response, status_code=201)

@app.post("/user/resetpassword",
          response_model=schema.StandarResponse,
          responses={
              404: {"description": "No email detected"},
              400: {"description": "Something else went wrong"},
          }
          )
async def permintaan_reset_password(email:str = "", db : Session = Depends(get_db)):
    if not email or email == "":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No email detected",
        )
    try:
        crud.update_user_password_by_temp_password(db, email)
        return {"detail":"Silahkan cek email anda untuk password baru anda"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/user/newpassword", response_model=schema.StandarResponse,
          responses={
              401: {"description": "Incorrect username or password"},
              401: {"description": "Inactive account"},
          })
async def ganti_password_baru(new_data:schema.UserNewPassword, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, new_data.email, new_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Inactive account",
        )
    crud.update_user_password_by_email(db, user, new_data.new_password)
    return({"detail":"password changed"})
        
@app.post("/mentor/updateprofilepicture", response_model=schema.StandarResponse,
          responses={
              400: {"description": "File must be an image"},
              401: {"description": "Could not validate credentials"},
              400: {"description": "Ukuran file terlalu besar. Maksimal ukuran file adalah {} bytes".format(5 * 1024 * 1024)},
              500: {"description": "Something went wrong, details: 'details of the error' "},
          })
@app.post("/pelajar/updateprofilepicture", response_model=schema.StandarResponse,
          responses={
              400: {"description": "File must be an image"},
              401: {"description": "Could not validate credentials"},
              400: {"description": "Ukuran file terlalu besar. Maksimal ukuran file adalah {} bytes".format(5 * 1024 * 1024)},
              500: {"description": "Something went wrong, details: 'details of the error' "},
          })
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



@app.get("/pelajar/mydata", response_model=schema.Pelajar, responses={
    401: {"description": "Could not validate credentials"},
    401: {"description": "Invalid authentication credentials"},
})
async def read_users_pelajar(token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    """
    kalo mau dipake harus tambahin header "Authorization" (tanpa tanda petik) 
    dengan value "Bearer + (token dari /token)"
    """
    current_user = crud.read_user_pelajar_by_id(db, token_data.id)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return current_user

@app.get("/mentor/mydata", response_model=schema.Mentor, responses={
    401: {"description": "Could not validate credentials"},
    401: {"description": "Invalid authentication credentials"},
})
async def read_users_mentor(token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    """
    kalo mau dipake harus tambahin header "Authorization" (tanpa tanda petik) 
    dengan value "Bearer + (token dari /token)"
    """
    current_user = crud.read_user_mentor_by_id(db, token_data.id)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return current_user

@app.post("/pelajar/register", response_model=schema.StandarResponse, responses={
    400: {"description": "user already exists"},
})
async def register_account_pelajar(register_form: schema.PelajarRegisterForm, db: Session = Depends(get_db)):
    """
    Membuat akun pelajar baru
    """
    try:
        crud.create_user_pelajar(db,register_form)
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return {"detail":"ok"}

@app.post("/mentor/register", response_model=schema.StandarResponse, responses={
    400: {"description": "user already exists"},
})
async def register_account_mentor(register_form: schema.MentorRegisterForm, db: Session = Depends(get_db)):
    """
    Membuat akun mentor baru
    """
    try:
        crud.create_user_mentor(db,register_form)
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return {"detail":"ok"}


@app.post("/video/upload", response_model=schema.StandarResponse, responses={
    401: {"description": "Could not validate credentials"},
    400: {"description": "File must be in MP4 format."},
    400: {"description": "Ukuran file terlalu besar. Maksimal ukuran file adalah {} bytes".format(524288000)},
    400: {"description": "Bad materi id"},
})
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
    
    
    materi = crud.read_materi_pembelajaran_filter_by(db, id_materi=id_materi)
    if(len(materi) != 1):
        raise HTTPException(400, detail="Bad materi id")
    crud.create_video_pembelajaran(db, token_data.id, judul_video, id_materi, file)

    return {"detail":"ok",}

@app.get("/video/download", response_model=schema.download_video_response,
         responses={
             401: {"description": "Could not validate credentials"},
             500: {"description": "Something went wrong (details: 'details of the error')"},
         })
async def read_video_pembelajaran(videoid:int, token_data: schema.TokenData = Depends(auth.get_token_data), db: Session = Depends(get_db)):
    try:
        metadata = crud.read_video_pembelajaran_metadata_by_id(db, videoid)
        download_url = crud.read_video_pembelajaran_download_url_by_id(db, videoid)
    except Exception as e:
        raise HTTPException(500, "Something went wrong (details:{})".format(str(e)))
    return {"metadata":metadata, "download link":download_url}

@app.put("/video/update", response_model=schema.StandarResponse,
         responses={
             401: {"description": "Could not validate credentials"},
             401: {"description": "akun tidak ditemukan"},
             401: {"description": "bukan mentor"},
             
         })
async def update_video_pembelajaran(
    video_id:int = Form(...),
    id_materi: int = Form(...),
    judul_video: str = Form(...), 
    token_data: schema.TokenData = Depends(auth.get_token_data), 
    db: Session = Depends(get_db)):

    auth.check_if_user_is_mentor(db, token_data.id)
    crud.update_video_pembelajaran_metadata_by_id(db, video_id, id_materi, judul_video)
    return {"detail":"ok",}
     

@app.delete("/video/delete", response_model=schema.StandarResponse,
         responses={
             401: {"description": "Could not validate credentials"},
             401: {"description": "akun tidak ditemukan"},
             401: {"description": "bukan mentor"},
             
         })
async def delete_video_pembelajaran(
    video_id:int = Form(...),
    token_data: schema.TokenData = Depends(auth.get_token_data), 
    db: Session = Depends(get_db)):

    auth.check_if_user_is_mentor(db, token_data.id)
    crud.delete_video_pembelajaran_by_id(db, video_id)
    return {"detail":"ok",}


@app.post("/admin/register", response_model=schema.StandarResponse,
         responses={
             400: {"description": "user already exist"},
             
         })
async def register_account_admin(register_form: schema.AdminRegisterForm, db: Session =Depends(get_db), admin_token_data = Depends(auth.get_admin_token)):
    try:
        crud.create_new_admin(db, register_form, admin_token_data.id)
    except IntegrityError:
        raise HTTPException(status_code = 400, detail=  "user already exists")
    return{"detail":"ok"}

@app.post("/admin/login", response_model=schema.Token, responses={
    401: {"description": "Incorrect username or password"},
})
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

@app.get("/admin/mydata", response_model=schema.AdminData, 
         responses={
             401: {"description": "Could not validate credentials"},
         })
async def read_users_admin(token_data: schema.AdminTokenData = Depends(auth.get_admin_token), db: Session = Depends(get_db)):
    current_user = crud.read_admin_by_id(db, token_data.id)
    
    return current_user

@app.patch("/admin/pelajar/updatemember",response_model=schema.StandarResponse,
         responses={
             401: {"description": "Could not validate credentials"},
             404: {"description": "account not found"},
             
         })
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

    
@app.post("/video/tugas/add", response_model=schema.tugas_pembelajaran_metadata, 
          responses={
              401: {"description": "Could not validate credentials"},
              400: {"description": "Tugas sudah ada"},
              400: {"description": "invalid video id"},
              403: {"description": "creator id missmatch"},
              
          })
async def tambah_tugas_ke_video(tugas_baru: schema.TambahTugasPembelajaran,tokendata:schema.TokenData = Depends(auth.get_token_data), db= Depends(get_db)):
    try:
        auth.check_if_user_is_mentor(db, tokendata.id)

        db_video = crud.read_video_pembelajaran_metadata_by_id(db, tugas_baru.id_video)

        if(db_video.creator_id != tokendata.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="creator id missmatch")
        
        if db_video.id_tugas != None:
            raise HTTPException(status_code=400, detail="Tugas sudah ada")

        db_tugas = crud.create_tugas_pembelajaran(db, tugas_baru.judul, \
                                              tugas_baru.jumlah_attempt, \
                                              tugas_baru.id_video)

        for soal in tugas_baru.daftar_soal:
            if isinstance(soal, schema.SoalABCKunci):
                db_soal = crud.create_soal_abc(db, soal.pertanyaan, db_tugas.id)
                for i in range(len(soal.pilihan_jawaban)):
                    string_jawaban=soal.pilihan_jawaban[i]
                    jawaban = crud.create_jawaban_abc(db, db_soal.id, string_jawaban)
                    if soal.index_jawaban_benar == i:
                        db_soal = crud.update_soal_abc_add_kunci_by_ids(db, db_soal.id, jawaban.id)
            elif isinstance(soal, schema.SoalBenarSalah):
                db_soal = crud.create_soal_benar_salah(db, soal.pertanyaan, db_tugas.id,\
                                                       soal.pernyataan_pada_benar, \
                                                       soal.pernyataan_pada_salah)
                for jawaban in soal.daftar_jawaban:
                    if isinstance(jawaban, schema.JawabanBenarSalahKunci):
                        crud.create_jawaban_benar_salah(db, db_soal.id, jawaban.isi_jawaban, \
                                                        jawaban.jawaban_pernyataan_yang_benar )
            elif isinstance(soal, schema.SoalMultiPilih):
                db_soal = crud.create_soal_multi_pilih(db, soal.pertanyaan, db_tugas.id)
                for jawaban in soal.pilihan:
                    if isinstance(jawaban, schema.JawabanMultiPilihKunci):
                        crud.create_jawaban_multi_pilih(db, db_soal.id, jawaban.isi_jawaban, \
                                                        jawaban.jawaban_ini_benar)
        print("Save tugas selesai")
        return(db_tugas)
    except NoResultFound:
        raise HTTPException(status_code=400, detail="Invalid video id")
    

@app.delete("/video/tugas/delete", response_model=schema.StandarResponse,
         responses={
             401: {"description": "Could not validate credentials"},
             403: {"description": "creator id missmatch"},
             400: {"description": "Tidak ada tugas pada video ini"},
             400: {"description": "invalid id"},

             
         })
async def menghapus_tugas_yang_ada_pada_video(id_video:int = Form(...), token:schema.TokenData=Depends(auth.get_token_data), \
                                              db=Depends(get_db) ):
    try:
        auth.check_if_user_is_mentor(db, token.id)

        db_video = crud.read_video_pembelajaran_metadata_by_id(db, id_video)

        if(db_video.creator_id != token.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="creator id missmatch")

        if db_video.id_tugas == None:
            raise HTTPException(status_code=400, detail="Tidak ada tugas pada video ini")
        crud.delete_attemp_pengerjaan_tugas_by_id_tugas(db, db_video.id_tugas)
        crud.delete_tugas_pembelajaran_by_id(db, db_video.id_tugas) 
        return({"detail":f"Tugas berhasil dihapus"})
    except NoResultFound:
        raise HTTPException(status_code=400, detail="Invalid id")
    
    
@app.get("/video/tugas", response_model=schema.ReadTugasPembelajaran)
async def mengakses_soal_yang_ada_pada_video(id_video:int = Form(...), \
                                             token:schema.TokenData=Depends(auth.get_token_data), \
                                             db=Depends(get_db)):
    try:
        db_video = crud.read_video_pembelajaran_metadata_by_id(db, id_video)

        if db_video.id_tugas == None:
            raise HTTPException(status_code=400, detail="Tidak ada tugas pada video ini")
        
        tugas_pembelajaran = crud.read_tugas_pembelajaran_by_id(db,db_video.id_tugas )
        daftar_soal=[]
        for soal in tugas_pembelajaran.soal:
            if isinstance(soal, models.SoalABC):
                _daftar_jawaban = []
                for jawaban in soal.pilihan:
                    _daftar_jawaban.append(jawaban.jawaban)
                daftar_soal.append(schema.SoalABC(pertanyaan=soal.pertanyaan, pilihan_jawaban=_daftar_jawaban))
            elif isinstance(soal, models.SoalBenarSalah):
                _daftar_jawaban = []
                for jawaban in soal.pilihan:
                    _daftar_jawaban.append(schema.JawabanBenarSalah(isi_jawaban=jawaban.jawaban))
                daftar_soal.append(schema.SoalBenarSalah(pertanyaan=soal.pertanyaan, \
                                                         pernyataan_pada_benar=soal.benar,\
                                                         pernyataan_pada_salah=soal.salah, \
                                                         daftar_jawaban=_daftar_jawaban)) 
            elif isinstance(soal, models.SoalMultiPilih):
                _daftar_jawaban = []
                for jawaban in soal.pilihan:
                    _daftar_jawaban.append(schema.JawabanMultiPilih(isi_jawaban=jawaban.jawaban))

                daftar_soal.append(schema.SoalMultiPilih(pertanyaan=soal.pertanyaan, pilihan=_daftar_jawaban))
        return schema.ReadTugasPembelajaran(
            judul=tugas_pembelajaran.judul,
            jumlah_attempt=tugas_pembelajaran.attempt_allowed,
            daftar_soal=daftar_soal,
            id=tugas_pembelajaran.id,
            time_created=tugas_pembelajaran.time_created,
            time_updated=tugas_pembelajaran.time_updated if tugas_pembelajaran.time_updated \
                else tugas_pembelajaran.time_created
        )
            
        
    except NoResultFound:
        raise HTTPException(status_code=400, detail="Invalid id")


@app.get("/video/tugas/edit", response_model=schema.ReadTugasPembelajaran)
async def lihat_soal_pada_video_untuk_mentor(id_video:int = Form(...), \
                                             token:schema.TokenData=Depends(auth.get_token_data), \
                                             db=Depends(get_db)):
    try:
        auth.check_if_user_is_mentor(db, token.id)

        db_video = crud.read_video_pembelajaran_metadata_by_id(db, id_video)

        if(db_video.creator_id != token.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="creator id missmatch")

        if db_video.id_tugas == None:
            raise HTTPException(status_code=400, detail="Tidak ada tugas pada video ini")
        
        tugas_pembelajaran = crud.read_tugas_pembelajaran_by_id(db,db_video.id_tugas )
        daftar_soal=[]
        for soal in tugas_pembelajaran.soal:
            if isinstance(soal, models.SoalABC):
                _daftar_jawaban = []
                for jawaban in soal.pilihan:
                    _daftar_jawaban.append(jawaban.jawaban)
                daftar_soal.append(schema.SoalABCKunci(pertanyaan=soal.pertanyaan, \
                                                       pilihan_jawaban=_daftar_jawaban,\
                                                       index_jawaban_benar=soal.kunci))
            elif isinstance(soal, models.SoalBenarSalah):
                _daftar_jawaban = []
                for jawaban in soal.pilihan:
                    _daftar_jawaban.append(schema.JawabanBenarSalahKunci(isi_jawaban=jawaban.jawaban, \
                                                                         jawaban_pernyataan_yang_benar=jawaban.kunci))
                daftar_soal.append(schema.SoalBenarSalah(pertanyaan=soal.pertanyaan, \
                                                         pernyataan_pada_benar=soal.benar,\
                                                         pernyataan_pada_salah=soal.salah, \
                                                         daftar_jawaban=_daftar_jawaban)) 
            elif isinstance(soal, models.SoalMultiPilih):
                _daftar_jawaban = []
                for jawaban in soal.pilihan:
                    _daftar_jawaban.append(schema.JawabanMultiPilihKunci(isi_jawaban=jawaban.jawaban, \
                        jawaban_ini_benar=jawaban.benar))

                daftar_soal.append(schema.SoalMultiPilih(pertanyaan=soal.pertanyaan, pilihan=_daftar_jawaban))
        return schema.ReadTugasPembelajaran(
            judul=tugas_pembelajaran.judul,
            jumlah_attempt=tugas_pembelajaran.attempt_allowed,
            daftar_soal=daftar_soal,
            id=tugas_pembelajaran.id,
            time_created=tugas_pembelajaran.time_created,
            time_updated=tugas_pembelajaran.time_updated if tugas_pembelajaran.time_updated \
                else tugas_pembelajaran.time_created
        )
            
        
    except NoResultFound:
        raise HTTPException(status_code=400, detail="Invalid id")

@app.post("/video/tugas/kumpul", response_model=schema.attempt_mengerjakan_tugas)
async def kirim_jawaban_tugas(format_jawaban:schema.format_kirim_jawaban_tugas,\
                              token: schema.TokenData = Depends(auth.get_token_data),\
                              db:Session = Depends(get_db)):
    try:
        db_tugas = crud.read_tugas_pembelajaran_by_id(db, format_jawaban.id_tugas)
        if(len(crud.read_attempt_mengerjakan_tugas(db, db_tugas.id, token.id)) >= db_tugas.attempt_allowed):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Max attempt reached")
        
        if(db_tugas.video is None):
            raise HTTPException(status.HTTP_400_BAD_REQUEST)
        
        jumlah_soal = len(db_tugas.soal)
        if( jumlah_soal != len(format_jawaban.jawaban)):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Length missmatch")
        
        jawaban_benar = 0.0

        for i in range(jumlah_soal):
            soal = db_tugas.soal[i]
            if isinstance(soal, models.SoalABC):
                
                if(soal.kunci == int(format_jawaban.jawaban[i])):
                    jawaban_benar += 1.0
            elif isinstance(soal, models.SoalBenarSalah):
                jumlah_jawaban = len(soal.pilihan)
                yang_benar = 0
                if(len(soal.pilihan) != len(format_jawaban.jawaban[i])):
                    raise HTTPException(status.HTTP_400_BAD_REQUEST,"Length not match")
                for j in range(jumlah_jawaban):
                    if(int(soal.pilihan[j].kunci) == int(format_jawaban.jawaban[i][j])):
                        yang_benar += 1
                jawaban_benar += yang_benar/jumlah_jawaban

            elif isinstance(soal, models.SoalMultiPilih):
                jumlah_jawaban = len(soal.pilihan)
                yang_benar = 0
                if(len(soal.pilihan) != len(format_jawaban.jawaban[i])):
                    raise HTTPException(status.HTTP_400_BAD_REQUEST,"Length not match")
                for j in range(jumlah_jawaban):
                    if(int(soal.pilihan[j].benar) == int(format_jawaban.jawaban[i][j])):
                        yang_benar += 1
                jawaban_benar += yang_benar/jumlah_jawaban
        nilai:float = jawaban_benar/jumlah_soal
        db_attempt = crud.create_new_attempt_mengerjakan_tugas(db, token.id, db_tugas.id, nilai,\
                     format_jawaban.waktu_mulai, format_jawaban.waktu_selesai)

        return db_attempt

    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid id")
    
@app.get("/video/tugas/nilai", response_model=List[schema.attempt_mengerjakan_tugas])
async def melihat_nilai_pelajar(id_pelajar:int = None, id_tugas:int = None, limit:int = None, page:int=None, \
        token:Union[schema.TokenData, schema.AdminTokenData]=Depends(auth.get_token_dynamic),db:Session = Depends(get_db) ):
    try:
        return crud.read_nilai_tugas_filter_by(db=db, id_tugas=id_tugas, id_pelajar=id_pelajar, limit=limit, page=page)    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@app.get("/video/list", response_model=List[schema.video_metadata])
async def melihat_daftar_video_milik_mentor(
    id_mentor: Optional[int] = Query(None, description="ID mentor yang dicari"),
    id_tugas: Optional[int] = Query(None, description="ID tugas yang dicari"),
    id_materi: Optional[int] = Query(None, description="ID materi yang dicari"),
    judul: Optional[str] = Query(None, description="judul video yang dicari"),
    limit: Optional[int] = Query(None, description="Limit the number of results"),
    page: Optional[int] = Query(None, description="Page number for pagination when using limit"),
    token: Union[schema.TokenData, schema.AdminTokenData] = Depends(auth.get_token_dynamic),
    db: Session = Depends(get_db)
):
    try:
        return crud.read_all_video_pembelajaran(
            db, 
            id_mentor=id_mentor, 
            id_tugas=id_tugas,
            id_materi=id_materi,
            judul=judul,
            limit=limit, 
            page=page
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@app.post("/materi/tambah", response_model=schema.Materi)
async def buat_materi_pembelajaran_baru(
        materi_baru: schema.schema_pembuatan_materi_pembelajaran_baru, 
        token: Union[schema.TokenData, schema.AdminTokenData] = Depends(auth.get_token_dynamic),
        db: Session = Depends(get_db)
        ):
    if isinstance(token, schema.TokenData):
        auth.check_if_user_is_mentor(db, token.id)

    if isinstance(materi_baru.mapel, int):
        if materi_baru.mapel > 6 or materi_baru.mapel < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mapel invalid")
    
    try:
        return crud.create_materi_pembelajaran(db, materi_baru.mapel, materi_baru.nama_materi) 
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mapel invalid")
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Materi sudah ada")
    

@app.put("/materi/admin/update", response_model=schema.UpdateMateri) # <- update materi
async def update_materi(
    id: int,
    materi_baru: schema.schema_pembuatan_materi_pembelajaran_baru, 
    token: schema.AdminTokenData = Depends(auth.get_admin_token), 
    db:Session = Depends(get_db)):
    try:
        if crud.read_admin_by_id(db, token.id) is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user id")
        
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
    

@app.delete("/materi/admin/delete", response_model=schema.DeleteMateri) # <- delete materi
async def delete_materi_menggunakan_id(id:int, token : schema.AdminTokenData=Depends(auth.get_admin_token), db=Depends(get_db) ):
    try:
        if crud.read_admin_by_id(db, token.id) is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user id")

        return {"detail":"ok", "row_deleted":crud.delete_materi_pembelajaran_by_id(db, id)}
    except Exception as e:
        raise HTTPException(500, f"something went wrong, details: {str(e)}")
        
@app.get("/materi/list", response_model=List[schema.MateriDenganDaftarVideo])
async def read_daftar_materi(
        id_materi:Optional[int] = Query(None, description="id materi yang dicari"),
        id_mapel:Optional[int] = Query(None, description="filter materi dengan id mapel"),
        nama_mapel:Optional[str] = Query(None, description="filter materi dengan nama mapel"),
        mapel:Optional[models.DaftarMapelSkolastik] = Query(None, description="filter materi dengan mapel"),
        limit: Optional[int] = Query(None, description="Limit the number of results"),
        page: Optional[int] = Query(None, description="Page number for pagination when using limit"),
        _:Union[schema.TokenData, schema.AdminTokenData] = Depends(auth.get_token_dynamic),
        db: Session = Depends(get_db)
        ):
    try:
        return crud.read_materi_pembelajaran_filter_by(
            db,
            id_materi = id_materi,
            id_mapel = id_mapel,
            nama_mapel = nama_mapel,
            mapel = mapel,
            limit=limit,
            page=page
            )
    except Exception as e:
        raise HTTPException(500, f"something went wrong, details: {str(e)}")
    
@app.get("/materi/tugas/list", response_model=List[schema.tugas_pembelajaran_metadata])
async def read_daftar_tugas(
        id_tugas:Optional[int] = Query(None, description="id materi yang dicari"), 
        newest:Optional[bool] = Query(True, description="mengurutkan dari yang terbaru"), 
        id_video:Optional[int] = Query(None, description="filter materi dengan id video"), 
        judul:Optional[str] = Query(None, description="filter materi dengan judul tugas"), 
        mapel:Optional[str] = Query(None, description="filter materi dengan nama mapel"),
        id_materi: Optional[int] = Query(None, description="filter materi dengan id materi"), 
        id_creator: Optional[int] = Query(None, description="filter materi dengan id mentor"),
        limit: Optional[int] = Query(None, description="Limit the number of results"),
        page: Optional[int] = Query(None, description="Page number for pagination when using limit"),
        _:Union[schema.TokenData, schema.AdminTokenData] = Depends(auth.get_token_dynamic),
        db: Session = Depends(get_db)
        ):
    try:
        return crud.read_tugas_pembelajaran_filter_by(
            db,
            id_tugas=id_tugas,
            newest=newest,
            id_video=id_video,
            mapel=mapel,
            judul=judul,
            id_materi=id_materi,
            id_creator=id_creator,
            limit=limit,
            page=page
            )
    except Exception as e:
        raise HTTPException(500, f"something went wrong, details: {str(e)}")