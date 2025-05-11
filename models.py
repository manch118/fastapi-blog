from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
from database import engine

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(Text)
    category = Column(String(50))  # Добавляем категорию
    image = Column(String(255))  # путь к картинке
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "image": self.image,
            "created_at": self.created_at.isoformat()  # Преобразуем дату в строку
        }

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)

# Создание таблиц при запуске
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)