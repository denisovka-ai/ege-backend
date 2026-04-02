from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from .. import models, schemas, adaptive
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/", response_model=schemas.QuestionOut)
def get_recommendation(
    topic_id: Optional[int] = Query(None, description="Указать тему (если не указана, выбирается автоматически)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить рекомендованный вопрос для пользователя на основе его навыков.
    """
    question = adaptive.select_next_question(db, current_user.id, topic_id)
    if not question:
        raise HTTPException(status_code=404, detail="No questions available")
    return question