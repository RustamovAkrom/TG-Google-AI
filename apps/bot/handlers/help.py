from aiogram import Router, types
from aiogram.filters import Command
from apps.bot.keyboards.telegram_link import send_telegram_link

router = Router()


@router.message(Command("help"))
async def help_command(message: types.Message):
    text = text = (
        "📚 <b>Справка по боту</b>\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/set_access_key - Получить доступ к ИИ\n"
        "/clear_history - Очистить историю запросов\n\n"
    )
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=False)
    title =  "📄 Документация"
    url = "https://github.com/RustamovAkrom/TG-Google-AI/blob/main/docs/getting_google_ai_key.md"
    description = "Как получить API-ключ Google AI Studio"
    await send_telegram_link(message,title, url,  description)
