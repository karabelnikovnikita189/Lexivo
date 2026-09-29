from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_transcription_by_id
from datetime import datetime
from database import is_user_vip
from keyboards import get_support_inline_keyboard


from database import (
    get_user_stats,
    get_last_transcriptions
)

from keyboards import (
    get_main_keyboard,
    get_buy_inline_keyboard
)

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "🎙️ Добро пожаловать в Lexivo\n\n"
        "Я превращаю голосовые сообщения, видео и аудиофайлы в понятный текст.\n\n"
        "Что умею:\n\n"
        "✅ Расшифровка речи\n"
        "✅ Краткие выжимки\n"
        "✅ Перевод текста\n"
        "✅ Экспорт в PDF и Word\n"
        "✅ История записей\n\n"
        "🚀 Просто отправьте аудио или видео для начала работы.",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "👤 Мой профиль")
@router.message(Command("profile"))
async def cmd_profile(message: types.Message):
    stats = get_user_stats(message.from_user.id)
    # Если пользователь не VIP, добавляем inline-кнопку для быстрой покупки
    if "PRO" not in stats:
        await message.answer(stats, reply_markup=get_buy_inline_keyboard())
    else:
        await message.answer(stats)


@router.message(F.text == "❓ Помощь")
async def cmd_help(message: types.Message):
    await message.answer(
        "❓ Помощь по Lexivo\n\n"
    
        "🎙️ Что можно отправлять:\n"
        "• Голосовые сообщения\n"
        "• Аудиофайлы\n"
        "• Видео\n"
        "• Видеокружки\n\n"

        "⚡ Что делает бот:\n"
        "✅ Расшифровывает речь в текст\n"
        "✅ Создает краткую выжимку\n"
        "✅ Выделяет ключевые мысли\n"
        "✅ Переводит текст\n"
        "✅ Экспортирует в PDF и Word\n"
        "✅ Сохраняет историю записей\n\n"

        "📚 Полезные команды:\n"
        "/start — главное меню\n"
        "/profile — информация об аккаунте\n"
        "/history — история расшифровок\n"
        "/buy — оформление подписки\n\n"

        "🚀 Для начала просто отправьте аудио или видео."
    )


@router.message(F.text == "✨ Подписка")
async def show_subscription(message: types.Message):
    user_id = message.from_user.id
    if is_user_vip(user_id):
        await message.answer(
            "💎 Lexivo PRO уже активирован\n\n"
            "Спасибо за поддержку проекта ❤️\n\n"
            "Если хотите поддержать дальнейшее развитие Lexivo, "
            "можете отправить любое количество Telegram Stars.",
            reply_markup=get_support_inline_keyboard()
        )
        return
    await message.answer(
        "✨ Lexivo PRO\n\n"

        "Ваш персональный помощник для работы с аудио и видео.\n\n"

        "Что входит:\n\n"

        "♾️ Безлимитные распознавания\n"
        "📄 Экспорт PDF\n"
        "📝 Экспорт Word\n"
        "🌍 Перевод текста\n"
        "📚 История записей\n"
        "🎙️ Поддержка голосовых, аудио и видео\n\n"

        "💰 Стоимость: 1 Telegram Stars\n\n"

        "После оплаты возможности активируются моментально.",
        reply_markup=get_buy_inline_keyboard()
    )

@router.message(F.text == "📚 История")
@router.message(Command("history"))
async def cmd_history(message: types.Message):

    if not is_user_vip(message.from_user.id):
        await message.answer(
            "💎 История записей доступна только пользователям Lexivo PRO.\n\n"
            "Оформите подписку в разделе «✨ Подписка»."
    )
        return

    rows = get_last_transcriptions(
        message.from_user.id
    )

    if not rows:
        await message.answer(
            "📚 История пока пуста."
        )
        return

    text = "📚 Последние расшифровки:\n\n"

    for row in rows:

        try:
            date_str = datetime.strptime(
                row[2],
                "%Y-%m-%d %H:%M:%S"
            ).strftime("%d.%m.%Y • %H:%M")
        except:
            date_str = row[2]

        builder = InlineKeyboardBuilder()

        builder.button(
            text="📖 Открыть",
            callback_data=f"open_{row[0]}"
        )

        await message.answer(
            f"🎙️ {row[1]}\n"
            f"📅 {date_str}",
            reply_markup=builder.as_markup()
        )

@router.callback_query(
    F.data.startswith("open_")
)
async def open_history_item(
    callback: types.CallbackQuery
):

    transcription_id = int(
        callback.data.split("_")[1]
    )

    row = get_transcription_by_id(
        transcription_id
    )

    if not row:
        await callback.answer(
            "Запись не найдена",
            show_alert=True
        )
        return

    title = row[0]
    transcription = row[1]
    summary = row[2]
    translated = row[3]

    result = (
        f"🎙️ {title}\n\n"
        f"{transcription}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
    )

    if translated:
        result += (
            f"🌍 Перевод\n\n"
            f"{translated}"
        )
    else:
        result += summary

    await callback.message.answer(
        result
    )

    await callback.answer()

