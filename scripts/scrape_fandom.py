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
    "Percival_Dumbledore": "Percival_Dumbledore",
    "Nagini": "Nagini.txt",
    # Персонажи ФТ
    "Porpentina_Goldstein": "Porpentina_Goldstein.txt",
    "Newton_Scamander": "Newton_Scamander.txt",
    "Queenie_Goldstein": "Queenie_Goldstein.txt",
    "Theseus_Scamander": "Theseus_Scamander.txt",
    "Yusuf_Kama": "Yusuf_Kama.txt",
    "Leta_Lestrange": "Leta_Lestrange.txt",
    "Gellert_Grindelwald": "Gellert_Grindelwald.txt",
    "Ariana_Dumbledore": "Ariana_Dumbledore.txt",
    "Aurelius_Dumbledore": "Aurelius_Dumbledore.txt",
    "Obscurial": "Obscurial.txt",
    "Aberforth_Dumbledore": "Aberforth_Dumbledore.txt",
    # Книги
    "Harry_Potter_and_the_Philosopher's_Stone": "Harry_Potter_and_the_Philosopher's_Stone.txt",
    "Harry_Potter_and_the_Chamber_of_Secrets": "Harry_Potter_and_the_Chamber_of_Secrets.txt",
    "Harry_Potter_and_the_Prisoner_of_Azkaban": "Harry_Potter_and_the_Prisoner_of_Azkaban.txt",
    "Harry_Potter_and_the_Goblet_of_Fire": "Harry_Potter_and_the_Goblet_of_Fire.txt",
    "Harry_Potter_and_the_Order_of_the_Phoenix": "Harry_Potter_and_the_Order_of_the_Phoenix.txt",
    "Harry_Potter_and_the_Half-Blood_Prince": "Harry_Potter_and_the_Half-Blood_Prince.txt",
    "Harry_Potter_and_the_Deathly_Hallows": "Harry_Potter_and_the_Deathly_Hallows.txt",
    # Фильмы
    "Harry_Potter_and_the_Philosopher's_Stone": "Harry_Potter_and_the_Philosopher's_Stone.txt",
    "Harry_Potter_and_the_Chamber_of_Secrets": "Harry_Potter_and_the_Chamber_of_Secrets.txt",
    "Harry_Potter_and_the_Prisoner_of_Azkaban": "Harry_Potter_and_the_Prisoner_of_Azkaban.txt",
    "Harry_Potter_and_the_Goblet_of_Fire": "Harry_Potter_and_the_Goblet_of_Fire.txt",
    "Harry_Potter_and_the_Order_of_the_Phoenix": "Harry_Potter_and_the_Order_of_the_Phoenix.txt",
    "Harry_Potter_and_the_Half-Blood_Prince": "Harry_Potter_and_the_Half-Blood_Prince.txt",
    "Harry_Potter_and_the_Deathly_Hallows:_Part_1": "Harry_Potter_and_the_Deathly_Hallows:_Part_1.txt",
    "Harry_Potter_and_the_Deathly_Hallows:_Part_2": "Harry_Potter_and_the_Deathly_Hallows:_Part_1.txt",
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