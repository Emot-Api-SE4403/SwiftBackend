import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import unittest.mock as mock
from sqlalchemy.orm import Session
import auth

import auth
import crud
import models
import schema
from database import SessionLocal

@pytest.fixture
def db():
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()

def test_verify_password():
    plain_password = "password123"
    hashed_password = auth.get_password_hash(plain_password)
    assert auth.verify_password(plain_password, hashed_password) is True

def test_verify_password_incorrect_password():
    plain_password = "password123"
    incorrect_password = "password456"
    hashed_password = auth.get_password_hash(plain_password)
    assert auth.verify_password(incorrect_password, hashed_password) is False

def test_verify_password_invalid_hash():
    plain_password = "password123"
    invalid_hash = "$2b$12$rVInvalidsaltInvalidsaltInvalidsalt897u8341u767v.I3uu"
    assert auth.verify_password(plain_password, invalid_hash) is False

def test_check_for_valid_password_valid_password():
    valid_password = "password123"
    assert auth.check_for_valid_password(valid_password) is None

def test_check_for_valid_password_invalid_password():
    invalid_password = "short"
    with pytest.raises(HTTPException) as exc:
        auth.check_for_valid_password(invalid_password)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert str(exc.value.detail) == "Password too short"

def test_authenticate_user_valid_user(db):
    email = "test@example.com"
    password = "password123"
    hashed_password = auth.get_password_hash(password)
    user = models.User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()

    authenticated_user = auth.authenticate_user(db, email, password)
    assert authenticated_user is not None
    assert authenticated_user.email == email



def test_authenticate_user_valid_user():
    # Create a mock session and user object
    mock_session = mock.Mock(spec=Session)
    mock_user = mock.Mock()
    mock_user.hashed_password = auth.get_password_hash("password123")

    # Mock the read_user_by_email function to return the mock user object
    auth.crud.read_user_by_email = mock.Mock(return_value=mock_user)

    # Call the authenticate_user function with the mock session and valid credentials
    user = auth.authenticate_user(mock_session, "test@example.com", "password123")

    # Assert that the authenticate_user function returns the mock user object
    assert user == mock_user
    # Assert that the read_user_by_email function was called with the correct email
    auth.crud.read_user_by_email.assert_called_once_with(mock_session, "test@example.com")

def test_authenticate_user_invalid_user():
    # Create a mock session
    mock_session = mock.Mock(spec=Session)

    # Mock the read_user_by_email function to return None (user not found)
    auth.crud.read_user_by_email = mock.Mock(return_value=None)

    # Call the authenticate_user function with the mock session and invalid credentials
    user = auth.authenticate_user(mock_session, "test@example.com", "password123")

    # Assert that the authenticate_user function returns False (user not found)
    assert user is False
    # Assert that the read_user_by_email function was called with the correct email
    auth.crud.read_user_by_email.assert_called_once_with(mock_session, "test@example.com")

def test_authenticate_user_invalid_password():
    # Create a mock session and user object
    mock_session = mock.Mock(spec=Session)
    mock_user = mock.Mock()
    mock_user.hashed_password = auth.get_password_hash("password123")

    # Mock the read_user_by_email function to return the mock user object
    auth.crud.read_user_by_email = mock.Mock(return_value=mock_user)

    # Call the authenticate_user function with the mock session and invalid password
    user = auth.authenticate_user(mock_session, "test@example.com", "wrongpassword")

    # Assert that the authenticate_user function returns False (invalid password)
    assert user is False
    # Assert that the read_user_by_email function was called with the correct email
    auth.crud.read_user_by_email.assert_called_once_with(mock_session, "test@example.com")


def test_create_access_token():
    data = {"id": 1}
    access_token = auth.create_access_token(data)
    assert access_token is not None

@pytest.mark.asyncio
async def test_get_token_data_valid_token():
    token = auth.create_access_token({"id":1})
    token_data = await auth.get_token_data(token)
    assert token_data.id == 1

@pytest.mark.asyncio
async def test_get_token_data_invalid_token():
    invalid_token = "invalid_token"
    with pytest.raises(HTTPException) as exc_info:
        await auth.get_token_data(invalid_token)
    assert exc_info.value.status_code == 401


def test_admin_auth_valid_credentials(db):
    id = "admin"
    password = "password123"
    hashed_password = auth.get_password_hash(password)
    admin = models.Admin(id=id, hashed_password=hashed_password)
    db.add(admin)
   

def test_check_if_user_is_mentor_user_found():
    mock_session = mock.Mock(spec=Session)
    mock_user = mock.Mock(spec=models.Mentor)

    auth.crud.read_user_mentor_by_id = mock.Mock(return_value=mock_user)

    auth.check_if_user_is_mentor(mock_session, 1)

    auth.crud.read_user_mentor_by_id.assert_called_once_with(mock_session, 1)

def test_check_if_user_is_mentor_user_not_found():
    mock_session = mock.Mock(spec=Session)

    auth.crud.read_user_mentor_by_id = mock.Mock(return_value=None)

    try:
        auth.check_if_user_is_mentor(mock_session, 1)
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "akun tidak ditemukan"

    auth.crud.read_user_mentor_by_id.assert_called_once_with(mock_session, 1)

def test_check_if_user_is_mentor_user_not_mentor():
    mock_session = mock.Mock(spec=Session)
    mock_user = mock.Mock(spec=models.Mentor)
    mock_user.Asal = None

    auth.crud.read_user_mentor_by_id = mock.Mock(return_value=mock_user)

    try:
        auth.check_if_user_is_mentor(mock_session, 1)
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "bukan mentor"

    auth.crud.read_user_mentor_by_id.assert_called_once_with(mock_session, 1)