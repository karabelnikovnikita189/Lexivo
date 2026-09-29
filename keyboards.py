from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
    InlineKeyboardBuilder
)




def get_main_keyboard():
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="👤 Мой профиль"),
        KeyboardButton(text="✨ Подписка")
    )

    builder.row(
        KeyboardButton(text="📚 История"),
        KeyboardButton(text="❓ Помощь")
    )

    return builder.as_markup(
        resize_keyboard=True
    )

# Кнопка умного перевода и удаления и экспорта
def get_action_inline_keyboard():
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
        text="🌐 Перевести",
        callback_data="smart_translate"
    )

    builder.button(
        text="🗑 Удалить",
        callback_data="delete_msg"
    )

    builder.adjust(2, 2)

    return builder.as_markup()

def get_buy_inline_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="👑 Оформить PRO",
        callback_data="buy_pro_stars"
    )

    return builder.as_markup()


def get_support_inline_keyboard():

    builder = InlineKeyboardBuilder()

    builder.button(
        text="⭐ 10",
        callback_data="support_10"
    )

    builder.button(
        text="⭐ 50",
        callback_data="support_50"
    )

    builder.button(
        text="⭐ 100",
        callback_data="support_100"
    )

    builder.button(
        text="⭐ 500",
        callback_data="support_500"
    )

    builder.adjust(2, 2)

    return builder.as_markup()
