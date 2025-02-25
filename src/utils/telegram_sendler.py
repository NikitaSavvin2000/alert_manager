import os
import yaml
import logging

from io import BytesIO
from aiogram import Bot
from pathlib import Path
from config import API_TOKEN
from aiogram.types.input_file import BufferedInputFile


home_path = os.getcwd()
YAML_FILE = f"{home_path}/src/chats_ids.yaml"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)


def load_chat_ids():
    """Загружает chat_id из YAML файла."""
    try:
        with open(YAML_FILE, "r") as file:
            data = yaml.safe_load(file) or {}
            return data.get("chat_ids", [])
    except FileNotFoundError:
        return []


async def send_notifications(text_message, html_path):
    chat_ids = load_chat_ids()
    text_message = text_message

    html_path = Path(html_path)
    if not html_path.exists():
        logging.error(f"Файл {html_path} не найден!")
        return

    with open(html_path, "rb") as file:
        file_content = file.read()

    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id, text_message, parse_mode="HTML")

            file_bytes = BytesIO(file_content)
            file_bytes.seek(0)
            buffered_file = BufferedInputFile(file_bytes.read(), filename="attachment.html")
            await bot.send_document(chat_id, document=buffered_file)
            logging.info(f"Уведомление отправлено пользователю {chat_id}")
        except Exception as e:
            logging.error(f"Ошибка при отправке уведомления пользователю {chat_id}: {e}")


async def telegram_sendler(text_message, html_path):
    await send_notifications(text_message, html_path)
    await bot.session.close()
