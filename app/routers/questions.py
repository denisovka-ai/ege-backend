from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/questions", tags=["questions"])

@router.get("/", response_model=List[schemas.QuestionOut])
def get_questions(
    topic_id: Optional[int] = Query(None, description="Filter by topic ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # защищаем эндпоинт
):
    """
    Получить список вопросов (доступно только авторизованным пользователям).
    Можно фильтровать по теме.
    """
    query = db.query(models.Question)
    if topic_id:
        query = query.filter(models.Question.topic_id == topic_id)
    questions = query.offset(skip).limit(limit).all()
    return questions

@router.get("/{question_id}", response_model=schemas.QuestionOut)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить конкретный вопрос по ID.
    """
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question