import os
import yaml
import asyncio
import logging

from config import API_TOKEN
from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


home_path = os.getcwd()


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
YAML_FILE = f"{home_path}/src/chats_ids.yaml"

def load_chat_ids():
    """Загружает chat_id из YAML файла."""
    try:
        with open(YAML_FILE, "r") as file:
            data = yaml.safe_load(file) or {}
            return data.get("chat_ids", [])
    except FileNotFoundError:
        return []


def save_chat_ids(chat_ids):
    """Сохраняет chat_id в YAML файл."""
    with open(YAML_FILE, "w") as file:
        yaml.dump({"chat_ids": chat_ids}, file)


def add_chat_id(chat_id):
    """Добавляет chat_id в YAML, если его там нет."""
    chat_ids = load_chat_ids()
    if chat_id not in chat_ids:
        chat_ids.append(chat_id)
        save_chat_ids(chat_ids)


def remove_chat_id(chat_id):
    """Удаляет chat_id из YAML, если он там есть."""
    chat_ids = load_chat_ids()
    if chat_id in chat_ids:
        chat_ids.remove(chat_id)
        save_chat_ids(chat_ids)


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Включить уведомления")],
        [KeyboardButton(text="❌ Выключить уведомления")]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Управляй уведомлениями с помощью кнопок ниже:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "✅ Включить уведомления")
async def enable_notifications(message: types.Message):
    add_chat_id(message.chat.id)
    await message.answer("🔔 Уведомления включены!")


@dp.message(lambda message: message.text == "❌ Выключить уведомления")
async def disable_notifications(message: types.Message):
    remove_chat_id(message.chat.id)
    await message.answer("🔕 Уведомления выключены.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
