from datetime import datetime
from unittest.mock import MagicMock, patch, call
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from crud import *
from models import *
import pytest


def test_read_user_by_email_success():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test user
    test_user = models.User(email="test@example.com")

    # Configure the mock session to return the test user
    session.query.return_value.filter.return_value.first.return_value = test_user

    # Call the function being tested
    result = read_user_by_email(session, "test@example.com")

    # Assertions
    assert result is not None
    assert result.email == "test@example.com"

def test_read_user_by_email_not_found():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Configure the mock session to return None (user not found)
    session.query.return_value.filter.return_value.first.return_value = None

    # Call the function being tested
    result = read_user_by_email(session, "test@example.com")

    # Assertions
    assert result is None


def test_read_user_by_id_filter_activation_code_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test user
    user = User(
        id=1,
        activation_code="123456",
    )

    # Configure the mock session to return the test user
    session.query.return_value.filter.return_value.one.return_value = user

    # Call the function being tested
    result = read_user_by_id_filter_activation_code(session, 1, "123456")

    # Assertions
    session.query.return_value.filter.return_value.one.assert_called_once()
    assert result == user


def test_read_user_by_id_filter_activation_code_user_not_found_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Configure the mock session to raise NoResultFound exception
    session.query.return_value.filter.return_value.one.side_effect = NoResultFound()

    # Call the function being tested
    with pytest.raises(NoResultFound):
        result = read_user_by_id_filter_activation_code(session, 1, "123456")

    # Assertions
    # session.query.return_value.filter.assert_called_once_with(User.id == 1, User.activation_code == "123456")
    session.query.return_value.filter.return_value.one.assert_called_once()


def test_update_user_is_active_by_id_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test user
    user = User(
        id=1,
        is_active=False,
        time_updated=None,
    )

    # Configure the mock session to return the test user
    session.query.return_value.filter.return_value.one.return_value = user

    # Call the function being tested
    result = update_user_is_active_by_id(session, 1)

    # Assertions
    session.query.return_value.filter.return_value.one.assert_called_once()
    assert user.is_active
    assert user.time_updated is not None
    session.add.assert_called_once_with(user)
    session.commit.assert_called_once()
    assert result == "done"

def test_update_user_password_by_email_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test user
    hashed_password = auth.get_password_hash("oldpassword")
    user = User(
        id=1,
        hashed_password=hashed_password,
        time_updated=None,
    )

    # Call the function being tested
    result = update_user_password_by_email(session, user, "newpassword")

    # Assertions
    assert user.hashed_password != hashed_password
    assert user.time_updated is not None
    session.add.assert_called_once_with(user)
    session.commit.assert_called_once()
    assert result == "done"

@patch('crud.s3.upload_fileobj')
def test_update_user_profile_picture_by_id_with_mock(mock_upload_fileobj):
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test user
    user = User(
        id=1,
        time_updated=None,
    )

    # Configure the mock session to return the test user
    session.query.return_value.filter.return_value.one.return_value = user

    # Create a test profile picture
    profile_picture = MagicMock(spec=UploadFile)
    profile_picture.filename = "test_image.png"
    profile_picture.file = "test file"


    # Call the function being tested
    result = update_user_profile_picture_by_id(session, profile_picture, 1)

    # Assertions
    assert user.time_updated is not None
    assert user.profile_picture is not None
    mock_upload_fileobj.assert_called_once()
    session.commit.assert_called_once()
    assert result is None


