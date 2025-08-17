# apps/bot/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.bot.models import New, TelegramUser
from aiogram import Bot
import asyncio
from django.conf import settings


@receiver(post_save, sender=New)
def send_news_to_users(sender, instance: New, created, **kwargs):
    if instance.is_published:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

        telegram_users = TelegramUser.objects.all()

        for user in telegram_users:
            try:
                bot.send_message(
                    user.user_id, f"📰 {instance.title}\n\n{instance.text}"
                )
            except Exception as e:
                print(f"Ошибка отправки пользователю {user.user_id}: {e}")
        bot.session.close()
