from models import Base
from database import engine  # Здесь ты импортируешь engine, если он у тебя уже есть в database.py

# Удаляем все таблицы (если нужно)
Base.metadata.drop_all(bind=engine)

# Создаем таблицы заново
Base.metadata.create_all(bind=engine)