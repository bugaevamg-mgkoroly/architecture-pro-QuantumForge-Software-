# QuantumForge Knowledge Base — RAG Bot

RAG-бот для корпоративной базы знаний компании QuantumForge Software.

## Стек

- **LLM:** OpenAI GPT-4o-mini
- **Эмбеддинги:** OpenAI text-embedding-3-small
- **Векторная БД:** FAISS
- **Фреймворк:** LangChain
- **Интерфейсы:** Telegram, FastAPI, REPL

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp .env.example .env
# Заполнить OPENAI_API_KEY и TELEGRAM_BOT_TOKEN
```

### 3. Подготовка базы знаний

```bash
# Парсинг фандома (опционально — документы уже есть)
python scripts/scrape_fandom.py

# Замена терминов Marvel → QuantumForge
python scripts/replace_terms.py

# Создание FAISS-индекса
python scripts/build_index.py
```

### 4. Запуск

```bash
# REPL (консоль)
python -m bot.repl

# FastAPI
python -m bot.api

# Telegram
python -m bot.telegram_bot
```

### 5. Docker

```bash
docker compose up --build
```

## Тестирование

```bash
# Юнит-тесты
python -m pytest tests/

# Автоматическая оценка (золотой набор)
python scripts/evaluate.py
```

## Структура проекта

```
├── bot/              # Основной код бота
├── scripts/          # Скрипты подготовки данных
├── knowledge_base/   # Документы базы знаний
├── index/            # FAISS-индекс
├── tests/            # Тесты
├── research/         # Исследование моделей
├── diagrams/         # PlantUML-диаграммы
└── logs/             # Логи запросов
```