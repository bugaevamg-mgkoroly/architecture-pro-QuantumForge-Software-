"""Работа с эмбеддингами. Инициализация модели."""

from langchain_openai import OpenAIEmbeddings
from bot.config import OPENAI_API_KEY, EMBEDDING_MODEL


def get_embeddings() -> OpenAIEmbeddings:
    """Получить экземпляр модели эмбеддингов."""
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )