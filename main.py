import pandas as pd
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from datetime import datetime
import asyncio
import logging
import os
import nest_asyncio

# Применяем nest_asyncio
nest_asyncio.apply()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Токен вашего бота Telegram
TOKEN = "7676551853:AAH-pZ_GpLUHBQOyOhkUy2iWMhWTse6kH9w"  # Замените на ваш реальный токен

# Функция для создания клавиатуры главного меню
def get_main_menu_keyboard():
    keyboard = [
        ["Список дежурных"]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False
    )
    return reply_markup

# Функция для обработки команды /start и кнопки "Главное меню"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    reply_markup = get_main_menu_keyboard()
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Выберите одно из действий ниже:",
        reply_markup=reply_markup,
    )

# Функция для обработки команды /getdata и кнопки "Список дежурных"
async def get_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        excel_path = "График дежурных.xlsx"
        if not os.path.exists(excel_path):
            await update.message.reply_text("Файл 'График дежурных.xlsx' не найден.")
            return

        df = pd.read_excel(excel_path)

        required_columns = {"ФИО", "Позиция"}
        if not required_columns.issubset(df.columns):
            await update.message.reply_text("Файл не содержит необходимых столбцов: 'ФИО', 'Позиция'.")
            return

        today_date = datetime.now().strftime("%Y-%m-%d")
        employees_info = df.head(3)
        response = f"Сегодняшняя дата: {today_date}\n\n"

        for index, row in employees_info.iterrows():
            response += f"ФИО: {row['ФИО']}; Позиция: {row['Позиция']}\n"

        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        await update.message.reply_text(f"Произошла ошибка при загрузке данных: {e}")

# Функция для обработки ошибок (опционально)
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Произошла незапланированная ошибка:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик текстовых сообщений для кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Список дежурных":
        await get_data(update, context)
    else:
        await update.message.reply_text("Пожалуйста, используйте кнопки для взаимодействия.")

async def main() -> None:
    # Убедитесь, что вы заменили 'YOUR_TELEGRAM_BOT_TOKEN_HERE' на реальный токен
    #application = ApplicationBuilder().token(TOKEN).build()
    application = ApplicationBuilder().token("7676551853:AAE7gNQCdPj_sR2tFkH6epM3aIzRs2pXJ8o").build()
    # Регистрация команд
    application.add_handler(CommandHandler("start", start))

    # Если вы хотите добавить команду /getdata, раскомментируйте следующую строку:
    # application.add_handler(CommandHandler("getdata", get_data))

    # Регистрация обработчика кнопок
    button_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_buttons)
    application.add_handler(button_handler)

    # Регистрация обработчика ошибок (опционально)
    application.add_error_handler(error_handler)

    logger.info("Бот запущен и ожидает сообщений.")

    # Запуск бота
    await application.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен вручную.")
