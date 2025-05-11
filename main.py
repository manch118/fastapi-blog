from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import secrets
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Post
import models, schemas
import os
from pathlib import Path 
from fastapi.responses import JSONResponse
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.responses import HTMLResponse
from werkzeug.utils import secure_filename
from fastapi import File, UploadFile
from typing import List
from fastapi.responses import FileResponse
import models, database
from schemas import PostSchema
from schemas import PaginatedPosts

app = FastAPI()
UPLOAD_FOLDER = 'static/images'  # Папка для хранения изображений
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
models.Base.metadata.create_all(bind=engine)

# Подключаем статику
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount("/static", StaticFiles(directory="static"), name="static")
# Подключаем шаблоны
templates = Jinja2Templates(directory="myblog/templates")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
# Функция для проверки допустимых типов файлов
def allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Псевдологин
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "secret"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(3).all()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


@app.get("/admin", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/admin/panel", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db)):
    is_admin(request)
    posts = db.query(Post).all()  # Получаем все посты
    return templates.TemplateResponse("admin_panel.html", {"request": request, "posts": posts})


@app.post("/admin/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "manch" and password == "mancho":  # Новый логин и пароль
        response = RedirectResponse("/admin/panel", status_code=302)
        response.set_cookie("is_admin", "true")
        return response
    raise HTTPException(status_code=401, detail="Invalid credentials")


def is_admin(request: Request):
    if request.cookies.get("is_admin") != "true":
        raise HTTPException(status_code=401, detail="Not authorized")

@app.get("/admin/create", response_class=HTMLResponse)
def get_create_form(request: Request):
    return templates.TemplateResponse("create_post.html", {"request": request})



# Обработчик POST-запроса для создания поста
@app.post("/admin/create")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Обрабатываем загрузку файла (если есть)
    image_filename = None
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        
        # Проверяем, существует ли директория для сохранения изображений
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        with open(image_path, "wb") as buffer:
            buffer.write(image.file.read())

    # Создаем новый пост
    new_post = Post(
        title=title,
        content=content,
        category=category,
        image=f'images/{image_filename}' if image_filename else None
    )
    db.add(new_post)
    db.commit()

    return RedirectResponse("/admin/panel", status_code=302)


@app.get("/admin/edit/{post_id}", response_class=HTMLResponse)
def edit_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    is_admin(request)
    post = db.query(Post).filter(Post.id == post_id).first()
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})


@app.post("/admin/edit/{post_id}")
def update_post(post_id: int, title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    post.title = title
    post.content = content
    db.commit()
    return RedirectResponse("/admin/panel", status_code=302)


@app.get("/admin/delete/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    db.delete(post)
    db.commit()
    return RedirectResponse("/admin/panel", status_code=302)


# Пример данных
fake_posts = [
    {"title": "Первая статья", "content": "Это первый пост"},
    {"title": "Вторая статья", "content": "Это второй пост"},
]

# Новый роут для получения последних статей в формате JSON
@app.get("/api/posts/latest/json")
def get_latest_posts_json(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(3).all()
    return JSONResponse(content=[
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.isoformat()
        } for post in posts
    ])

@app.get("/api/posts/json")
def get_posts_json(category: str = None, db: Session = Depends(get_db)):
    query = db.query(Post)
    if category:
        query = query.filter(Post.category == category)

    posts = query.order_by(Post.created_at.desc()).all()
    return JSONResponse(content=[
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "category": post.category,
            "created_at": post.created_at.isoformat()
        } for post in posts
    ])

@app.get("/api/posts/html", response_class=HTMLResponse)
def get_posts_html(request: Request, category: str = None, q: str = None, db: Session = Depends(get_db)):
    query = db.query(Post)

    if category:
        query = query.filter(Post.category == category)

    if q:
        query = query.filter(
            Post.title.ilike(f"%{q}%") |
            Post.content.ilike(f"%{q}%")
        )

    posts = query.order_by(Post.created_at.desc()).all()

    return templates.TemplateResponse("components/posts_list.html", {
        "request": request,
        "posts": posts
    })

# Функция для проверки расширения файла
def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Обработчик загрузки изображения
@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # Проверяем, что файл имеет допустимое расширение
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG, JPG, JPEG, GIF are allowed.")
    
    # Получаем путь для сохранения изображения
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    # Сохраняем файл в нужной папке
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return {"filename": file.filename, "url": f"/{file_path}"}

# Обработчик для отображения изображения по URL
@app.get("/static/images/{image_name}")
async def get_image(image_name: str):
    image_path = Path(UPLOAD_FOLDER) / image_name
    if image_path.exists():
        return FileResponse(image_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")



@app.get("/posts")
def read_posts(request: Request, db: Session = Depends(get_db), page: int = 1, limit: int = 10):
    total = db.query(Post).count()
    posts = db.query(Post).offset((page - 1) * limit).limit(limit).all()

    class Pagination:
        def __init__(self, items, page, limit, total):
            self.items = items
            self.page = page
            self.limit = limit
            self.pages = (total + limit - 1) // limit

    paginated = Pagination(posts, page, limit, total)

    return templates.TemplateResponse("posts.html", {
        "request": request,
        "posts": paginated
    })
@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # Проверка типа файла
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG, JPG, JPEG, GIF are allowed.")
    
    # Путь для сохранения файла
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    # Сохраняем файл в папке
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Печать пути для отладки
    print(f"File saved at: {file_path}")
    
    return {"filename": file.filename, "url": f"/{file_path}"}