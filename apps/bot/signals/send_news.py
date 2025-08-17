# apps/bot/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.bot.models import New
from apps.bot.services import get_telegram_users
from aiogram import Bot
import asyncio
from django.conf import settings
from asgiref.sync import async_to_sync


async def _send_news(instance: New):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    telegram_users = await get_telegram_users()

    for user in telegram_users:
        try:
            await bot.send_message(
                user.user_id, f"{instance.title}\n\n{instance.text}", parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Ошибка отправки пользователю {user.user_id}: {e}")

    await bot.session.close()


@receiver(post_save, sender=New)
def send_news_to_users(sender, instance: New, created, **kwargs):
    if instance.is_published:
        async_to_sync(_send_news)(instance)
