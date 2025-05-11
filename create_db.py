from sqlalchemy import create_engine
from models import Base  # замените на актуальный путь, где у вас Base и модели
# Например: from models import Base
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

engine = create_engine("sqlite:///./blog.db")  # путь к вашей базе данных

Base.metadata.create_all(bind=engine)