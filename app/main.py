from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from .database import engine, Base
from .config import settings
from .routers import auth, questions, attempts, recommendations, users
from .auth import get_current_user
from . import models
import os

app = FastAPI(title="EGE AI Platform")

# Разрешаем CORS (можно оставить, но если фронтенд на том же домене, не обязательно)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://celebrated-swan-a6df24.netlify.app",  # ваш старый Netlify URL
        "https://ege-pro-100.netlify.app",            # если меняли имя
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все API-роутеры
app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(attempts.router)
app.include_router(recommendations.router)
app.include_router(users.router)

# Определяем путь к папке со статикой (собранный React)
static_dir = os.path.join(os.path.dirname(__file__), "../static")

# Если папка статики существует, раздаём её
if os.path.exists(static_dir):
    # Монтируем статические файлы (CSS, JS, изображения)
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    # Если статики нет (например, при разработке), просто корневой маршрут
    @app.get("/")
    def root():
        return {"message": "Hello, EGE AI Platform!"}

# Глобальный обработчик 404: для API возвращаем JSON, для остальных путей – index.html
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    # Если запрос к API (начинается с /auth, /questions и т.д.) – отдаём JSON ошибку
    if request.url.path.startswith(("/auth", "/questions", "/attempts", "/recommendations", "/users", "/api")):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    # Иначе пытаемся отдать index.html из папки статики
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})