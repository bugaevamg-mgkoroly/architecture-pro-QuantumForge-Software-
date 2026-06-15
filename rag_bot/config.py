"""Конфигурация бота. Загрузка переменных окружения."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR",
                                os.path.join(BASE_DIR, "knowledge_base"))
INDEX_DIR = os.getenv("INDEX_DIR", os.path.join(BASE_DIR, "index"))
LOGS_DIR = os.getenv("LOGS_DIR", os.path.join(BASE_DIR, "logs"))

# RAG settings
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
TOP_K = 4