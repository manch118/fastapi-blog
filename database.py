from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Создаём абсолютный путь к файлу базы данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "blog.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Создаём движок
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Сессии и базовый класс
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Создание всех таблиц (можно вызывать в main.py)
Base.metadata.create_all(bind=engine)
