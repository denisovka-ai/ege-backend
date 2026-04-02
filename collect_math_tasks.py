import csv
import json
from pathlib import Path

# Путь к папке dataset_benchmark (относительный или абсолютный)
# Если скрипт лежит в C:\Users\Kir\Desktop\Auto-check-EGE-math, то так:
TASKS_ROOT = Path(__file__).parent / "dataset_benchmark"
# Если вы запускаете скрипт из другого места, замените на абсолютный путь:
# TASKS_ROOT = Path(r"C:\Users\Kir\Desktop\Auto-check-EGE-math\dataset_benchmark")

OUTPUT_CSV = "questions_math_auto.csv"
TOPIC_ID = 1   # id математики в таблице topics (уточните через psql)

def parse_text_file(file_path):
    """Парсит текстовый файл формата: условие --- ответ --- пояснение."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    parts = content.split('---')
    if len(parts) < 3:
        print(f"Неожиданная структура в {file_path}")
        return None
    text = parts[0].strip()
    answer_part = parts[1].strip()
    explanation_part = parts[2].strip() if len(parts) > 2 else ''
    answer = ''
    if 'Ответ:' in answer_part:
        answer = answer_part.split('Ответ:', 1)[1].strip()
    else:
        answer = answer_part
    explanation = ''
    if 'Пояснение:' in explanation_part:
        explanation = explanation_part.split('Пояснение:', 1)[1].strip()
    else:
        explanation = explanation_part
    return {
        'text': text,
        'options': [],
        'answer': answer,
        'explanation': explanation
    }

def parse_json_file(file_path):
    """Парсит JSON-файл задания."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {
        'text': data.get('task', '') or data.get('text', ''),
        'options': data.get('options', []),
        'answer': data.get('answer', '') or data.get('correct', ''),
        'explanation': data.get('explanation', '')
    }

def main():
    all_tasks = []
    # Проходим по всем подпапкам в dataset_benchmark
    for folder in TASKS_ROOT.iterdir():
        if not folder.is_dir():
            continue
        # Проверяем, что имя папки начинается с числа от 13 до 19 и содержит точку
        parts = folder.name.split('.')
        if len(parts) < 2:
            continue
        try:
            num = int(parts[0])
        except ValueError:
            continue
        if not (13 <= num <= 19):
            continue

        print(f"Обработка папки {folder.name}")
        # Внутри папки ищем все файлы
        for file_path in folder.glob('*'):
            if file_path.suffix == '.json':
                task = parse_json_file(file_path)
            else:
                # Попробуем как текстовый
                task = parse_text_file(file_path)
            if task and task['text']:
                all_tasks.append(task)
                print(f"  Добавлено: {file_path.name}")

    if not all_tasks:
        print("Задания не найдены. Проверьте путь и наличие файлов.")
        return

    # Записываем CSV
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['topic_id', 'difficulty', 'text', 'options', 'answer', 'explanation'])
        for task in all_tasks:
            writer.writerow([
                TOPIC_ID,
                0.5,
                task['text'],
                json.dumps(task['options'], ensure_ascii=False),
                task['answer'],
                task['explanation']
            ])

    print(f"Собрано {len(all_tasks)} заданий. Сохранено в {OUTPUT_CSV}")

if __name__ == '__main__':
    main()