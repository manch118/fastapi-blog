from sqlalchemy.orm import Session
from myblog.models import User
from myblog.database import SessionLocal
from passlib.context import CryptContext
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_or_update_admin(username: str, new_username: str = None, new_password: str = None):
    db = SessionLocal()

    # Проверяем, если администратор уже существует
    existing_admin = db.query(User).filter(User.username == username).first()

    if existing_admin:
        # Если новый логин или новый пароль переданы, обновляем данные
        if new_username:
            print(f"[+] Логин обновлен с {existing_admin.username} на {new_username}")
            existing_admin.username = new_username
        if new_password:
            print(f"[+] Пароль обновлен для {existing_admin.username}")
            existing_admin.password = pwd_context.hash(new_password)
        
        db.commit()
        print(f"[+] Админ обновлен: {existing_admin.username}")
    else:
        # Если админ не существует, создаем нового
        if not new_password:
            new_password = "adminpassword123"  # Используем дефолтный пароль

        hashed_password = pwd_context.hash(new_password)
        admin_user = User(username=new_username or username, email="admin@example.com", password=hashed_password, is_admin=True)
        
        db.add(admin_user)
        db.commit()
        print(f"[+] Админ создан: {admin_user.username}")

if __name__ == "__main__":
    # Входные параметры: старое имя, новое имя и/или новый пароль
    old_username = "manch"  # Текущий логин администратора
    new_username = "manch"  # Новый логин (если нужно)
    new_password = "mancho"  # Новый пароль (если нужно)

    create_or_update_admin(old_username, new_username, new_password)