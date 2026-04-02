from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Схема для создания пользователя (регистрация)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Схема для ответа с данными пользователя (без пароля)
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True   # позволяет работать с SQLAlchemy моделями

# Схема для логина
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Схема для токена
class Token(BaseModel):
    access_token: str
    token_type: str

# Схема для данных, хранящихся в токене
class TokenData(BaseModel):
    user_id: Optional[int] = None

# Схемы для вопросов
class QuestionBase(BaseModel):
    topic_id: int
    difficulty: float
    text: str
    options: str   # JSON-строка
    answer: str
    explanation: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id: int

    class Config:
        from_attributes = True

# Схемы для попыток
class AttemptCreate(BaseModel):
    question_id: int
    answer_given: str
    response_time: Optional[float] = None   # время ответа в секундах

class AttemptOut(BaseModel):
    id: int
    user_id: int
    question_id: int
    is_correct: bool
    answer_given: str
    response_time: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

# Схема для пользователя с профилем (включая навыки)
class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    skills: Optional[str]   # JSON-строка с навыками

    class Config:
        from_attributes = True