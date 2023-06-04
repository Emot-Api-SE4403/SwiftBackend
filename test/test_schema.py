import pytest
import schema
from datetime import datetime


def test_token_schema():
    # Create a test token data
    token_data = {
        "access_token": "test_token",
        "token_type": "bearer",
    }

    # Create a Token schema instance
    token = schema.Token(**token_data)

    # Assertions
    assert token.access_token == "test_token"
    assert token.token_type == "bearer"


def test_token_data_schema():
    # Create a test token data
    token_data = {
        "id": 1,
    }

    # Create a TokenData schema instance
    token_data = schema.TokenData(**token_data)

    # Assertions
    assert token_data.id == 1


def test_admin_token_data_schema():
    # Create a test admin token data
    admin_token_data = {
        "id": "admin_id",
    }

    # Create an AdminTokenData schema instance
    admin_token_data = schema.AdminTokenData(**admin_token_data)

    # Assertions
    assert admin_token_data.id == "admin_id"


def test_user_login_form_schema():
    # Create a test user login form data
    login_form_data = {
        "email": "test@example.com",
        "password": "test_password",
    }

    # Create a UserLoginForm schema instance
    login_form = schema.UserLoginForm(**login_form_data)

    # Assertions
    assert login_form.email == "test@example.com"
    assert login_form.password == "test_password"


def test_user_register_form_schema():
    # Create a test user register form data
    register_form_data = {
        "email": "test@example.com",
        "nama_lengkap": "Test User",
        "raw_password": "test_password",
    }

    # Create a UserRegisterForm schema instance
    register_form = schema.UserRegisterForm(**register_form_data)

    # Assertions
    assert register_form.email == "test@example.com"
    assert register_form.nama_lengkap == "Test User"
    assert register_form.raw_password == "test_password"


def test_standar_response():
    # Create a test standar response data
    response_data = {
        "detail":"ok"
    }

    response = schema.StandarResponse(**response_data)

    assert response.detail == "ok"

def test_video_metadata():
    metadata = schema.video_metadata(
        id=1,
        time_created=datetime.now(),
        id_materi=2,
        s3_key="video123",
        creator_id=3,
        judul="Video Pembelajaran",
        id_tugas=None
    )

    assert metadata.id == 1
    assert isinstance(metadata.time_created, datetime)
    assert metadata.id_materi == 2
    assert metadata.s3_key == "video123"
    assert metadata.creator_id == 3
    assert metadata.judul == "Video Pembelajaran"
    assert metadata.id_tugas is None


def test_download_video_response():
    metadata = schema.video_metadata(
        id=1,
        time_created=datetime.now(),
        id_materi=2,
        s3_key="video123",
        creator_id=3,
        judul="Video Pembelajaran",
        id_tugas=None
    )
    download_link = "https://example.com/video"

    response = schema.download_video_response(metadata=metadata, download_link=download_link)

    assert isinstance(response.metadata, schema.video_metadata)
    assert response.metadata.id == 1
    assert isinstance(response.metadata.time_created, datetime)
    assert response.metadata.id_materi == 2
    assert response.metadata.s3_key == "video123"
    assert response.metadata.creator_id == 3
    assert response.metadata.judul == "Video Pembelajaran"
    assert response.metadata.id_tugas is None
    assert response.download_link == "https://example.com/video"

def test_attempt_mengerjakan_tugas():
    # Create a sample data dictionary
    data = {
        'id': 1,
        'waktu_mulai': datetime.now(),
        'waktu_selesai': datetime.now(),
        'nilai': 80.5,
        'id_pelajar': 1,
        'id_tugas': 1
    }

    # Create an instance of the schema class
    attempt = schema.attempt_mengerjakan_tugas(**data)

    # Assert that the fields match the provided data
    assert attempt.id == 1
    assert attempt.waktu_mulai == data['waktu_mulai']
    assert attempt.waktu_selesai == data['waktu_selesai']
    assert attempt.nilai == 80.5
    assert attempt.id_pelajar == 1
    assert attempt.id_tugas == 1

def test_daftar_mapel_skolastik():
    assert schema.DaftarMapelSkolastik.kuantitatif.value == 1
    assert schema.DaftarMapelSkolastik.penalaran_matematika.value == 2
    assert schema.DaftarMapelSkolastik.literasi_inggris.value == 3
    assert schema.DaftarMapelSkolastik.literasi_indonesia.value == 4
    assert schema.DaftarMapelSkolastik.penalaran_umum.value == 5
    assert schema.DaftarMapelSkolastik.membaca_dan_menulis.value == 6

    assert isinstance(schema.DaftarMapelSkolastik.kuantitatif, schema.DaftarMapelSkolastik)
    assert isinstance(schema.DaftarMapelSkolastik.penalaran_matematika, schema.DaftarMapelSkolastik)
    assert isinstance(schema.DaftarMapelSkolastik.literasi_inggris, schema.DaftarMapelSkolastik)
    assert isinstance(schema.DaftarMapelSkolastik.literasi_indonesia, schema.DaftarMapelSkolastik)
    assert isinstance(schema.DaftarMapelSkolastik.penalaran_umum, schema.DaftarMapelSkolastik)
    assert isinstance(schema.DaftarMapelSkolastik.membaca_dan_menulis, schema.DaftarMapelSkolastik)

    with pytest.raises(ValueError):
        schema.DaftarMapelSkolastik(7)

def test_materi():
    # Create a sample data dictionary
    data = {
        'id': 1,
        'nama': 'Materi 1',
        'mapel': schema.DaftarMapelSkolastik.kuantitatif
    }

    # Create an instance of the schema class
    materi = schema.Materi(**data)

    # Assert that the fields match the provided data
    assert materi.id == 1
    assert materi.nama == 'Materi 1'
    assert materi.mapel == schema.DaftarMapelSkolastik.kuantitatif

def test_update_materi():
    instance_data = schema.Materi(
        id= 1,
        nama= 'Materi 1',
        mapel= schema.DaftarMapelSkolastik.kuantitatif
    )
    response_data = schema.UpdateMateri(detail="Materi updated successfully.", instance=instance_data)
    assert response_data.detail == "Materi updated successfully."
    assert response_data.instance == instance_data

def test_delete_materi():
    response_data = schema.DeleteMateri(detail="Materi deleted successfully.", row_deleted=3)
    assert response_data.detail == "Materi deleted successfully."
    assert response_data.row_deleted == 3

def test_materi_dengan_daftar_video():
    materi_data = schema.Materi(
        id= 1,
        nama= 'Materi 1',
        mapel= schema.DaftarMapelSkolastik.kuantitatif
    )
    video_metadata_list = [schema.video_metadata(id=1, time_created=datetime.now(), id_materi=1, s3_key="video1", creator_id=1, judul="Video 1", id_tugas=1)]
    response_data = schema.MateriDenganDaftarVideo(id=1, nama="Materi 1", mapel=schema.DaftarMapelSkolastik.kuantitatif, video_pembelajaran=video_metadata_list)
    assert response_data.id == 1
    assert response_data.nama == "Materi 1"
    assert response_data.mapel == schema.DaftarMapelSkolastik.kuantitatif
    assert response_data.video_pembelajaran == video_metadata_list