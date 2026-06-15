"""
Задание 6: Автоматическое обновление FAISS-индекса.

Сканирует knowledge_base/ на новые/изменённые файлы,
обновляет индекс, логирует изменения.
"""

import hashlib
import io
import json
import os
import sys
import logging
from datetime import datetime

# Принудительный UTF-8 для Windows-консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from bot.config import KNOWLEDGE_BASE_DIR, INDEX_DIR, LOGS_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from bot.embeddings import get_embeddings
from scripts.build_index import split_documents

# Настройка логирования
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "update.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

HASHES_FILE = os.path.join(INDEX_DIR, "file_hashes.json")


def compute_file_hash(filepath: str) -> str:
    """Вычислить MD5-хеш файла."""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def load_hashes() -> dict:
    """Загрузить сохранённые хеши файлов."""
    if os.path.exists(HASHES_FILE):
        with open(HASHES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_hashes(hashes: dict):
    """Сохранить хеши файлов."""
    with open(HASHES_FILE, "w") as f:
        json.dump(hashes, f, indent=2)


def find_changed_files(kb_dir: str) -> tuple[list[str], list[str]]:
    """Найти новые и изменённые файлы.

    Returns:
        (new_files, modified_files) — списки путей
    """
    old_hashes = load_hashes()
    new_files = []
    modified_files = []

    for filename in os.listdir(kb_dir):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(kb_dir, filename)
        current_hash = compute_file_hash(filepath)

        if filename not in old_hashes:
            new_files.append(filepath)
        elif old_hashes[filename] != current_hash:
            modified_files.append(filepath)

    return new_files, modified_files


def update_index():
    """Обновить FAISS-индекс новыми/изменёнными документами."""
    logger.info("Начало обновления индекса")
    print(f"[{datetime.now().isoformat()}] Обновление индекса...")

    new_files, modified_files = find_changed_files(KNOWLEDGE_BASE_DIR)

    if not new_files and not modified_files:
        msg = "Изменений не обнаружено"
        logger.info(msg)
        print(f"  {msg}")
        return

    logger.info(f"Новых файлов: {len(new_files)}, изменённых: {len(modified_files)}")
    print(f"  Новых файлов: {len(new_files)}, изменённых: {len(modified_files)}")

    # Загрузка новых/изменённых документов
    all_changed = new_files + modified_files
    documents = []
    for filepath in all_changed:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if text:
            documents.append(Document(
                page_content=text,
                metadata={"source": filename, "title": filename.replace(".txt", "")},
            ))

    # Разбиение на чанки
    chunks = split_documents(documents)
    logger.info(f"Создано {len(chunks)} новых чанков")

    # Загрузка существующего индекса или создание нового
    embeddings = get_embeddings()
    if os.path.exists(os.path.join(INDEX_DIR, "index.faiss")):
        vectorstore = FAISS.load_local(
            INDEX_DIR, embeddings, allow_dangerous_deserialization=True
        )
        # Добавляем новые чанки
        vectorstore.add_documents(chunks)
        logger.info("Чанки добавлены в существующий индекс")
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)
        logger.info("Создан новый индекс")

    # Сохранение
    vectorstore.save_local(INDEX_DIR)

    # Обновление хешей
    hashes = load_hashes()
    for filepath in all_changed:
        filename = os.path.basename(filepath)
        hashes[filename] = compute_file_hash(filepath)
    save_hashes(hashes)

    msg = f"Индекс обновлён: +{len(chunks)} чанков из {len(all_changed)} файлов"
    logger.info(msg)
    print(f"  {msg}")


def main():
    try:
        update_index()
    except Exception as e:
        logger.error(f"Ошибка обновления: {e}", exc_info=True)
        print(f"  Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()