def test_update_user_password_by_temp_password_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Mock the read_user_by_email function to return None (user not found)
    with patch("crud.read_user_by_email") as mock_read_user:
        mock_read_user.return_value = None

        # Assert that an exception is raised when the user is not found
        with pytest.raises(Exception) as exc_info:
            update_user_password_by_temp_password(session, "test@example.com")

        assert str(exc_info.value) == "Wrong email or User not found"

    # Create a test user
    user = models.User(
        email="test@example.com",
        is_active=False
    )

    # Mock the read_user_by_email function to return the test user
    with patch("crud.read_user_by_email") as mock_read_user:
        mock_read_user.return_value = user

        # Assert that an exception is raised when the user is not active
        with pytest.raises(Exception) as exc_info:
            update_user_password_by_temp_password(session, "test@example.com")

        assert str(exc_info.value) == "Mohon aktifkan akun anda terlebih dahulu"

    # Reset the mock read_user_by_email function
    mock_read_user.reset_mock()

    # Create a test user
    user = models.User(
        email="test@example.com",
        is_active=True
    )

    # Mock the read_user_by_email function to return the test user
    with patch("crud.read_user_by_email") as mock_read_user:
        with patch("requests.post") as mock_post:
            mock_read_user.return_value = user

            # Call the function being tested
            result = update_user_password_by_temp_password(session, "test@example.com")

            # Assertions
            session.add.assert_called_once()  # Verify that session.add was called
            session.commit.assert_called_once()  # Verify that session.commit was called

            assert result == "done"

            mock_post.assert_called_once()


def test_create_user_mentor_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test user
    user = schema.MentorRegisterForm(
        email="test@example.com",
        nama_lengkap="John Doe",
        raw_password="password123",
        keahlian="Python",
        asal="USA"
    )

    # Patch the requests.post function to prevent the API request
    with patch("requests.post") as mock_post:
        # Call the function being tested
        result = create_user_mentor(session, user)

        # Assertions
        session.add.assert_called_once()  # Verify that session.add was called
        session.commit.assert_called_once()  # Verify that session.commit was called

        # Additional assertions specific to the patched requests.post function
        mock_post.assert_called_once()  # Verify that requests.post was called

        assert result == "done"


def test_read_user_mentor_by_id_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test mentor
    mentor = models.Mentor(
        uid=1,
        profile_picture="mentor_profile_picture.jpg"
    )

    # Configure the mock session to return the test mentor
    session.query.return_value.filter.return_value.one.return_value = mentor

    # Patch the s3.generate_presigned_url function
    with patch("database.s3.generate_presigned_url") as mock_generate_presigned_url:
        # Configure the mock generate_presigned_url function to return a test URL
        mock_generate_presigned_url.return_value = "https://example.com/mentor_profile_picture.jpg"

        # Call the function being tested
        result = read_user_mentor_by_id(session, 1)

        # Assertions
        session.query.return_value.filter.return_value.one.assert_called_once()
        mock_generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': 'profile-picture', 'Key': "mentor_profile_picture.jpg"},
            ExpiresIn=86400
        )

        assert result == mentor
        assert result.profile_picture == "https://example.com/mentor_profile_picture.jpg"


def test_create_user_pelajar_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test pelajar
    pelajar = schema.PelajarRegisterForm(
        email="test@example.com",
        nama_lengkap="Test User",
        raw_password="password01",
        asal_sekolah="Test School",
        jurusan="Test Major"
    )

    # Patch the requests.post function
    with patch("requests.post") as mock_post:
        # Configure the mock post function to return a test response
        mock_post.return_value.status_code = 200

        # Call the function being tested
        result = create_user_pelajar(session, pelajar)

        # Assertions
        session.add.assert_called_once()
        session.commit.assert_called_once()
        session.refresh.assert_called_once()
        mock_post.assert_called_once()

        assert result == "done"


def test_read_user_pelajar_by_id_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test mentor
    pelajar = models.Pelajar(
        uid=1,
        profile_picture="profile_picture.jpg"
    )

    # Configure the mock session to return the test mentor
    session.query.return_value.filter.return_value.first.return_value = pelajar

    # Patch the s3.generate_presigned_url function
    with patch("database.s3.generate_presigned_url") as mock_generate_presigned_url:
        # Configure the mock generate_presigned_url function to return a test URL
        mock_generate_presigned_url.return_value = "https://example.com/profile_picture.jpg"

        # Call the function being tested
        result = read_user_pelajar_by_id(session, 1)

        # Assertions
        session.query.return_value.filter.return_value.first.assert_called_once()
        mock_generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': 'profile-picture', 'Key': "profile_picture.jpg"},
            ExpiresIn=86400
        )

        assert result == pelajar
        assert result.profile_picture == "https://example.com/profile_picture.jpg"

