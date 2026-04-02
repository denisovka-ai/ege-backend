import requests
from bs4 import BeautifulSoup
import time
import json
import csv
from urllib.parse import urljoin

BASE_URL = "https://openfipi.devinf.ru"

# Сопоставление предметов с topic_id из вашей таблицы topics
SUBJECTS = {
    'math': 1,   # математика
    'rus': 2,    # русский язык
}

# Задержка между запросами (сек)
DELAY = 2

def get_page_tasks(subject: str, page_num: int):
    """Парсит одну страницу списка заданий"""
    url = f"{BASE_URL}/{subject}/tasks/page/{page_num}"
    print(f"Загрузка {url}")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Найти все блоки заданий (пробуем возможные классы)
    tasks_blocks = soup.select('.task, .question, .exercise, .task-item')
    if not tasks_blocks:
        print(f"Не найдены блоки заданий на {url}. Проверьте селекторы.")
        return []

    tasks = []
    for block in tasks_blocks:
        # Текст вопроса
        text_elem = block.select_one('.task__text, .question-text, .task-text')
        if not text_elem:
            # может быть в обычном <p> внутри блока
            text_elem = block.find('p')
        text = text_elem.get_text(strip=True) if text_elem else ''

        # Варианты ответов
        options = []
        for opt in block.select('.answer, .task__answer, .option'):
            opt_text = opt.get_text(strip=True)
            if opt_text:
                options.append(opt_text)

        # Правильный ответ (обычно в элементе с классом correct)
        answer_elem = block.select_one('.correct, .task__correct, .answer-correct')
        answer = answer_elem.get_text(strip=True) if answer_elem else ''

        # Пояснение (если есть)
        explanation_elem = block.select_one('.explanation, .task__explanation')
        explanation = explanation_elem.get_text(strip=True) if explanation_elem else ''

        # Если текст вопроса пустой, пропускаем
        if not text:
            continue

        tasks.append({
            'text': text,
            'options': options,
            'answer': answer,
            'explanation': explanation,
        })

    return tasks


def parse_subject(subject: str, max_pages: int = 30):
    """Парсит все страницы предмета до пустой страницы или max_pages"""
    all_tasks = []
    for page in range(1, max_pages + 1):
        tasks = get_page_tasks(subject, page)
        if not tasks:
            break
        all_tasks.extend(tasks)
        print(f"{subject}: страница {page} -> {len(tasks)} заданий, всего {len(all_tasks)}")
        time.sleep(DELAY)
    return all_tasks


def save_to_csv(tasks, subject, topic_id):
    """Сохраняет задания в CSV для загрузки в базу"""
    filename = f"questions_{subject}.csv"
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['topic_id', 'difficulty', 'text', 'options', 'answer', 'explanation'])
        for task in tasks:
            # difficulty можно выставить по умолчанию 0.5, потом корректировать
            difficulty = 0.5
            writer.writerow([
                topic_id,
                difficulty,
                task['text'],
                json.dumps(task['options'], ensure_ascii=False),
                task['answer'],
                task['explanation']
            ])
    print(f"Сохранено {len(tasks)} заданий в {filename}")


def main():
    for subject, topic_id in SUBJECTS.items():
        print(f"\n=== Парсинг {subject} ===")
        tasks = parse_subject(subject, max_pages=30)
        if tasks:
            save_to_csv(tasks, subject, topic_id)
        else:
            print(f"Заданий для {subject} не найдено.")


if __name__ == '__main__':
    main()