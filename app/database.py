from sqlalchemy import create_engine, URL
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

class Base(DeclarativeBase):
    pass
