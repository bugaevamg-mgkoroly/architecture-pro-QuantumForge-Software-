"""Поиск по FAISS-индексу."""

import os
from langchain_community.vectorstores import FAISS
from bot.config import INDEX_DIR, TOP_K
from bot.embeddings import get_embeddings


_vectorstore = None


def get_vectorstore() -> FAISS:
    """Загрузить или вернуть кэшированный FAISS-индекс."""
    global _vectorstore
    if _vectorstore is None:
        embeddings = get_embeddings()
        _vectorstore = FAISS.load_local(
            INDEX_DIR,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    return _vectorstore


def reload_vectorstore():
    """Перезагрузить индекс (после обновления)."""
    global _vectorstore
    _vectorstore = None
    return get_vectorstore()


def get_retriever(k: int = TOP_K):
    """Получить retriever для RAG-пайплайна."""
    vs = get_vectorstore()
    return vs.as_retriever(search_kwargs={"k": k})


def search(query: str, k: int = TOP_K) -> list:
    """Поиск релевантных документов по запросу."""
    vs = get_vectorstore()
    return vs.similarity_search(query, k=k)