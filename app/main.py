from fastapi import FastAPI
from .database import engine, Base
from .config import settings

# Создаём таблицы в базе данных (пока закомментируем, будем использовать миграции)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="EGE AI Platform")

@app.get("/")
def root():
    return {"message": "Hello, EGE AI Platform!"}

# Здесь позже подключатся роутеры