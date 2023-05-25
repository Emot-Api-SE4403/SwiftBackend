from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import boto3


load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("SQL_DATABASE_URL")
ENDPOINT_URL = os.getenv("S3_URL")
KEY_ID = os.getenv("S3_ACCESS_KEY")
ACCESS_KEY = os.getenv("S3_SECRET_KEY")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
# Create database if it does not exist.
if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

s3= boto3.client('s3', 
    endpoint_url= ENDPOINT_URL,
    aws_access_key_id=KEY_ID,
    aws_secret_access_key=ACCESS_KEY,
    aws_session_token=None,
    config=boto3.session.Config(signature_version='s3v4'),
    verify=False
)


