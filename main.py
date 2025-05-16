from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import smtplib
from email.mime.text import MIMEText
import re

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/services")
async def services(request: Request):
    return templates.TemplateResponse("services.html", {"request": request})


@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/solutions")
async def solutions(request: Request):
    return templates.TemplateResponse("solutions.html", {"request": request})

@app.get("/contacts")
async def contacts(request: Request):
    return templates.TemplateResponse("contacts.html", {"request": request})

@app.get("/team")
async def team(request: Request):
    return templates.TemplateResponse("team.html", {"request": request})


@app.get("/vacancies")
async def vacancies(request: Request):
    return templates.TemplateResponse("vacancies.html", {"request": request})

@app.get("/blog")
async def blog(request: Request):
    return templates.TemplateResponse("blog.html", {"request": request})


@app.get("/callback")
async def get_callback(request: Request, status: str = None, message: str = None):
    return templates.TemplateResponse(
        "callback.html",
        {"request": request, "status": status, "message": message}
    )

@app.post("/callback")
async def post_callback(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    message: str = Form(None),
):
    # Валидация данных
    if not name or len(name.strip()) < 2:
        return templates.TemplateResponse(
            "callback.html",
            {
                "request": request,
                "status": "error",
                "message": "Имя слишком короткое"
            }
        )
    
    # Проверка формата телефона (пример: +7 (123) 456-78-90)
    phone_pattern = r"^\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}$"
    if not re.match(phone_pattern, phone):
        return templates.TemplateResponse(
            "callback.html",
            {
                "request": request,
                "status": "error",
                "message": "Неверный формат номера телефона"
            }
        )

    # Настройки SMTP
    sender_email = "manchmanchestr@yandex.com"
    receiver_email = "manchmanchestr@yandex.com"
    app_password = "dosfszmwrdbthsve"

    body = f"Новая заявка с сайта:\n\nИмя: {name}\nТелефон: {phone}\nСообщение: {message or '-'}"

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "Заявка с сайта SmartLife"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.yandex.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        return templates.TemplateResponse(
            "callback.html",
            {
                "request": request,
                "status": "error",
                "message": f"Ошибка отправки: {str(e)}"
            }
        )

    return templates.TemplateResponse(
        "callback.html",
        {
            "request": request,
            "status": "success",
            "message": "Заявка успешно отправлена!"
        }
    )