def test_update_user_pelajar_toggle_is_member_by_email_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test pelajar
    pelajar = models.Pelajar(
        email="test@example.com",
        is_member=False
    )

    # Configure the mock session to return the test pelajar
    session.query.return_value.filter.return_value.one.return_value = pelajar

    # Call the function being tested
    result = update_user_pelajar_toggle_is_member_by_email(session, "test@example.com")

    # Assertions
    session.query.return_value.filter.return_value.one.assert_called_once()
    session.commit.assert_called_once()

    assert pelajar.is_member is True
    assert result == "success"


def test_create_new_admin_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test admin
    admin_form = schema.AdminRegisterForm(
        id=1,
        nama_lengkap="John Doe",
        new_password="password123",
    )

    # Call the function being tested
    result = create_new_admin(session, admin_form, "parent_user")

    # Assertions
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

    assert result == "done"


def test_read_admin_by_id_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test admin
    admin = models.Admin(id=1, nama_lengkap="John Doe")

    # Configure the mock session to return the test admin
    session.query.return_value.filter.return_value.first.return_value = admin

    # Call the function being tested
    result = read_admin_by_id(session, 1)

    # Assertions
    session.query.return_value.filter.return_value.first.assert_called_once()
    assert result == admin


def test_create_materi_pembelajaran_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test mapel
    mapel_int = 1
    mapel_str = "kuantitatif"
    mapel = DaftarMapelSkolastik(1)

    # Create a test materi
    nama_materi = "Materi A"

    # Call the function being tested
    result = create_materi_pembelajaran(session, mapel, nama_materi)

    # Assertions
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()
    
    # Create a mock session
    session = MagicMock(spec=Session)

    # Call the function being tested with mapel as an int
    result_int = create_materi_pembelajaran(session, mapel_int, nama_materi)

    # Assertions for mapel as an int
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

    # Reset the mock session for the next test
    session.reset_mock()

    # Call the function being tested with mapel as a string
    result_str = create_materi_pembelajaran(session, mapel_str, nama_materi)

    # Assertions for mapel as a string
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

def test_read_materi_pembelajaran_all_data_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Mock data
    materi_list = [
        models.Materi(id=1, mapel=models.DaftarMapelSkolastik(1)),
        models.Materi(id=2, mapel=models.DaftarMapelSkolastik(2)),
        models.Materi(id=3, mapel=models.DaftarMapelSkolastik(3)),
    ]

    # Configure the mock session to return the mock data
    session.query.return_value.all.return_value = materi_list

    # Call the function being tested
    result = read_materi_pembelajaran_all_data(session)

    # Assertions
    session.query.return_value.all.assert_called_once()
    assert result == materi_list


def test_read_materi_pembelajaran_by_id_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Mock data
    materi_id = 1
    materi = models.Materi(id=materi_id, mapel=models.DaftarMapelSkolastik(1))

    # Configure the mock session to return the mock data
    session.query.return_value.filter.return_value.one.return_value = materi

    # Call the function being tested
    result = read_materi_pembelajaran_by_id(session, materi_id)

    # Assertions
    session.query.return_value.filter.return_value.one.assert_called_once()
    assert result == materi


def test_read_materi_pembelajaran_by_mapel_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Mock data
    mapel_int = 1
    mapel_str = "kuantitatif"
    mapel = models.DaftarMapelSkolastik(1)
    materi_list = [
        models.Materi(id=1, mapel=models.DaftarMapelSkolastik(1)),
        models.Materi(id=2, mapel=models.DaftarMapelSkolastik(1)),
    ]

    # Configure the mock session to return the mock data
    session.query.return_value.filter.return_value.all.return_value = materi_list
    

    # Call the function being tested with int mapel
    result_int = read_materi_pembelajaran_by_mapel(session, mapel_int)

    # Assertions for int mapel
    assert result_int == materi_list

    # Call the function being tested with string mapel
    result_str = read_materi_pembelajaran_by_mapel(session, mapel_str)

    # Assertions for string mapel
    assert result_str == materi_list

    # Call the function being tested with string mapel
    result_enum = read_materi_pembelajaran_by_mapel(session, mapel)

    # Assertions for string mapel
    assert result_enum == materi_list


