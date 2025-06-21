from gradio_client import Client
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import json
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

# Настройки  
TELEGRAM_TOKEN = os.getenv("THETMYTELEGRAM_TOKEN")
HF_TOKEN = os.getenv("THETMYHF_TOKEN")

# Подключение к модели Qwen/Qwen2.5
client = Client("Qwen/Qwen2-72B-Instruct", hf_token=HF_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Команда /start получена")
    await update.message.reply_text("Привет! Я искуственный интеллект. Задайте вопрос.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logging.info(f"Получено сообщение: {user_message}")

    try:
        # Отправка запроса к модели через API-точку /model_chat
        result = client.predict(
            query=user_message,          #system_message="Ты — дружелюбный ассистент. ты будешь получать названия продуктов и их колличество или вес и ты должен расчитать колличество каллорий",
		    history=[],
		    system="Ты — дружелюбный ассистент. отвечай на русском языке. ты будешь получать названия продуктов и их колличество или вес и ты должен расчитать колличество каллорий",
		    api_name="/model_chat"
        )
        logging.info(f"Полный ответ API: {json.dumps(result, indent=4, ensure_ascii=False)}")  # Логируем полный ответ

        # Новый, более безопасный способ извлечения ответа
        try:
            # Попытка извлечь ответ по ожидаемому пути
            answer = result[1][0][1]
            # Дополнительная проверка, что ответ — это строка
            if not isinstance(answer, str):
                answer = "Ошибка: Ответ модели не является текстом."
                logging.warning(f"Ответ модели не является строкой: {answer}")

        except (IndexError, TypeError) as e:
            answer = "Ошибка: Не удалось разобрать ответ от модели (неожиданная структура)."
            logging.error(f"Не удалось разобрать ответ. Структура: {result}. Ошибка: {e}")

    except Exception as e:
        logging.error(f"Ошибка при обращении к API: {e}")
        answer = f"Произошла ошибка: {str(e)}"

    if answer.strip():
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text("Не понял вопрос. Переформулируйте, пожалуйста.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))  # Добавлен обработчик /start
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
