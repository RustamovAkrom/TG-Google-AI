from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram import Bot
from apps.bot.services import get_telegram_user


class IsUserActiveMiddleware(BaseMiddleware):
    async def __call__(
            self, 
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], 
            event: Message, 
            data: Dict[str, Any]
        ) -> Any:
        bot: Bot = data["bot"]
        user_id: int = event.from_user.id

        telegram_user = await get_telegram_user(user_id)
        if telegram_user.is_active:
            return await handler(event, data)
        else:
            await event.answer(
                f"You can not use bot because that blocked."
            )
            return

__all__ = ("IsUserActiveMiddleware", )
