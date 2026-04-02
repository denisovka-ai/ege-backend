from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .config import settings
from .routers import auth, questions, attempts, recommendations, users
from .auth import get_current_user
from . import models

app = FastAPI(title="EGE AI Platform")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # добавьте порт фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем все роутеры
app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(attempts.router)
app.include_router(recommendations.router)
app.include_router(users.router)   # новый роутер для пользователей (профиль, статистика, рейтинг, достижения)

@app.get("/")
def root():
    return {"message": "Hello, EGE AI Platform!"}

@app.get("/users/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user