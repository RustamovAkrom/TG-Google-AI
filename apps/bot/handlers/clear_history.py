from aiogram import Router, types, filters

from apps.bot.services import get_telegram_user, clear_history

router = Router()

@router.message(filters.Command("clear_history"))
async def clear_user_history(message: types.Message):
    user_id = message.from_user.id
    telegram_user = await get_telegram_user(user_id=user_id)

    if not telegram_user:
        await message.answer("❌ Пользователь не найден.")
        return
    
    await clear_history(user_id)
    await message.answer("🗑 История чата успешно очищена.")