def test_update_materi_pembelajaran_by_id_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Mock data
    id = 1
    mapel_int = 2
    mapel_str = "literasi_indonesia"
    nama_materi = "Updated Materi"

    # Create a mock materi object
    materi = models.Materi(
        id=id,
        nama="Original Materi",
        mapel=models.DaftarMapelSkolastik(mapel_int)
    )

    # Configure the mock session query and filter to return the mock materi object
    session.query.return_value.filter.return_value.one.return_value = materi

    # Call the function being tested with mapel as an integer
    result_int = update_materi_pembelajaran_by_id(session, id, mapel_int, nama_materi)

    # Assertions for mapel as an integer
    session.query.assert_called_once_with(models.Materi)
    session.query.return_value.filter.return_value.one.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(materi)
    assert materi.nama == nama_materi
    assert materi.mapel == models.DaftarMapelSkolastik(mapel_int)
    assert result_int == materi

    # Call the function being tested with mapel as a string
    result_str = update_materi_pembelajaran_by_id(session, id, mapel_str, nama_materi)

    # Assertions for mapel as a string
    session.query.assert_called_with(models.Materi)
    session.query.return_value.filter.return_value.one.assert_called()
    session.commit.assert_called()
    session.refresh.assert_called()
    assert materi.nama == nama_materi
    assert materi.mapel == models.DaftarMapelSkolastik[mapel_str]
    assert result_str == materi

def test_delete_materi_pembelajaran_by_id_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Mock data
    id = 1

    # Configure the mock session query and filter to return the desired result
    session.query.return_value.filter.return_value.delete.return_value = 1

    # Call the function being tested
    result = delete_materi_pembelajaran_by_id(session, id)

    # Assertions
    session.query.return_value.filter.return_value.delete.assert_called_once()
    session.commit.assert_called_once()
    assert result == 1


def test_create_video_pembelajaran_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Mock data
    creator_id = 1
    judul = "Video Pembelajaran"
    materi_id = 2
    s3_key = "video_key"

    # Create a mock file
    file = MagicMock(spec=UploadFile)
    file.filename = "video.mp4"
    file.file = MagicMock()
    file.file.read.return_value = b"video content"

    # Create a mock video object
    video = models.VideoPembelajaran(
        creator_id=creator_id,
        judul=judul,
        id_materi=materi_id,
        s3_key=s3_key
    )

    # Patch datetime.datetime.now() to return a fixed value
    with patch('crud.datetime.datetime') as mock_datetime:
        now = datetime.datetime(2023, 5, 25, 12, 0, 0)
        mock_datetime.now.return_value = now

        # Patch s3.upload_fileobj
        with patch('crud.s3.upload_fileobj') as mock_upload_fileobj:
            mock_upload_fileobj.return_value = None

            # Call the function being tested
            result = create_video_pembelajaran(session, creator_id, judul, materi_id, file)

            # Assertions
            session.add.assert_called_once()
            session.commit.assert_called_once()
            session.refresh.assert_called_once()
            mock_datetime.now.assert_called_once()
            mock_upload_fileobj.assert_called_once()
            file.file.read.assert_called_once()
            file.file.seek.assert_called_once_with(0)
            file.file.close.assert_called_once()


