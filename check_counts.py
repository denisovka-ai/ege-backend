from app.database import SessionLocal
from app.models import Question

db = SessionLocal()
# Список всех topic_id, которые есть в таблице questions
topics = db.query(Question.topic_id).distinct().all()
for (tid,) in topics:
    count = db.query(Question).filter(Question.topic_id == tid).count()
    print(f"topic_id {tid}: {count} заданий")
db.close()