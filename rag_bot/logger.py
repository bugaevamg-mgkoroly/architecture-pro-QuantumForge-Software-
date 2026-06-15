"""Логирование запросов к RAG-боту."""

import json
import os
from datetime import datetime

from bot.config import LOGS_DIR


def log_query(
    query: str,
    answer: str,
    chunks: list,
    status: str = "success",
    interface: str = "unknown",
):
    """Записать лог запроса в JSONL-файл.

    Args:
        query: текст запроса пользователя
        answer: ответ бота
        chunks: найденные чанки (список Document)
        status: статус обработки (success/filtered/error/no_answer)
        interface: источник запроса (repl/api/telegram)
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_path = os.path.join(LOGS_DIR, "queries.jsonl")

    sources = []
    for chunk in chunks:
        meta = getattr(chunk, "metadata", {})
        sources.append({
            "source": meta.get("source", "unknown"),
            "chunk_id": meta.get("chunk_id", ""),
            "preview": (chunk.page_content[:100] + "...")
                       if hasattr(chunk, "page_content") else "",
        })

    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "answer_length": len(answer),
        "status": status,
        "interface": interface,
        "chunks_found": len(chunks),
        "sources": sources,
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")