from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import boto3


load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("SQL_DATABASE_URL")
ENDPOINT_URL = os.getenv("S3_URL")
KEY_ID = os.getenv("S3_KEY_ID")
ACCESS_KEY = os.getenv("S3_ACCESS_KEY")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)


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


