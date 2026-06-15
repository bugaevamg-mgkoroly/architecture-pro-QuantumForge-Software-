"""Telegram-интерфейс для RAG-бота."""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from bot.config import TELEGRAM_BOT_TOKEN
from bot.rag_chain import ask

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start."""
    await update.message.reply_text(
        "Привет! Я бот корпоративной базы знаний QuantumForge Software.\n\n"
        "Задайте мне вопрос о персонажах, технологиях, локациях "
        "или событиях из вселенной QuantumForge.\n\n"
        "Команды:\n"
        "/start — начало работы\n"
        "/help — справка\n"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help."""
    await update.message.reply_text(
        "Просто отправьте мне вопрос, и я найду ответ в базе знаний.\n\n"
        "Примеры вопросов:\n"
        "• Кто такой Ferron Kael?\n"
        "• Что такое Nexus Shards?\n"
        "• Расскажи о Velundra\n"
        "• Что произошло во время Nexus War?\n"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстового сообщения."""
    query = update.message.text.strip()
    if not query:
        return

    # Отправляем индикатор "печатает..."
    await update.message.chat.send_action("typing")

    try:
        result = ask(query, interface="telegram")
        response = result["answer"]

        if result["sources"]:
            response += f"\n\n📚 Источники: {', '.join(result['sources'])}"

        if result["status"] == "filtered":
            response = "⚠️ Запрос отклонён системой безопасности."

    except Exception as e:
        logger.error(f"Ошибка обработки запроса: {e}")
        response = "Произошла ошибка при обработке запроса. Попробуйте позже."

    await update.message.reply_text(response)


def main():
    """Запуск Telegram-бота."""
    if not TELEGRAM_BOT_TOKEN:
        print("Ошибка: TELEGRAM_BOT_TOKEN не задан в .env")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram-бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()