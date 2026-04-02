import csv
from app.database import SessionLocal
from app.models import Question

def load_csv(csv_file):
    db = SessionLocal()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # ожидаем заголовок
        for row in reader:
            q = Question(
                topic_id=int(row['topic_id']),
                difficulty=float(row['difficulty']),
                text=row['text'],
                options=row['options'],
                answer=row['answer'],
                explanation=row['explanation']
            )
            db.add(q)
        db.commit()
    db.close()
    print(f"Данные из {csv_file} загружены.")

if __name__ == '__main__':
    load_csv('math_105.csv')