def test_read_video_pembelajaran_metadata_by_id_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Mock data
    video_id = 1

    # Create a mock video object
    video = models.VideoPembelajaran(id=video_id)

    # Configure the mock session to return the mock data
    session.query.return_value.filter_by.return_value.one.return_value = video

    # Call the function being tested
    result = read_video_pembelajaran_metadata_by_id(session, video_id)

    # Assertions
    session.query.return_value.filter_by.assert_called_once_with(id=video_id)
    session.query.return_value.filter_by.return_value.one.assert_called_once()
    assert result == video


def test_read_video_pembelajaran_download_url_by_id_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Mock data
    video_id = 1
    s3_key = "video_key.mp4"
    download_url = "https://example.com/video_key.mp4"

    # Create a mock video object
    video = models.VideoPembelajaran(id=video_id, s3_key=s3_key)

    # Configure the mock session to return the mock data
    session.query.return_value.filter.return_value.one.return_value = video

    # Patch the generate_presigned_url function
    with patch('crud.s3.generate_presigned_url') as mock_generate_presigned_url:
        mock_generate_presigned_url.return_value = download_url

        # Call the function being tested
        result = read_video_pembelajaran_download_url_by_id(session, video_id)

        # Assertions
        session.query.return_value.filter.return_value.one.assert_called_once()
        mock_generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': 'video-pembelajaran', 'Key': s3_key},
            ExpiresIn=10800
        )
        assert result == download_url


def test_update_video_pembelajaran_metadata_by_id_with_mock():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Mock data
    video_id = 1
    id_materi = 1
    judul_video = "Math Lesson"

    # Create a mock video object
    video = models.VideoPembelajaran(id=video_id)

    # Configure the mock session to return the mock data
    session.query.return_value.filter.return_value.one.return_value = video

    # Call the function being tested
    result = update_video_pembelajaran_metadata_by_id(session, video_id, id_materi, judul_video)

    # Assertions
    assert video.id_materi == id_materi
    assert video.judul == judul_video
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(video)
    assert result == "ok"


def test_delete_video_pembelajaran_by_id_with_mock():
    # Create a mock session and S3 client
    session = MagicMock(spec=Session)

    # Mock data
    video_id = 1
    s3_key = "video_key"

    # Create a mock video object
    video = models.VideoPembelajaran(id=video_id, s3_key=s3_key)

    # Configure the mock session to return the mock data
    session.query.return_value.filter.return_value.one.return_value = video

    # Call the function being tested
    with patch('database.s3.delete_object', return_value=True):
        result = delete_video_pembelajaran_by_id(session, video_id)

    # Assertions
    session.query.return_value.filter.return_value.delete.assert_called_once()
    session.commit.assert_called_once()
    assert result == "ok"

def test_create_tugas_pembelajaran():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create test data
    judul = "Test Tugas"
    attempt = 3
    id_video = 12345

    # Configure the mock session to return the test video
    video = models.VideoPembelajaran(id=id_video)
    session.query.return_value.filter.return_value.one.return_value = video

    # Call the function being tested
    result = create_tugas_pembelajaran(session, judul, attempt, id_video)

    # Assertions
    session.add.assert_called_once()  # Verify that session.add was called
    session.commit.assert_called()  # Verify that session.commit was called
    db_tugas = session.add.call_args[0][0]  # Get the TugasPembelajaran object passed to session.add
    assert db_tugas.judul == judul  # Verify that the judul is set correctly
    assert db_tugas.attempt_allowed == attempt  # Verify that the attempt_allowed is set correctly
    assert video.id_tugas == db_tugas.id  # Verify that the id_tugas of the video is updated

    assert result == db_tugas  # Verify that the returned value is the TugasPembelajaran object

def test_create_soal_abc():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create test data
    pertanyaan = "Test Pertanyaan"
    id_tugas = 12345

    # Call the function being tested
    result = create_soal_abc(session, pertanyaan, id_tugas)

    # Assertions
    session.add.assert_called_once()  # Verify that session.add was called
    session.commit.assert_called_once()  # Verify that session.commit was called
    db_soal = session.add.call_args[0][0]  # Get the SoalABC object passed to session.add
    assert db_soal.pertanyaan == pertanyaan  # Verify that the pertanyaan is set correctly
    assert db_soal.type == "pilihan_ganda"  # Verify that the type is set correctly
    assert db_soal.id_tugas == id_tugas  # Verify that the id_tugas is set correctly

    assert result == db_soal


