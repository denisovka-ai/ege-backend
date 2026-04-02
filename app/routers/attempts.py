from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
import json

from .. import models, schemas, adaptive
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/attempts", tags=["attempts"])

def check_and_unlock_achievement(db: Session, user_id: int, achievement_type: str, value: int = None):
    """
    Проверяет, выполнено ли условие для достижения, и если да – разблокирует его.
    """
    # Ищем достижение по типу и значению (если указано)
    query = db.query(models.Achievement).filter(
        models.Achievement.condition_type == achievement_type
    )
    if value is not None:
        query = query.filter(models.Achievement.condition_value == value)
    achievement = query.first()
    
    if not achievement:
        return
    
    # Проверяем, не разблокировано ли уже
    existing = db.query(models.UserAchievement).filter(
        models.UserAchievement.user_id == user_id,
        models.UserAchievement.achievement_id == achievement.id
    ).first()
    if existing:
        return
    
    # Разблокируем достижение
    user_achievement = models.UserAchievement(
        user_id=user_id,
        achievement_id=achievement.id
    )
    db.add(user_achievement)
    db.commit()


@router.post("/", response_model=schemas.AttemptOut)
def create_attempt(
    attempt_data: schemas.AttemptCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Получаем вопрос
    question = db.query(models.Question).filter(models.Question.id == attempt_data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Проверяем правильность ответа
    is_correct = (attempt_data.answer_given.strip().lower() == question.answer.strip().lower())

    # Сохраняем попытку
    attempt = models.Attempt(
        user_id=current_user.id,
        question_id=question.id,
        answer_given=attempt_data.answer_given,
        is_correct=is_correct,
        response_time=attempt_data.response_time,
        created_at=datetime.utcnow()
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # Обновляем навык пользователя (адаптивный алгоритм)
    adaptive.update_user_skill(
        db=db,
        user_id=current_user.id,
        topic_id=question.topic_id,
        correct=is_correct,
        response_time=attempt_data.response_time
    )

    # === Ударный режим (streak) ===
    today = date.today()
    if current_user.last_activity_date:
        if current_user.last_activity_date == today - timedelta(days=1):
            current_user.streak_days += 1
        elif current_user.last_activity_date != today:
            current_user.streak_days = 1
    else:
        current_user.streak_days = 1
    current_user.last_activity_date = today
    
    # Проверяем достижение "Ударный режим" (14 дней)
    if current_user.streak_days >= 14:
        check_and_unlock_achievement(db, current_user.id, "streak", 14)
    
    db.commit()

    return attempt


@router.get("/history")
def get_attempts_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Получить историю попыток пользователя"""
    attempts = db.query(models.Attempt).filter(
        models.Attempt.user_id == current_user.id
    ).order_by(models.Attempt.created_at.desc()).limit(limit).all()
    
    result = []
    for attempt in attempts:
        question = db.query(models.Question).filter(models.Question.id == attempt.question_id).first()
        result.append({
            "id": attempt.id,
            "question_id": attempt.question_id,
            "question_text": question.text[:100] if question else "",
            "is_correct": attempt.is_correct,
            "answer_given": attempt.answer_given,
            "response_time": attempt.response_time,
            "created_at": attempt.created_at
        })
    return result


@router.get("/subject/{topic_id}")
def get_subject_statistics(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Получить статистику по конкретному предмету"""
    attempts = db.query(models.Attempt).join(models.Question).filter(
        models.Attempt.user_id == current_user.id,
        models.Question.topic_id == topic_id
    ).all()
    
    total = len(attempts)
    correct = sum(1 for a in attempts if a.is_correct)
    
    # Получаем текущий навык
    skills_dict = {}
    if current_user.skills:
        try:
            skills_dict = json.loads(current_user.skills)
        except:
            skills_dict = {}
    skill = skills_dict.get(str(topic_id), 0.5)
    
    return {
        "topic_id": topic_id,
        "total_attempts": total,
        "correct_attempts": correct,
        "accuracy": (correct / total * 100) if total > 0 else 0,
        "skill": skill,
        "recent_attempts": [
            {
                "is_correct": a.is_correct,
                "created_at": a.created_at
            } for a in attempts[-10:]
        ]
    }