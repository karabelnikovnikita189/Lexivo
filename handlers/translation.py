import sqlite3

from aiogram import Router, F, types


from database import DB_PATH
from google import genai
from services.gemini_service import (
    gemini_client
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
router = Router()
from database import is_user_vip

@router.callback_query(F.data == "smart_translate")
async def process_smart_translation(callback: types.CallbackQuery):
    await callback.answer("Перевожу...")

    user_id = callback.from_user.id
    if not is_user_vip(user_id):
        await callback.message.answer(
            "💎 Перевод доступен только пользователям Lexivo PRO.\n\n"
            "Откройте раздел «✨ Подписка» для получения доступа."
        )

        return

    
    original_text = callback.message.text
    
    prompt = (
        "Проанализируй следующий текст. "
        "Если текст преимущественно на русском языке — переведи его на АНГЛИЙСКИЙ.\n"
        "Если текст преимущественно на английском или любом другом языке — переведи его на РУССКИЙ.\n\n"
        "Важно: Сохрани абсолютно все форматирование (жирный шрифт, переносы строк), "
        "структуру, заголовки и эмодзи в точности как в оригинале!\n\n"
        f"Текст для перевода:\n{original_text}"
    )

    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        
        translated_text = response.text

        user_id = callback.from_user.id
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE transcriptions
            SET translated = ?
            WHERE id = (
                SELECT MAX(id)
                FROM transcriptions
                WHERE user_id = ?
            )
            """,
        (
        translated_text,
        user_id
        )
)

        conn.commit()
        conn.close()


        
        
        # Меняем клавиатуру после перевода: убираем кнопку перевода, оставляем кнопку удаления
        builder = InlineKeyboardBuilder()

        builder.button(
            text="📄 PDF",
            callback_data="export_pdf"
        )

        builder.button(
            text="📝 Word",
            callback_data="export_docx"
    )

        builder.button(
            text="🗑 Удалить",
            callback_data="delete_msg"
        )           

        builder.adjust(2, 1)
        
        await callback.message.edit_text(
            f"🌐 **[Перевод]**\n\n{translated_text}",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        await callback.message.answer(f"⚠️ Ошибка при переводе: {e}")