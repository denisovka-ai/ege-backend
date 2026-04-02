import json
import csv
from pathlib import Path

INPUT_FILE = Path("data/math/gaokao_math_qa.json")
OUTPUT_CSV = "questions_math_agieval.csv"
TOPIC_ID = 1   # замените на реальный id темы "Математика"

def main():
    data = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                data.append(obj)
            except json.JSONDecodeError:
                continue

    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['topic_id', 'difficulty', 'text', 'options', 'answer', 'explanation'])

        for item in data:
            question_text = item.get('question', '').strip()
            if not question_text:
                continue

            options = item.get('options', [])
            label = item.get('label', '').strip()
            if not label:
                continue

            # Сохраняем ответ как есть (строку из букв, например "ACD")
            writer.writerow([
                TOPIC_ID,
                0.5,
                question_text,
                json.dumps(options, ensure_ascii=False),
                label,          # ответ в виде букв
                ''
            ])

    print(f"Конвертация завершена. Сохранено {len(data)} заданий в {OUTPUT_CSV}")

if __name__ == '__main__':
    main()