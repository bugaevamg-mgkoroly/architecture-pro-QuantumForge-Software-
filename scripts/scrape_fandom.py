"""
Задание 2: Парсинг Harry Potter Fandom Wiki.

Скрипт скачивает 30+ статей с harrypotter.fandom.com,
очищает от HTML-разметки и сохраняет как текстовые файлы.
"""

import io
import os
import re
import sys
import time

# Принудительный UTF-8 для Windows-консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import requests
from bs4 import BeautifulSoup

# Список страниц для скачивания
PAGES = {
    # Персонажи
    "Harry_Potter": "Harry_Potter.txt",
    "Hermione_Granger": "Hermione_Granger.txt",
    "Ronald_Weasley": "Ronald_Weasley.txt",
    "Ginevra_Weasley": "Ginevra_Weasley.txt",
    "Neville_Longbottom": "Neville_Longbottom.txt",
    "Luna_Lovegood": "Luna_Lovegood.txt",
    "Tom_Riddle": "Tom_Riddle.txt",
    "Draco_Malfoy": "Draco_Malfoy.txt",
    "Albus_Dumbledore": "Albus_Dumbledore.txt",
    # Книги
    "Harry_Potter_and_the_Philosopher%27s_Stone": "Harry_Potter_and_the_Philosopher%27s_Stone.txt",
  
    # Фильмы
   
}

BASE_URL = "https://harrypotter.fandom.com/wiki/"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")


def clean_text(soup: BeautifulSoup) -> str:
    """Извлечь и очистить текст статьи."""
    # Удаляем ненужные элементы
    for tag in soup.find_all(["script", "style", "nav", "footer", "header",
                               "aside", "table", "sup", "figure"]):
        tag.decompose()

    # Находим основной контент
    content = soup.find("div", {"class": "mw-parser-output"})
    if not content:
        content = soup.find("div", {"id": "content"})
    if not content:
        return ""

    # Извлекаем текст
    text = content.get_text(separator="\n")

    # Очистка
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Пропускаем навигационные элементы
        if line in ("[]", "Edit", "Edit source", "Contents"):
            continue
        if line.startswith("Categories"):
            break
        lines.append(line)

    text = "\n".join(lines)
    # Убираем множественные переносы строк
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def scrape_page(page_name: str) -> str:
    """Скачать и очистить одну страницу."""
    url = BASE_URL + page_name
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    return clean_text(soup)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = len(PAGES)

    for i, (page_name, filename) in enumerate(PAGES.items(), 1):
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(filepath):
            print(f"[{i}/{total}] Пропуск {filename} (уже существует)")
            continue

        print(f"[{i}/{total}] Скачивание {page_name}...")
        try:
            text = scrape_page(page_name)
            if text:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"  -> Сохранено: {filename} ({len(text)} символов)")
            else:
                print(f"  -> Предупреждение: пустой текст для {page_name}")
        except Exception as e:
            print(f"  -> Ошибка: {e}")

        # Пауза между запросами
        time.sleep(1.5)

    print(f"\nГотово! Документы сохранены в {OUTPUT_DIR}")


if __name__ == "__main__":
    main()