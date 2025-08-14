from aiogram import Router
from aiogram.filters import CommandStart
from aiogram import types

from apps.bot.services import create_telegram_user, update_telegram_user, get_telegram_user

router = Router()


@router.message(CommandStart())
async def start_bot(message: types.Message):
    user_id = message.from_user.id

    telegram_user = await get_telegram_user(user_id=user_id)

    if not telegram_user:
        telegram_user = await create_telegram_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code
        )
        text = (
            f"**Salom {telegram_user.first_name} botga hush kelibsiz qisqacha malumot berib otaman bu botda siz suniy Intelekt (Google GenAI) bilan muloqat qila olasiz.**\n"
            f"**Imkoniyatlar:**\n"
            f"**Text - Matin korinishida muloqat qilish.**"
            f"**Audio - Audio filar ustida ish olib borish.**"
            f"**Video - Video filar ustida ish olib borish.**"
            f"**Photo - Rasimlar ustida ish olib borish.**"
            f"**Document - Har hil boshqa hujatlarni qayta ishlash.**"
            f"__Qoshimcha malumot olish uchun /help komandasini kiriting ->__"
        )
        await message.answer(text, parse_mode="Markdown")
    else:
        telegram_user = await update_telegram_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code
        )
        await message.answer(
            f"{telegram_user.username} siz allaqachon royhattan otkansiz va botan foydalana olasiz."
        )