def test_update_soal_abc_add_kunci_by_ids():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Create a test soal and kunci
    soal_id = 1
    kunci_id = 1

    # Mock the query and filter methods
    query_mock = session.query.return_value
    filter_mock = query_mock.filter.return_value
    soal_mock = filter_mock.one.return_value

    # Call the function being tested
    result = update_soal_abc_add_kunci_by_ids(session, soal_id, kunci_id)

    # Assertions
    filter_mock.one.assert_called_once()
    soal_mock.kunci = kunci_id
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

    # Assert the result
    assert result == soal_mock

def test_create_soal_benar_salah():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Define test data
    pertanyaan = "Test pertanyaan"
    id_tugas = 1
    pernyataan_true = "Pernyataan benar"
    pernyataan_false = "Pernyataan salah"

    # Call the function being tested
    result = create_soal_benar_salah(session, pertanyaan, id_tugas, pernyataan_true, pernyataan_false)

    # Assertions
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

def test_create_jawaban_benar_salah():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Define test data
    id_soal = 1
    jawaban = "Jawaban"
    pernyataan_yg_benar = True

    # Call the function being tested
    result = create_jawaban_benar_salah(session, id_soal, jawaban, pernyataan_yg_benar)

    # Assertions
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()


    assert result.id_soal == id_soal
    assert result.jawaban == jawaban
    assert result.kunci == pernyataan_yg_benar

def test_create_soal_multi_pilih():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Define test data
    pertanyaan = "Pertanyaan"
    id_tugas = 1

    # Call the function being tested
    result = create_soal_multi_pilih(session, pertanyaan, id_tugas)

    # Assertions
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

    assert result.pertanyaan == pertanyaan
    assert result.type == "multi_pilih"
    assert result.id_tugas == id_tugas

def test_create_jawaban_multi_pilih():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Define test data
    id_soal = 1
    jawaban = "Jawaban"
    benar = True

    # Call the function being tested
    result = create_jawaban_multi_pilih(session, id_soal, jawaban, benar)

    # Assertions
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()
    assert result.id_soal == id_soal
    assert result.jawaban == jawaban
    assert result.benar == benar


def test_update_video_pembelajaran_remove_tugas():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Define test data
    id_video = 1

    # Call the function being tested
    update_video_pembelajaran_remove_tugas(session, id_video)

    # Assertions
    session.query.assert_called_once_with(models.VideoPembelajaran)
    session.query.return_value.filter.return_value.one.assert_called_once()
    assert session.query.return_value.filter.return_value.one.return_value.id_tugas is None

def test_delete_tugas_pembelajaran_by_id():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Define test data
    tugas_pembelajaran_id = 1

    # Create a mock TugasPembelajaran object
    tugas_pembelajaran = MagicMock(spec=models.TugasPembelajaran)
    tugas_pembelajaran.video.id = 1

    # Create mock Soal objects
    soal_abc = MagicMock(spec=models.SoalABC)
    soal_benar_salah = MagicMock(spec=models.SoalBenarSalah)
    soal_multi_pilih = MagicMock(spec=models.SoalMultiPilih)

    # Assign Soal objects to TugasPembelajaran's soal attribute
    tugas_pembelajaran.soal = [soal_abc, soal_benar_salah, soal_multi_pilih]
    soal_abc.pilihan = [MagicMock(spec=models.JawabanABC)]
    soal_benar_salah.pilihan = [MagicMock(spec=models.JawabanBenarSalah)]
    soal_multi_pilih.pilihan = [MagicMock(spec=models.JawabanMultiPilih)]

    # Mock the query method to return the TugasPembelajaran object
    session.query.return_value.get.return_value = tugas_pembelajaran

    # Call the function being tested
    result = delete_tugas_pembelajaran_by_id(session, tugas_pembelajaran_id)

    # Assertions
    session.query.return_value.get.assert_called_once_with(tugas_pembelajaran_id)
    assert session.query.return_value.get.return_value.video.id == tugas_pembelajaran_id
    assert session.delete.call_count == 7  # 1 for TugasPembelajaran, 3 for Soal objects, and 3 for each Answers
    assert session.commit.called_once()
    assert result is True

