from aiogram import Router, F, Bot, types
from aiogram.types import (
    LabeledPrice,
    PreCheckoutQuery
)

from config import STARS_PRICE
from database import set_vip_status

router = Router()

DONATIONS = {
"support_10": 10,
"support_50": 50,
"support_100": 100,
"support_500": 500,
}


@router.callback_query(F.data == "buy_pro_stars")
async def send_invoice_handler(
    callback: types.CallbackQuery
):
    print("BUY CLICK")
    bot = callback.bot

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="💎 Lexivo PRO",
        description=(
            "Безлимитные распознавания, "
            "PDF, Word, перевод и история."
        ),
        payload="pro_status_payload",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Lexivo PRO",
                amount=STARS_PRICE
            )
        ]
    )

    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout(
    pre_checkout_query: PreCheckoutQuery
):
    bot = pre_checkout_query.bot

    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )


@router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload
    if payload == "pro_status_payload":

        set_vip_status(user_id)

        await message.answer(
            "🎉 Оплата прошла успешно!\n\n"
            "💎 Lexivo PRO активирован.\n\n"
            "♾️ Безлимитные возможности\n"
            "📄 PDF экспорт\n"
            "📝 Word экспорт\n"
            "🌍 Перевод текста\n"
            "📚 История записей\n\n"
            "Спасибо за поддержку проекта ❤️"
        )

        return

    if payload.startswith("support_"):

        amount = payload.split("_")[1]

        await message.answer(
            f"❤️ Спасибо за поддержку проекта!\n\n"
            f"Вы отправили: ⭐ {amount}\n\n"
            f"Благодаря таким пользователям Lexivo становится лучше."
        )

        return

@router.callback_query(
    F.data.startswith("support_")
)
async def support_project(
    callback: types.CallbackQuery
):

    amount = DONATIONS[
        callback.data
    ]

    bot = callback.bot

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="⭐ Поддержка Lexivo",
        description="Спасибо за поддержку проекта ❤️",
        payload=f"support_{amount}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label=f"Поддержка на {amount} ⭐",
                amount=amount
            )
        ]
    )

    await callback.answer()