from sqlalchemy import create_engine, URL
from sqlalchemy.orm import DeclarativeBase

from config import settings

url_object = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.DB_USERNAME,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME
)
engine = create_engine(url_object)

class Base(DeclarativeBase):
    pass
