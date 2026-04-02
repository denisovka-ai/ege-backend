import json
import random
from sqlalchemy.orm import Session
from . import models

def get_user_skill(db: Session, user_id: int, topic_id: int) -> float:
    """
    Получить текущий уровень навыка пользователя по теме.
    Если навык не определён, возвращаем 0.5 (средний).
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.skills:
        return 0.5
    try:
        skills = json.loads(user.skills)
    except json.JSONDecodeError:
        return 0.5
    return skills.get(str(topic_id), 0.5)

def update_user_skill(db: Session, user_id: int, topic_id: int, correct: bool, response_time: float = None):
    """
    Обновить навык пользователя по теме после ответа.
    Используем простую формулу: skill = skill + alpha * (результат - ожидание)
    где ожидание = текущий skill (0..1), alpha = 0.1.
    Можно учитывать время ответа (чем дольше, тем меньше изменение).
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return

    # Текущий навык
    current_skill = get_user_skill(db, user_id, topic_id)

    # Коэффициент обучения (можно регулировать)
    alpha = 0.1
    # Если ответ был долгим (больше 30 секунд), уменьшаем alpha
    if response_time and response_time > 30:
        alpha *= 0.5

    # Ожидаемая вероятность правильного ответа = текущий навык (упрощённо)
    expected = current_skill
    # Результат: 1 если правильно, 0 если нет
    result = 1.0 if correct else 0.0

    # Новая оценка навыка
    new_skill = current_skill + alpha * (result - expected)
    # Ограничиваем в пределах [0, 1]
    new_skill = max(0.0, min(1.0, new_skill))

    # Загружаем все навыки пользователя
    try:
        skills = json.loads(user.skills) if user.skills else {}
    except json.JSONDecodeError:
        skills = {}
    skills[str(topic_id)] = new_skill
    user.skills = json.dumps(skills)
    db.commit()

def select_next_question(db: Session, user_id: int, topic_id: int = None) -> models.Question:
    """
    Подобрать следующий вопрос для пользователя.
    Если topic_id не указан, выбираем тему с наименьшим навыком.
    Возвращает объект Question.
    """
    # Определяем тему, если не задана
    if topic_id is None:
        # Получаем все темы (можно из таблицы topics)
        topics = db.query(models.Topic).all()
        if not topics:
            return None
        # Выбираем тему с минимальным навыком
        min_skill = float('inf')
        best_topic = topics[0]
        for topic in topics:
            skill = get_user_skill(db, user_id, topic.id)
            if skill < min_skill:
                min_skill = skill
                best_topic = topic
        topic_id = best_topic.id

    # Получаем навык по выбранной теме
    skill = get_user_skill(db, user_id, topic_id)

    # Находим вопросы с difficulty близкой к skill
    questions = db.query(models.Question).filter(models.Question.topic_id == topic_id).all()
    if not questions:
        return None

    # Ищем вопросы с difficulty в интервале [skill-0.1, skill+0.1]
    candidates = [q for q in questions if abs(q.difficulty - skill) <= 0.1]
    if not candidates:
        # Если нет близких, берём случайный
        candidates = questions

    return random.choice(candidates)