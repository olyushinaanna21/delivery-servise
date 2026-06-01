from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime


#подключение к постгрес
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/delivery"

engine = create_engine(DATABASE_URL, echo=True)

#сессия
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#базовая модель
Base = declarative_base()

#создание сессий в эндпоинтах
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()