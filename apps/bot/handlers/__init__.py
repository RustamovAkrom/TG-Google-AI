from aiogram import Router
from .chats import router as chats_router # noqa
from .start import router as start_router # noqa
from .access_to_ai import router as access_to_ai_router # noqa
from .clear_history import router as clear_history_router

from apps.bot.middlewares.subscription import SubscriptionMiddleware

global_router = Router(name="Global Bot")
global_router.include_routers(
    clear_history_router,
    start_router,
    access_to_ai_router,
    chats_router, # it is required to last
)

__all__ = ("global_router", )