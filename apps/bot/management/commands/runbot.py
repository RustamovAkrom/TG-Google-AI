import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from django.core.management.base import BaseCommand
from core import settings


from apps.bot.middlewares import (
    SubscriptionMiddleware,
    TypingMiddleware,
    IsUserActiveMiddleware,
)

from apps.bot.handlers import *


# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # можно DEBUG для более подробного
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class Command(BaseCommand):
    help = "Запуск Telegram-бота (aiogram)"

    def handle(self, *args, **options):
        logger.info("Запуск бота через Django management command.")
        asyncio.run(self.start_bot())

    async def start_bot(self):

        # Intialization Bot
        logger.debug("Инициализация бота с токеном из настроек.")
        bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML"),
        )

        # Creating Dispatcher
        logger.debug("Создание диспетчера и FSM-хранилища.")
        dp = Dispatcher(storage=MemoryStorage())

        # Register Global Router which included all routers
        logger.debug("Регистрация всех роутеров с хендлерами.")
        dp.include_router(global_router)

        # Register Middleware
        dp.message.middleware(SubscriptionMiddleware())
        dp.message.middleware(TypingMiddleware())
        # dp.message.middleware(IsUserActiveMiddleware())

        self.stdout.write(self.style.SUCCESS("🤖 Бот запущен. Ожидание сообщений..."))
        logger.info("Aiogram бот запущен и ожидает входящие сообщения.")

        try:
            await dp.start_polling(bot)
        except (KeyboardInterrupt, SystemExit):
            self.stdout.write(self.style.WARNING("⛔ Бот остановлен."))
            logger.warning("Получен сигнал остановки. Бот завершает работу.")
        except Exception as e:
            logger.exception(f"Произошла непредвиденная ошибка: {e}")
