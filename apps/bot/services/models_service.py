from asgiref.sync import sync_to_async
from django.db.models import QuerySet
from apps.bot.models import TelegramUser, History, GenAISetting, Feedback


@sync_to_async
def create_telegram_user(
    user_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    language_code: str = None,
) -> TelegramUser:
    telegram_user, _ = TelegramUser.objects.get_or_create(
        user_id=user_id,
        defaults={
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "language_code": language_code,
        },
    )
    return telegram_user


@sync_to_async
def get_telegram_user(user_id: int) -> TelegramUser:
    return TelegramUser.objects.filter(user_id=user_id).first()


@sync_to_async
def get_telegram_users():
    return list(TelegramUser.objects.all())


@sync_to_async
def update_telegram_user(user_id: int, **kwargs) -> TelegramUser | None:
    telegram_user = TelegramUser.objects.filter(user_id=user_id).first()

    if telegram_user:
        for key, value in kwargs.items():
            if hasattr(telegram_user, key):
                setattr(telegram_user, key, value)
        telegram_user.save()
    return telegram_user


@sync_to_async
def deactivate_telegram_user(user_id: int) -> TelegramUser | None:
    telegram_user = TelegramUser.objects.filter(user_id=user_id).first()
    if telegram_user:
        telegram_user.is_active = False
        telegram_user.save()
        return telegram_user


@sync_to_async
def set_telegram_user_access_token(user_id: int, access_token: str) -> bool:
    try:
        telegram_user = TelegramUser.objects.filter(user_id=user_id).first()
        telegram_user.access_token = access_token
        telegram_user.save()
        return True
    except Exception as e:
        print(e)
        return False


@sync_to_async
def create_history(
    telegram_user: TelegramUser,
    role: str,
    message_type: str,
    content: str = None,
    file: str = None,
) -> History:
    History.objects.create(
        telegram_user=telegram_user,
        role=role,
        message_type=message_type,
        content=content,
        file=file,
    )


@sync_to_async
def get_chat_histories(user_id: int, limit: int = 10) -> list[History]:
    telegram_user = TelegramUser.objects.get(user_id=user_id)
    return (
        History.objects.filter(telegram_user=telegram_user)
        .select_related("telegram_user")
        .order_by("-created_at")[:limit][::-1]
    )


@sync_to_async
def clear_history(user_id: int) -> None:
    telegram_user = TelegramUser.objects.get(user_id=user_id)
    History.objects.filter(telegram_user=telegram_user).delete()


@sync_to_async
def get_user_ai_config(user_id: int) -> GenAISetting:
    telegram_user = TelegramUser.objects.get(user_id=user_id)
    genai_settings = GenAISetting.objects.filter(user=telegram_user).first()
    return genai_settings


@sync_to_async
def create_feedback(user_id: int, message: str) -> None:
    telegram_user = TelegramUser.objects.get(user_id=user_id)
    Feedback.objects.create(
        user=telegram_user,
        message=message
    )
