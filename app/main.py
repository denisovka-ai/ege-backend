from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers import auth, questions, attempts, recommendations, users
import os

app = FastAPI(title="EGE AI Platform")

# CORS (на всякий случай)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем API-роутеры
app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(attempts.router)
app.include_router(recommendations.router)
app.include_router(users.router)

# Папка со статикой (собранный фронтенд)
static_dir = os.path.join(os.path.dirname(__file__), "../static")

# Если папка static существует, раздаём её
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    # fallback, чтобы не сломать API
    print("WARNING: static directory not found, frontend not available")

# Обработчик 404 для React Router (все неизвестные пути отдаём index.html)
@app.exception_handler(404)
async def not_found(request: Request, exc):
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Not Found"}