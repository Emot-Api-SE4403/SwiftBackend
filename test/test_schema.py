import pytest
import schema


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



