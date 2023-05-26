import pytest
from unittest.mock import MagicMock

from models import DaftarMapelSkolastik, User, Mentor, Pelajar, Admin, Materi, VideoPembelajaran

@pytest.fixture
def db_session():
    return MagicMock()

def test_user_model(db_session):
    # Create a test user
    user = User(
        email="test@example.com",
        nama_lengkap="Test User",
        hashed_password="password123",
        is_active=True,
        activation_code="123456",
    )

    # Assertions
    assert user.email == "test@example.com"
    assert user.nama_lengkap == "Test User"
    assert user.is_active

def test_materi_model(db_session):
    # Create a test materi
    materi = Materi(
        nama="Test Materi",
        mapel=DaftarMapelSkolastik.kuantitatif,
    )

    # Assertions
    assert materi.nama == "Test Materi"
    assert materi.mapel == DaftarMapelSkolastik.kuantitatif

def test_mentor_model(db_session):
    # Create a test mentor
    mentor = Mentor(
        email="mentor@example.com",
        nama_lengkap="Test Mentor",
        hashed_password="password123",
        is_active=True,
        activation_code="654321",
        keahlian="Test Keahlian",
        Asal="Test Asal",
    )

    # Assertions
    assert mentor.email == "mentor@example.com"
    assert mentor.nama_lengkap == "Test Mentor"
    assert mentor.keahlian == "Test Keahlian"
    assert mentor.Asal == "Test Asal"

def test_pelajar_model(db_session):
    # Create a test pelajar
    pelajar = Pelajar(
        email="pelajar@example.com",
        nama_lengkap="Test Pelajar",
        hashed_password="password123",
        is_active=True,
        activation_code="987654",
        asal_sekolah="Test Asal Sekolah",
        jurusan="Test Jurusan",
        is_member=True,
    )

    # Assertions
    assert pelajar.email == "pelajar@example.com"
    assert pelajar.nama_lengkap == "Test Pelajar"
    assert pelajar.asal_sekolah == "Test Asal Sekolah"
    assert pelajar.jurusan == "Test Jurusan"
    assert pelajar.is_member

def test_admin_model(db_session):
    # Create a test admin
    admin = Admin(
        id="admin1",
        nama_lengkap="Test Admin",
        hashed_password="password123",
    )

    # Assertions
    assert admin.id == "admin1"
    assert admin.nama_lengkap == "Test Admin"

def test_video_pembelajaran_model(db_session):
    # Create a test mentor
    mentor = Mentor(
        email="mentor@example.com",
        nama_lengkap="Test Mentor",
        hashed_password="password123",
        is_active=True,
        activation_code="654321",
        keahlian="Test Keahlian",
        Asal="Test Asal",
    )

    # Create a test materi
    materi = Materi(
        nama="Test Materi",
        mapel=DaftarMapelSkolastik.kuantitatif,
    )

    # Create a test video pembelajaran
    video_pembelajaran = VideoPembelajaran(
        judul="Test Video Pembelajaran",
        creator_id=mentor.uid,
        id_materi=materi.id,
        s3_key="test_video.mp4",
    )

    # Assertions
    assert video_pembelajaran.judul == "Test Video Pembelajaran"
    assert video_pembelajaran.creator_id == mentor.uid
    assert video_pembelajaran.id_materi == materi.id
    assert video_pembelajaran.s3_key == "test_video.mp4"
