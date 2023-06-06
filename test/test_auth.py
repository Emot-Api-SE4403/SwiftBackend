from unittest import result
import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import unittest.mock as mock
from sqlalchemy.orm import Session
import auth
from jose import jwt

import auth
import crud
import models
import schema
from database import SessionLocal


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
    with mock.patch('auth.pwd_context.verify') as mock_verify:
        mock_verify.return_value = False
        result = auth.verify_password(plain_password, invalid_hash)
    assert result is False

def test_check_for_valid_password_valid_password():
    valid_password = "password123"
    assert auth.check_for_valid_password(valid_password) is None

def test_check_for_valid_password_invalid_password():
    invalid_password = "short"
    with pytest.raises(HTTPException) as exc:
        auth.check_for_valid_password(invalid_password)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert str(exc.value.detail) == "Password too short"

def test_authenticate_user_valid_user():
    email = "test@example.com"
    password = "password123"
    hashed_password = auth.get_password_hash(password)
    user = models.User(email=email, hashed_password=hashed_password)

    # Mock the database session and relevant functions
    db = mock.MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = user

    authenticated_user = auth.authenticate_user(db, email, password)
    assert authenticated_user is not None
    assert authenticated_user.email == email



def test_authenticate_user_valid_user():
    mock_session = mock.Mock(spec=Session)
    mock_user = mock.Mock()
    mock_user.hashed_password = auth.get_password_hash("password123")

    auth.crud.read_user_by_email = mock.Mock(return_value=mock_user)

    user = auth.authenticate_user(mock_session, "test@example.com", "password123")

    assert user == mock_user
    auth.crud.read_user_by_email.assert_called_once_with(mock_session, "test@example.com")

def test_authenticate_user_invalid_user():
    mock_session = mock.Mock(spec=Session)

    auth.crud.read_user_by_email = mock.Mock(return_value=None)

    user = auth.authenticate_user(mock_session, "test@example.com", "password123")

    assert user is False
    auth.crud.read_user_by_email.assert_called_once_with(mock_session, "test@example.com")

def test_authenticate_user_invalid_password():
    mock_session = mock.Mock(spec=Session)
    mock_user = mock.Mock()
    mock_user.hashed_password = auth.get_password_hash("password123")

    auth.crud.read_user_by_email = mock.Mock(return_value=mock_user)

    user = auth.authenticate_user(mock_session, "test@example.com", "wrongpassword")

    
    assert user is False
    
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


@pytest.mark.asyncio
async def test_get_token_data_token_contain_none():
    token = "test"
    with pytest.raises(HTTPException) as exc_info:
        with mock.patch('jose.jwt.decode') as payload:
            payload.return_value.get.return_value = None
            await auth.get_token_data(token)

            assert exc_info.value.status_code == 401
            assert str(exc_info.value) == "Could not validate credentials"

def test_admin_auth_valid_credentials():
    id = "admin_id"
    password = "password"
    hashed_password = auth.get_password_hash(password)
    
    admin = models.Admin(id=id, hashed_password=hashed_password)

    mock_db = mock.MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = admin

    with mock.patch('auth.crud.read_admin_by_id', return_value=admin), \
         mock.patch('auth.verify_password', return_value=True):
        result = auth.admin_auth(mock_db, id, password)

    assert result == admin

def test_admin_auth_invalid_credentials():
    id = "admin_id"
    password = "password"
    hashed_password = auth.get_password_hash(password)
    
    admin = models.Admin(id=id, hashed_password=hashed_password)

    mock_db = mock.MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = admin

    with mock.patch('auth.crud.read_admin_by_id', return_value=admin), \
         mock.patch('auth.verify_password', return_value=False):
        with pytest.raises(HTTPException) as exc:
            auth.admin_auth(mock_db, id, password)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert str(exc.value.detail) == "Wrong id/password"

def test_admin_auth_id_not_found():
    id = "admin_id"
    password = "password"

    mock_db = mock.MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    with mock.patch('auth.crud.read_admin_by_id', return_value=None):
        with pytest.raises(HTTPException) as exc:
            auth.admin_auth(mock_db, id, password)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert str(exc.value.detail) == "Not found"

   

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



@pytest.mark.asyncio
async def test_get_admin_token_valid_token():
    payload = {"id": "admin_id"}

    token = auth.create_access_token(payload)

    admin_token_data = await auth.get_admin_token(token=token)

    assert admin_token_data.id == payload["id"]


@pytest.mark.asyncio
async def test_get_admin_token_invalid_token():
    token = "invalid_token"

    with pytest.raises(HTTPException) as exc:
        await auth.get_admin_token(token=token)

    assert exc.type == HTTPException
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert str(exc.value.detail) == "Could not validate credentials"

@pytest.mark.asyncio
async def test_get_admin_token_contain_none():
    token = "test"
    with pytest.raises(HTTPException) as exc_info:
        with mock.patch('jose.jwt.decode') as payload:
            payload.return_value.get.return_value = None
            await auth.get_admin_token(token)

            assert exc_info.value.status_code == 401
            assert str(exc_info.value) == "Could not validate credentials"

@pytest.mark.asyncio
async def test_get_token_dynamic():
    token_user = auth.create_access_token({"id":1})
    token_data = await auth.get_token_dynamic(token_user)
    assert token_data.id == 1
    assert isinstance(token_data, schema.TokenData)

    token_admin = auth.create_access_token({"id":"admin"})
    token_data = await auth.get_token_dynamic(token_admin)
    assert token_data.id == "admin"
    assert isinstance(token_data, schema.AdminTokenData)

    token_err = auth.create_access_token({"id": "admin"})
    with mock.patch("auth.jwt.decode") as mock_decode:
        mock_decode.side_effect = auth.JWTError("Invalid token")
        with pytest.raises(HTTPException) as exc_info:
            await auth.get_token_dynamic(token_err)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    with pytest.raises(HTTPException) as exc_info:
        with mock.patch('jose.jwt.decode') as payload:
            payload.return_value.get.return_value = None
            await auth.get_token_dynamic("test token")

            assert exc_info.value.status_code == 401
            assert str(exc_info.value) == "Could not validate credentials"
    