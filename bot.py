import os
import sqlite3
import asyncio
import time
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
from aiogram.types import FSInputFile
from datetime import date
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import *
from database import *
from keyboards import *
from handlers.translation import (router as translation_router)
from services.gemini_service import (gemini_client)
from services.whisper_service import (groq_client)
from handlers.payments import (router as payments_router)
from handlers.audio import (router as audio_router)
from handlers.commands import (router as commands_router)

# 1. Загрузка конфигурации

dp = Dispatcher()

from handlers.exports import router as exports_router

bot = Bot(token=BOT_TOKEN)

# Загрузка шрифта
pdfmetrics.registerFont(
    TTFont(
        "NotoSans",
        "NotoSans-Regular.ttf"
    )
)

# Обработчик кнопки удаления
@dp.callback_query(F.data == "delete_msg")
async def process_delete(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer("Сообщение удалено")

async def main():
    init_db()
    print("Бот успешно запущен!")
    dp.include_router(commands_router)
    dp.include_router(exports_router)
    dp.include_router(translation_router)
    dp.include_router(payments_router)
    dp.include_router(audio_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


