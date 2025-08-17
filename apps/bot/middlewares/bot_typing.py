from aiogram import BaseMiddleware
from aiogram.types import Message
import asyncio

class TypingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        async def typing_loop():
            while True:
                try:
                    await event.bot.send_chat_action(event.chat.id, "typing")
                    await asyncio.sleep(4)
                except asyncio.CancelledError:
                    break

        typing_task = asyncio.create_task(typing_loop())
        try:
            return await handler(event, data)  # выполняем хендлер
        finally:
            typing_task.cancel()  # останавливаем "печатает..."

__all__ = ("TypingMiddleware",)
