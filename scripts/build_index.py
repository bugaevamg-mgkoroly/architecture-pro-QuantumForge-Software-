
# -*- coding: utf-8 -*-
"""
Задание 3: Создание векторного индекса FAISS.

Загружает документы из knowledge_base/, разбивает на чанки,
генерирует эмбеддинги и сохраняет FAISS-индекс.
"""

import io
import os
import sys
import time

# Принудительный UTF-8 для Windows-консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from bot.config import KNOWLEDGE_BASE_DIR, INDEX_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from bot.embeddings import get_embeddings


def load_documents(kb_dir: str) -> list[Document]:
    """Загрузить все текстовые документы из директории."""
    documents = []
    for filename in sorted(os.listdir(kb_dir)):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(kb_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if text:
            documents.append(Document(
                page_content=text,
                metadata={"source": filename, "title": filename.replace(".txt", "")},
            ))
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """Разбить документы на чанки."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    # Добавляем chunk_id в метаданные
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    return chunks


def build_index(chunks: list[Document], index_dir: str):
    """Создать и сохранить FAISS-индекс."""
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs(index_dir, exist_ok=True)
    vectorstore.save_local(index_dir)
    return vectorstore


def test_index(vectorstore, queries: list[str]):
    """Тестовые запросы к индексу."""
    print("\n--- Тестовые запросы ---")
    for query in queries:
        results = vectorstore.similarity_search(query, k=2)
        print(f"\nЗапрос: {query}")
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "?")
            preview = doc.page_content[:150].replace("\n", " ")
            print(f"  [{i}] {source}: {preview}...")


def main():
    print("=== Создание FAISS-индекса ===\n")

    # 1. Загрузка документов
    print(f"Загрузка документов из {KNOWLEDGE_BASE_DIR}...")
    documents = load_documents(KNOWLEDGE_BASE_DIR)
    print(f"  Загружено документов: {len(documents)}")

    if not documents:
        print("Ошибка: документы не найдены!")
        sys.exit(1)

    # 2. Разбиение на чанки
    t0 = time.time()
    print(f"\nРазбиение на чанки (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks = split_documents(documents)
    split_time = time.time() - t0
    print(f"  Создано чанков: {len(chunks)}")
    print(f"  Время разбиения: {split_time:.2f} сек")

    # 3. Создание индекса
    t0 = time.time()
    print(f"\nСоздание FAISS-индекса в {INDEX_DIR}...")
    vectorstore = build_index(chunks, INDEX_DIR)
    index_time = time.time() - t0
    print(f"  Индекс создан и сохранён!")
    print(f"  Время генерации (эмбеддинги + индекс): {index_time:.2f} сек")

    # 4. Тестовые запросы
    test_queries = [
        "Кто является создателем Патронуса?",
        "Что такое Шармбатон?",
        "Расскажи о Avada Kedavra",
    ]
    test_index(vectorstore, test_queries)

    total_time = split_time + index_time
    print(f"\n--- Статистика ---")
    print(f"  Документов: {len(documents)}")
    print(f"  Чанков: {len(chunks)}")
    print(f"  Время разбиения: {split_time:.2f} сек")
    print(f"  Время генерации индекса: {index_time:.2f} сек")
    print(f"  Общее время: {total_time:.2f} сек")

    print("\n=== Готово! ===")


if __name__ == "__main__":
    main()