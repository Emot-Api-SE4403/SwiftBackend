import pytest
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import Session

from database import engine, create_database, SessionLocal, Base, s3

@pytest.fixture(scope="session")
def test_database():
    # Create the test database if it doesn't exist
    if not database_exists(engine.url):
        create_database(engine.url)

    # Apply the database schema
    Base.metadata.create_all(bind=engine)

    # Provide a session for the tests
    session = SessionLocal()

    yield session  # Test code will execute here

    # Tear down the test database
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_s3_client():
    # Test S3 client configuration
    assert s3 is not None
    # Add more assertions specific to your S3 client setup

def test_database_connection(test_database):
    # Test database connection
    assert test_database is not None
    # Add more assertions or queries to test the database connection

def test_database_session(test_database):
    # Test the database session
    assert isinstance(test_database, Session)
    # Add more assertions or queries to test the database session
