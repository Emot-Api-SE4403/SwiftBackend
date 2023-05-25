import pytest
from sqlalchemy.orm import Session

from models import DaftarMapelSkolastik, User, Mentor, Pelajar, Admin, Materi, VideoPembelajaran
from database import Base, engine, SessionLocal

@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_db):
    connection = test_db.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

def test_user_model(db_session):
    # Create a test user
    user = User(
        email="test@example.com",
        nama_lengkap="Test User",
        hashed_password="password123",
        is_active=True,
        activation_code="123456",
    )
    db_session.add(user)
    db_session.commit()

    # Retrieve the user from the database
    db_user = db_session.query(User).filter_by(email="test@example.com").first()

    # Assertions
    assert db_user is not None
    assert db_user.email == "test@example.com"
    assert db_user.nama_lengkap == "Test User"
    assert db_user.is_active

def test_materi_model(db_session):
    # Create a test materi
    materi = Materi(
        nama="Test Materi",
        mapel=DaftarMapelSkolastik.kuantitatif,
    )
    db_session.add(materi)
    db_session.commit()

    # Retrieve the materi from the database
    db_materi = db_session.query(Materi).filter_by(nama="Test Materi").first()

    # Assertions
    assert db_materi is not None
    assert db_materi.nama == "Test Materi"
    assert db_materi.mapel == DaftarMapelSkolastik.kuantitatif

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
    db_session.add(mentor)
    db_session.commit()

    # Retrieve the mentor from the database
    db_mentor = db_session.query(Mentor).filter_by(email="mentor@example.com").first()

    # Assertions
    assert db_mentor is not None
    assert db_mentor.email == "mentor@example.com"
    assert db_mentor.nama_lengkap == "Test Mentor"
    assert db_mentor.keahlian == "Test Keahlian"
    assert db_mentor.Asal == "Test Asal"

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
    db_session.add(pelajar)
    db_session.commit()

    # Retrieve the pelajar from the database
    db_pelajar = db_session.query(Pelajar).filter_by(email="pelajar@example.com").first()

    # Assertions
    assert db_pelajar is not None
    assert db_pelajar.email == "pelajar@example.com"
    assert db_pelajar.nama_lengkap == "Test Pelajar"
    assert db_pelajar.asal_sekolah == "Test Asal Sekolah"
    assert db_pelajar.jurusan == "Test Jurusan"
    assert db_pelajar.is_member

def test_admin_model(db_session):
    # Create a test admin
    admin = Admin(
        id="admin1",
        nama_lengkap="Test Admin",
        hashed_password="password123",
    )
    db_session.add(admin)
    db_session.commit()

    # Retrieve the admin from the database
    db_admin = db_session.query(Admin).filter_by(id="admin1").first()

    # Assertions
    assert db_admin is not None
    assert db_admin.id == "admin1"
    assert db_admin.nama_lengkap == "Test Admin"

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
    db_session.add(mentor)
    db_session.commit()

    # Create a test materi
    materi = Materi(
        nama="Test Materi",
        mapel=DaftarMapelSkolastik.kuantitatif,
    )
    db_session.add(materi)
    db_session.commit()

    # Create a test video pembelajaran
    video_pembelajaran = VideoPembelajaran(
        judul="Test Video Pembelajaran",
        creator_id=mentor.uid,
        id_materi=materi.id,
        s3_key="test_video.mp4",
    )
    db_session.add(video_pembelajaran)
    db_session.commit()

    # Retrieve the video pembelajaran from the database
    db_video_pembelajaran = db_session.query(VideoPembelajaran).filter_by(judul="Test Video Pembelajaran").first()

    # Assertions
    assert db_video_pembelajaran is not None
    assert db_video_pembelajaran.judul == "Test Video Pembelajaran"
    assert db_video_pembelajaran.creator_id == mentor.uid
    assert db_video_pembelajaran.id_materi == materi.id
    assert db_video_pembelajaran.s3_key == "test_video.mp4"

