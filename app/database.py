from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv() # читаем .env

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Настройка пула соединений для оптимизации производительности
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,  # Количество постоянных соединений
    max_overflow=20,  # Максимальное количество дополнительных соединений
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=300  # Пересоздание соединений каждые 5 минут
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
