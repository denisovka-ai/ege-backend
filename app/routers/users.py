from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
import json
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/statistics")
def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Общая статистика по попыткам
    total_attempts = db.query(models.Attempt).filter(models.Attempt.user_id == current_user.id).count()
    correct_attempts = db.query(models.Attempt).filter(
        models.Attempt.user_id == current_user.id,
        models.Attempt.is_correct == True
    ).count()
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0

    # Парсим skills (JSON строка)
    skills_dict = {}
    if current_user.skills:
        try:
            skills_dict = json.loads(current_user.skills)
        except:
            skills_dict = {}

    # Статистика по предметам (topic_id 1 и 2)
    subjects_stats = {}
    for topic_id, name in [(1, "Математика"), (2, "Русский язык")]:
        attempts = db.query(models.Attempt).join(models.Question).filter(
            models.Attempt.user_id == current_user.id,
            models.Question.topic_id == topic_id
        ).all()
        total = len(attempts)
        correct = sum(1 for a in attempts if a.is_correct)
        
        # Получаем общее количество вопросов по теме
        total_questions = db.query(models.Question).filter(
            models.Question.topic_id == topic_id
        ).count()
        
        subjects_stats[name] = {
            "total_questions": total,
            "total_available": total_questions,
            "correct": correct,
            "accuracy": (correct / total * 100) if total > 0 else 0,
            "skill": skills_dict.get(str(topic_id), 0.5)
        }

    return {
        "total_attempts": total_attempts,
        "accuracy": accuracy,
        "streak_days": current_user.streak_days,
        "subjects": subjects_stats
    }


@router.get("/leaderboard")
def get_leaderboard(
    topic_id: int = 1,  # 1 - математика, 2 - русский
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Получаем всех пользователей
    users = db.query(models.User).all()
    leaderboard = []
    for user in users:
        skill = 0.5
        if user.skills:
            try:
                skills = json.loads(user.skills)
                skill = skills.get(str(topic_id), 0.5)
            except:
                pass
        leaderboard.append({
            "user_id": user.id,
            "username": user.username,
            "school": user.school or "Не указано",
            "city": user.city or "Не указано",
            "score": round(skill * 100, 1)  # переводим в баллы от 0 до 100
        })
    # Сортируем по убыванию баллов
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    # Добавляем место и обрезаем до лимита
    result = []
    for idx, user in enumerate(leaderboard[:limit], 1):
        user["rank"] = idx
        result.append(user)
    return result


@router.get("/me")
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Получить полный профиль пользователя"""
    # Получаем статистику
    stats = get_user_statistics(db, current_user)
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "school": current_user.school or "",
        "city": current_user.city or "",
        "streak_days": current_user.streak_days,
        "created_at": current_user.created_at,
        "statistics": stats
    }


@router.put("/me")
def update_user_profile(
    profile_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Обновить профиль пользователя (школа, город)"""
    if "school" in profile_data:
        current_user.school = profile_data["school"]
    if "city" in profile_data:
        current_user.city = profile_data["city"]
    db.commit()
    db.refresh(current_user)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "school": current_user.school,
        "city": current_user.city
    }


@router.get("/achievements")
def get_achievements(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Все достижения
    all_achievements = db.query(models.Achievement).all()
    # Полученные пользователем
    unlocked = db.query(models.UserAchievement).filter(
        models.UserAchievement.user_id == current_user.id
    ).all()
    unlocked_ids = {ua.achievement_id for ua in unlocked}
    unlocked_dates = {ua.achievement_id: ua.unlocked_at for ua in unlocked}

    result = []
    for ach in all_achievements:
        result.append({
            "id": ach.id,
            "name": ach.name,
            "description": ach.description,
            "icon": ach.icon,
            "unlocked": ach.id in unlocked_ids,
            "unlocked_at": unlocked_dates.get(ach.id, None)
        })
    return result