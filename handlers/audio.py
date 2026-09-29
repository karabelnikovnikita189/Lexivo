import os
import subprocess
import traceback

from aiogram import Router, F, types

from database import (
    check_and_update_limit,
    save_transcription
)

from keyboards import (
    get_action_inline_keyboard,
    get_buy_inline_keyboard
)

from services.gemini_service import (
    gemini_client
)

from services.whisper_service import (
    groq_client
)

from config import DAILY_FREE_LIMIT

router = Router()


@router.message(F.voice | F.audio | F.video_note | F.video)
async def handle_audio(message: types.Message):
    user_id = message.from_user.id
    bot = message.bot
    allowed, left = check_and_update_limit(user_id)

    if not allowed:
        await message.answer(
            "⚠️ Превышен дневной лимит!\n\n"
            f"Вы исчерпали {DAILY_FREE_LIMIT} бесплатных распознаваний на сегодня.\n\n"
            "👑 Оплатите подписку, чтобы снять ограничения!",
            reply_markup=get_buy_inline_keyboard()
        )
        return

    status_str = "Осталось попыток: " + ("Безлимит 👑" if left == 999 else str(left))
    status_msg = await message.answer(f"📥 Загружаю файл... ({status_str})")

    audio_path = None

    try:
        # Определяем тип файла
        if message.voice:
            file_obj = message.voice
            file_extension = "ogg"

        elif message.audio:
            file_obj = message.audio
            file_extension = "mp3"

        elif message.video_note:
            file_obj = message.video_note
            file_extension = "mp4"

        elif message.video:
            file_obj = message.video
            file_extension = "mp4"

        else:
            await status_msg.edit_text("❌ Неподдерживаемый формат файла.")
            return

        file_info = await bot.get_file(file_obj.file_id)

        input_path = f"temp_{file_obj.file_id}.{file_extension}"

        await bot.download_file(
            file_info.file_path,
            destination=input_path
        )

        transcription_file = input_path

        # Видео -> WAV
        if message.video or message.video_note:
            await status_msg.edit_text(
                "🎬 Видео получено. Извлекаю звук..."
            )

            audio_path = f"audio_{file_obj.file_id}.wav"

            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    input_path,
                    "-vn",
                    "-acodec",
                    "pcm_s16le",
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    audio_path,
                    "-y"
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )

            transcription_file = audio_path

        await status_msg.edit_text(
            "🎙️ Расшифровка"
        )

        with open(transcription_file, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(transcription_file, file.read()),
                model="whisper-large-v3",
                response_format="text"
            )

        transcribed_text = str(transcription).strip()

        title = transcribed_text[:50]

        try:
            title_response = gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=(
                    "Придумай короткий заголовок для текста.\n"
                    "Максимум 5 слов.\n"
                    "Без кавычек.\n"
                    "Только сам заголовок.\n\n"
                    f"{transcribed_text[:2000]}"
                )
            )

            if title_response.text:
                title = title_response.text.strip()

        except Exception:
            pass

        if not transcribed_text:
            await status_msg.edit_text(
                "❌ Не удалось распознать речь или аудио пустое."
            )
            return

        await status_msg.edit_text(
            "🧠 Генерирую краткую выжимку..."
        )

        prompt = (
    "Ты ассистент-аналитик.\n\n"
    "Верни результат строго в формате:\n\n"
    "📌 Суть\n"
    "Краткое описание.\n\n"
    "💡 Основные моменты\n"
    "• пункт 1\n"
    "• пункт 2\n"
    "• пункт 3\n\n"
    "✅ Задачи\n"
    "• задача 1\n"
    "• задача 2\n\n"
    f"Текст:\n{transcribed_text}"
    )

        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        summary_text = response.text
       


        if len(title) > 50:
            title += "..."

        

        save_transcription(
            user_id=user_id,
            title=title,
            transcription=transcribed_text,
            summary=summary_text
        )

        result_message = (
            f"🎙️ Расшифровка\n\n"
            f"{transcribed_text}\n\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"{summary_text}"
        )

        if len(result_message) > 4000:
            await status_msg.edit_text(
                f"🎙️ Расшифровка\n\n"
                f"{transcribed_text[:3700]}...\n"
                f"*(текст сокращён)*"
            )

            await message.answer(
                f"━━━━━━━━━━━━━━━━━\n{summary_text}",
                reply_markup=get_action_inline_keyboard()
            )
        else:
            await status_msg.edit_text(
                result_message,
                reply_markup=get_action_inline_keyboard()
            )

    except Exception as e:
        traceback.print_exc()

        await status_msg.edit_text(
            f"⚠️ Ошибка обработки:\n{e}"
        )

    finally:
        if 'input_path' in locals() and os.path.exists(input_path):
            os.remove(input_path)

        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
