from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers import auth, questions, attempts, recommendations, users
import os

app = FastAPI(title="EGE AI Platform")

# CORS (на всякий случай, но при одном домене не обязателен)
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

# Путь к папке со статикой (собранный фронтенд)
static_dir = os.path.join(os.path.dirname(__file__), "../static")

# Если папка static существует – раздаём её как корень сайта
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    # Если статики нет – просто выводим сообщение (для отладки)
    @app.get("/")
    def no_frontend():
        return {"error": "Frontend not built. Please run 'npm run build' and copy to 'static' folder."}

# Обработчик 404: для API возвращаем JSON, для остальных путей – index.html (для React Router)
@app.exception_handler(404)
async def custom_404(request: Request, exc):
    # Если запрос начинается с /api или стандартных эндпоинтов – отдаём JSON ошибку
    if request.url.path.startswith(("/auth", "/questions", "/attempts", "/recommendations", "/users", "/api")):
        return {"detail": "Not Found"}
    # Иначе пытаемся отдать index.html для клиентского роутинга
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Not Found"}