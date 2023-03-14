from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("SQL_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
# Create database if it does not exist.
if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()