"""
Задание 2: Замена терминов Marvel → QuantumForge.

Скрипт загружает словарь замен из terms_map.json
и применяет его ко всем документам в knowledge_base/.
"""

import io
import json
import os
import re
import sys

# Принудительный UTF-8 для Windows-консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
TERMS_MAP_PATH = os.path.join(KB_DIR, "terms_map.json")


def load_terms_map() -> dict:
    """Загрузить словарь замен."""
    with open(TERMS_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def replace_terms_in_text(text: str, terms_map: dict) -> str:
    """Заменить все термины в тексте.

    Замены применяются от длинных к коротким,
    чтобы избежать частичных замен.
    """
    # Сортируем по длине ключа (от длинных к коротким)
    sorted_terms = sorted(terms_map.items(), key=lambda x: len(x[0]), reverse=True)

    for original, replacement in sorted_terms:
        # Используем регулярное выражение для точного совпадения слов
        pattern = re.escape(original)
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def main():
    terms_map = load_terms_map()
    print(f"Загружено {len(terms_map)} замен из {TERMS_MAP_PATH}")

    txt_files = [f for f in os.listdir(KB_DIR) if f.endswith(".txt")]
    print(f"Найдено {len(txt_files)} документов в {KB_DIR}\n")

    total_replacements = 0

    for filename in sorted(txt_files):
        filepath = os.path.join(KB_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            original_text = f.read()

        new_text = replace_terms_in_text(original_text, terms_map)

        # Подсчёт замен
        replacements = 0
        for original in terms_map:
            replacements += len(re.findall(re.escape(original), original_text, re.IGNORECASE))

        if replacements > 0:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_text)
            print(f"  {filename}: {replacements} замен")
            total_replacements += replacements
        else:
            print(f"  {filename}: без изменений")

    print(f"\nВсего замен: {total_replacements}")
    print("Готово!")


if __name__ == "__main__":
    main()