def test_delete_tugas_pembelajaran_by_id_not_found():
    session = MagicMock(spec=Session)
    tugas_pembelajaran_id = 1
    session.query.return_value.get.return_value = None

    result = delete_tugas_pembelajaran_by_id(session, tugas_pembelajaran_id)

    session.query.return_value.get.assert_called_once_with(tugas_pembelajaran_id)
    assert result is False


def test_create_jawaban_abc():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Define test data
    id_soal = 1
    jawaban = "Option A"

    # Call the function being tested
    result = create_jawaban_abc(session, id_soal, jawaban)

    # Assertions
    session.add.assert_called_once()  # Verify that session.add was called
    session.commit.assert_called_once()  # Verify that session.commit was called
    session.refresh.assert_called_once_with(result)  # Verify that session.refresh was called with the result
    assert result.id_soal == id_soal  # Verify the id_soal value of the created JawabanABC object
    assert result.jawaban == jawaban  # Verify the jawaban value of the created JawabanABC object

def test_read_tugas_pembelajaran_by_id():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Define test data
    id_tugas = 1
    mock_tugas = MagicMock(spec=models.TugasPembelajaran)

    # Configure the mock session to return the mock_tugas
    session.query.return_value.filter.return_value.one.return_value = mock_tugas

    # Call the function being tested
    result = read_tugas_pembelajaran_by_id(session, id_tugas)

    # Assertions
    session.query.return_value.filter.return_value.one.assert_called_once_with()
    assert result == mock_tugas

def test_read_attempt_mengerjakan_tugas():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Define test data
    id_tugas = 1
    id_pelajar = 1
    mock_attempts = [MagicMock(spec=models.AttemptMengerjakanTugas), MagicMock(spec=models.AttemptMengerjakanTugas)]

    # Configure the mock session to return the mock_attempts
    session.query.return_value.filter.return_value.all.return_value = mock_attempts

    # Call the function being tested
    result = read_attempt_mengerjakan_tugas(session, id_tugas, id_pelajar)

    # Assertions
    session.query.return_value.filter.return_value.all.assert_called_once_with()
    assert result == mock_attempts

def test_create_new_attempt_mengerjakan_tugas():
    # Create a mock session
    session = MagicMock(spec=Session)

    # Define test data
    id_pelajar = 1
    id_tugas = 1
    nilai = 8
    start = datetime.datetime.now()
    stop = datetime.datetime.now()

    # Call the function being tested
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.side_effect = [start, stop]
        result = create_new_attempt_mengerjakan_tugas(session, id_pelajar, id_tugas, nilai, start, stop)

    # Assertions
    session.add.assert_called_once_with(result)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(result)


def test_read_nilai_tugas_filter_by():
    # Create a mock Session object
    db = MagicMock()

    # Set up the test data
    id_pelajar = 1
    id_tugas = 2
    limit = 10
    page = 1

    # Set up the expected return value
    expected_result = [
        MagicMock(spec=models.AttemptMengerjakanTugas),
        MagicMock(spec=models.AttemptMengerjakanTugas),
        MagicMock(spec=models.AttemptMengerjakanTugas)
    ]
    db.query.return_value.all.return_value = expected_result

    # Call the function under test
    result = read_nilai_tugas_filter_by(db, id_pelajar=id_pelajar, id_tugas=id_tugas, limit=limit, page=page)

    # Assert that the query, filter, offset, and limit calls were made with the expected arguments
    db.query.assert_called_once_with(models.AttemptMengerjakanTugas)
    db.query.return_value.filter.assert_called()


