from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
import pytest
import schema, auth, email_api, models
from database import SessionLocal
from crud import *


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