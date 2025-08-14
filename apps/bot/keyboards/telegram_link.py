from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message


async def send_telegram_link(message: Message, title: str, webapp_url: str, description: str):
    """
    Отправляет сообщение с кнопкой на Telegram-ссылку.

    :param message: объект aiogram Message
    :param title: текст кнопки
    :param link: ссылка
    :param description: текст перед кнопкой
    """
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=title, web_app={"url": webapp_url})]
        ]
    )

    await message.answer(description, reply_markup=kb)
