"""RAG-пайплайн: запрос → эмбеддинг → поиск → промпт → LLM → ответ."""

from langchain_openai import ChatOpenAI

from bot.config import OPENAI_API_KEY, LLM_MODEL, TOP_K
from bot.retriever import search
from bot.prompts import RAG_PROMPT_TEMPLATE
from bot.security import filter_chunks, sanitize_query
from bot.logger import log_query


def get_llm() -> ChatOpenAI:
    """Получить экземпляр LLM."""
    return ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=0.3,
    )


def ask(query: str, interface: str = "unknown") -> dict:
    """Обработать вопрос пользователя через RAG-пайплайн.

    Args:
        query: вопрос пользователя
        interface: источник запроса (repl/api/telegram)

    Returns:
        dict с ключами: answer, sources, status
    """
    # Проверка на инъекцию в запросе
    clean_query = sanitize_query(query)
    if not clean_query:
        log_query(query, "", [], status="filtered", interface=interface)
        return {
            "answer": "Запрос отклонён системой безопасности.",
            "sources": [],
            "status": "filtered",
        }

    # Поиск релевантных чанков
    raw_chunks = search(clean_query, k=TOP_K)

    # Фильтрация вредоносных чанков
    safe_chunks = filter_chunks(raw_chunks)

    if not safe_chunks:
        log_query(query, "", raw_chunks, status="no_chunks", interface=interface)
        return {
            "answer": "К сожалению, я не нашёл релевантной информации в базе знаний.",
            "sources": [],
            "status": "no_chunks",
        }

    # Формируем контекст из безопасных чанков
    context = "\n\n---\n\n".join(
        chunk.page_content for chunk in safe_chunks
    )

    # Генерация ответа через LLM
    llm = get_llm()
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=clean_query)
    response = llm.invoke(prompt)
    answer = response.content

    # Логирование
    sources = [
        chunk.metadata.get("source", "unknown")
        for chunk in safe_chunks
    ]
    log_query(query, answer, safe_chunks, status="success", interface=interface)

    return {
        "answer": answer,
        "sources": list(set(sources)),
        "status": "success",
    }