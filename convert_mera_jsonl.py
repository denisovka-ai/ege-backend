import json
import csv
import re
from pathlib import Path

# Путь к файлу train.jsonl (измените, если нужно)
INPUT_FILE = Path(r"C:\Users\Kir\Desktop\ege-backend\data\mera\train.jsonl")
OUTPUT_CSV = "questions_russian_mera.csv"

# Укажите id темы "Русский язык" из вашей таблицы topics
RUSSIAN_TOPIC_ID = 2   # <-- замените на реальный id

def extract_options(choices_str: str):
    """Разбивает строку вариантов на список (убирает нумерацию)."""
    lines = [line.strip() for line in choices_str.strip().split('\n') if line.strip()]
    options = []
    for line in lines:
        # Убираем нумерацию вроде "1) текст" -> "текст"
        match = re.match(r'^\d+[).]\s*(.*)', line)
        if match:
            options.append(match.group(1).strip())
        else:
            options.append(line)
    return options

def build_full_question(inputs: dict) -> str:
    """Собирает текст вопроса из полей task и text."""
    task = inputs.get('task', '').strip()
    text = inputs.get('text', '').strip()
    if task and text:
        return f"{task}\n\n{text}"
    elif task:
        return task
    else:
        return text

def convert():
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile, \
         open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as outfile:

        writer = csv.writer(outfile)
        writer.writerow(['topic_id', 'difficulty', 'text', 'options', 'answer', 'explanation'])

        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(f"Ошибка JSON в строке {line_num}")
                continue

            inputs = record.get('inputs', {})
            full_question = build_full_question(inputs)
            if not full_question:
                continue

            choices_str = inputs.get('choices', '')
            if not choices_str:
                continue   # пропускаем задания без вариантов (краткий ответ)

            options = extract_options(choices_str)
            answer = record.get('outputs', '').strip()
            if not answer:
                continue

            writer.writerow([
                RUSSIAN_TOPIC_ID,
                0.5,
                full_question,
                json.dumps(options, ensure_ascii=False),
                answer,
                ''
            ])

    print(f"Конвертация завершена. Сохранено в {OUTPUT_CSV}")

if __name__ == '__main__':
    convert()