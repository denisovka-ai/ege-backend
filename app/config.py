from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Загружаем .env файл (можно не вызывать, если используется SettingsConfigDict)
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Указываем, что файл .env нужно использовать
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Создаём единственный экземпляр настроек
settings = Settings()