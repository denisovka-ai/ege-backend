import json
import csv
from pathlib import Path

# Путь к скачанному файлу gaokao_math_qa.json
INPUT_FILE = Path("data/math/gaokao_math_qa.json")
OUTPUT_CSV = "questions_math_agieval.csv"

# Укажите id темы "Математика" из вашей таблицы topics
# Узнать можно через psql: SELECT id, name FROM topics;
TOPIC_ID = 1   # замените на реальный id

def get_answer_text(options, answer_letter):
    """Возвращает текст варианта по букве (A, B, C, D)."""
    if not options or not answer_letter:
        return ''
    # Приводим к верхнему регистру и получаем индекс
    idx = ord(answer_letter.upper()) - ord('A')
    if 0 <= idx < len(options):
        return options[idx].strip()
    return answer_letter  # если что-то пошло не так, возвращаем букву

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['topic_id', 'difficulty', 'text', 'options', 'answer', 'explanation'])

        for item in data:
            text = item.get('question', '').strip()
            if not text:
                continue

            options = item.get('options', [])
            answer_letter = item.get('answer', '').strip()
            if not answer_letter:
                continue

            # Получаем текст правильного ответа
            answer_text = get_answer_text(options, answer_letter)

            writer.writerow([
                TOPIC_ID,
                0.5,   # сложность по умолчанию
                text,
                json.dumps(options, ensure_ascii=False),
                answer_text,
                ''     # пояснение в этом датасете отсутствует
            ])

    print(f"Конвертация завершена. Сохранено в {OUTPUT_CSV}")

if __name__ == '__main__':
    main()