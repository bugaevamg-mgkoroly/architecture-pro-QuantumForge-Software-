"""
Задание 5: Защита от промпт-инъекций.

Фильтрация вредоносных чанков и пользовательских запросов.
"""

import re

# Паттерны промпт-инъекций
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous\s+)?instructions",
    r"ignore\s+the\s+above",
    r"disregard\s+(all\s+)?(previous\s+)?instructions",
    r"forget\s+(all\s+)?(previous\s+)?instructions",
    r"override\s+(all\s+)?(previous\s+)?(instructions|rules)",
    r"system\s*:\s*",
    r"Output\s*:\s*[\"']",
    r"output\s+the\s+following",
    r"print\s+the\s+following",
    r"you\s+are\s+now\s+(a|an)\s+",
    r"new\s+instructions?\s*:",
    r"mandatory\s+system\s+override",
    r"admin\s+override",
    r"sudo\s+mode",
    r"пароль\s*(root|admin|системы)",
    r"игнорируй\s+(все\s+)?(предыдущие\s+)?инструкции",
    r"забудь\s+(все\s+)?(предыдущие\s+)?инструкции",
]

# Компилируем паттерны
_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def is_injection(text: str) -> bool:
    """Проверить текст на наличие промпт-инъекций."""
    for pattern in _compiled_patterns:
        if pattern.search(text):
            return True
    return False


def filter_chunks(chunks: list) -> list:
    """Отфильтровать чанки с промпт-инъекциями.

    Args:
        chunks: список Document объектов из LangChain

    Returns:
        отфильтрованный список без вредоносных чанков
    """
    safe_chunks = []
    for chunk in chunks:
        content = chunk.page_content if hasattr(chunk, "page_content") else str(chunk)
        if is_injection(content):
            source = getattr(chunk, "metadata", {}).get("source", "unknown")
            print(f"[SECURITY] Отфильтрован вредоносный чанк из: {source}")
        else:
            safe_chunks.append(chunk)
    return safe_chunks


def sanitize_query(query: str) -> str:
    """Очистить пользовательский запрос от инъекций.

    Returns:
        очищенный запрос или пустую строку при обнаружении инъекции
    """
    if is_injection(query):
        return ""
    return query.strip()