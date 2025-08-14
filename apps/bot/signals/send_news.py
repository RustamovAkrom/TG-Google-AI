# apps/bot/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.bot.models import News, TelegramUser
from aiogram import Bot
import asyncio
from django.conf import settings

@receiver(post_save, sender=News)
def send_news_to_users(sender, instance: News, created, **kwargs):
    if instance.is_published:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        async def _send():
            users = TelegramUser.objects.all()
            for user in users:
                try:
                    await bot.send_message(user.chat_id, f"📰 {instance.title}\n\n{instance.text}")
                except Exception as e:
                    print(f"Ошибка отправки пользователю {user.chat_id}: {e}")
            await bot.session.close()

        asyncio.run(_send())
