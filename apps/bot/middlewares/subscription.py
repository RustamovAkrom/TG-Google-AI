from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram import Bot
from django.conf import settings

from apps.bot.keyboards.subscribe import get_subscribe_keyboard


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        bot: Bot = data["bot"]
        user_id: int = event.from_user.id

        for channel in settings.REQUIRED_CHANNELS:
            try:
                member = await bot.get_chat_member(channel, user_id)
                if member.status in ["left", "kicked"]:
                    await event.answer(
                        f"🚫 Для использования бота подпишитесь на канал(ы):)",
                        reply_markup=get_subscribe_keyboard(),
                    )
                    return  # Останавливаем выполнение хендлера

            except Exception as e:
                await event.answer(
                    "❌ Бот не может проверить подписку.\n\n"
                    "🔹 Убедитесь, что:\n"
                    "1️⃣ Бот добавлен в канал в качестве администратора.\n"
                    "2️⃣ У канала есть @username или бот в нём присутствует.\n"
                    "3️⃣ Вы подписаны на канал.\n\n"
                    "После этого снова отправьте команду.",
                    reply_markup=get_subscribe_keyboard(),
                )
                return

        return await handler(event, data)


__all__ = ("SubscriptionMiddleware",)
