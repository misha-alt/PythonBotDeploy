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
client = Client("Qwen/Qwen2.5", hf_token=HF_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Команда /start получена")
    await update.message.reply_text("Привет! Я искуственный интеллект. Задайте вопрос.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logging.info(f"Получено сообщение: {user_message}")

    try:
        # Отправка запроса к модели через API-точку /model_chat
        result = client.predict(
            query=user_message,
            history=[],
            system="Ты — дружелюбный ассистент. ты будешь получать названия продуктов и их колличество или вес и ты должен расчитать колличество каллорий",
            radio="72B",
            api_name="/model_chat"
        )
        logging.info(f"Полный ответ API: {json.dumps(result, indent=4, ensure_ascii=False)}")  # Логируем полный ответ

        # Обработка формата ответа
        if isinstance(result, tuple) and len(result) > 1:
            history = result[1]
            if isinstance(history, list) and len(history) > 0:
                # История — это список списков, берем первый внутренний список
                inner_history = history[0]
                if isinstance(inner_history, list) and len(inner_history) > 1:
                    # Последний элемент внутреннего списка — это ответ модели
                    last_message = inner_history[-1]
                    if isinstance(last_message, dict) and 'text' in last_message:
                        answer = last_message['text']
                    else:
                        answer = "Ошибка: Неверный формат ответа."
                else:
                    answer = "Ошибка: Неверный формат ответа."
            else:
                answer = "Ошибка: Неверный формат ответа."
        else:
            answer = "Ошибка: Неверный формат ответа."

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        answer = f"Произошла ошибка: {str(e)}"

    if answer.strip():
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text("Не понял вопрос. Переформулируйте, пожалуйста.")

# Запуск бота плоывра
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))  # Добавлен обработчик /start
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
