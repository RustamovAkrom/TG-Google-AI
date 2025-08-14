from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.conf import settings


def get_subscribe_keyboard():
    kb = InlineKeyboardBuilder()
    for ch in settings.REQUIRED_CHANNELS:
        if "https://t.me" not in ch:
            kb.button(text=f"📢 Подписаться {ch}", url=f"https://t.me/{ch.lstrip('@')}")
        else:
            kb.button(text=f"📢 Подписаться {ch}", url=ch)
    return kb.as_markup()
