from unittest.mock import MagicMock, patch
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


