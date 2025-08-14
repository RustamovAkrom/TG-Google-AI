from aiogram import Router, types, filters, F, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from google.api_core import exceptions

from django.core.files import File
from django.conf import settings

from apps.bot.services import (
    get_telegram_user,
    create_history,
    clear_history,
    genai_client,
    genai_chat_generation,
)
from apps.bot.utils import safe_send_markdown, safe_send_plain
from core.settings import GEMINI_API_KEY
import asyncio
import os
from io import BytesIO


router = Router()

class ChatStates(StatesGroup):
    waiting_for_ai = State()


@router.message(ChatStates.waiting_for_ai)
async def reject_while_processing(message: types.Message, state: FSMContext):
    msg = await message.answer("⚠ Пожалуйста, подождите, бот генерирует ответ...")
    await state.update_data(wait_msg_id=msg.message_id)


@router.message(F.text)
async def handle_text(message: types.Message, state: FSMContext):
    await state.set_state(ChatStates.waiting_for_ai)

    system_message = await message.answer("🔁 Обрабатываю ваш запрос, подождите...")
    
    user_message = message.text
    user_id = message.from_user.id

    try:
        telegram_user = await get_telegram_user(user_id=user_id)
        # History by user
        await create_history(
            telegram_user=telegram_user,
            role="user",
            message_type="text",
            content=user_message
        )
        api_key = telegram_user.access_token or GEMINI_API_KEY

        if not api_key:
            await message.answer(
                "🔑 У вас не установлен API ключ для Google AI.\n"
                "Отправьте команду /set_access_key чтобы его установить."
            )
            return
        
        client = await genai_client(api_key=api_key) # User api key or system api key

        response_ai = await genai_chat_generation(
            client=client, 
            user_id=user_id, 
            message=user_message
        )
        response_ai_to_text = response_ai.text

        if hasattr(response_ai, '__await__'):
            response_ai_to_text = await response_ai_to_text

        # History by model
        await create_history(
            telegram_user=telegram_user,
            role="model",
            message_type="text",
            content=response_ai_to_text
        )
        await system_message.delete()

        data = await state.get_data()

        if "wait_msg_id" in data:
            try:
                await message.bot.delete_message(message.chat.id, data["wait_msg_id"])
            except Exception:
                pass
        await safe_send_plain(message, response_ai_to_text)
    

    except exceptions.PermissionDenied:
        await message.answer("❌ Доступ запрещён. Проверьте, верен ли API ключ и есть ли у него нужные права.")
        await state.clear()
        return

    except exceptions.ResourceExhausted:
        await message.answer("⚠ Квота по вашему API ключу исчерпана. Попробуйте позже или используйте другой ключ.")
        await state.clear()
        return

    except exceptions.NotFound:
        await message.answer("❌ API ключ не найден. Проверьте, что вы скопировали его полностью.")
        await state.clear()
        return

    except exceptions.InvalidArgument:
        await message.answer("❌ Некорректный API ключ. Проверьте формат ключа.")
        await state.clear()
        return

    except Exception as e:
        await message.reply(f"⚠ Ошибка при получении ответа AI: {e}")
        return

    finally:
        await state.clear()

MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".mp4": "video/mp4",
    ".mp3": "audio/mpeg",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
    # добавь по необходимости
}

async def find_extension_from_handle_media(
    message: types.Message
) -> tuple[types.PhotoSize | types.Video | types.Audio | types.Document | None, str | None, str | None, str | None]:

    if message.photo:
        media = message.photo[-1]
        message_type = "image"
        extension = ".jpg"
    elif message.video:
        media = message.video
        message_type = "video"
        extension = ".mp4"
    elif message.audio:
        media = message.audio
        message_type = "audio"
        extension = ".mp3"
    elif message.document:
        media = message.document
        message_type = "document"
        extension = os.path.splitext(media.file_name or "")[1] or ""
    else:
        return None, None, None

    return media, message_type, extension


@router.message(F.content_type.in_({"photo", "video", "audio", "document"}))
async def handle_media(message: types.Message, state: FSMContext):
    await state.set_state(ChatStates.waiting_for_ai)

    user_id = message.from_user.id
    caption_text = (message.caption or "").strip()

    try:
        telegram_user = await get_telegram_user(user_id=user_id)

        # Определяем медиа и расширение
        media, message_type, extension = await find_extension_from_handle_media(message)

        if not (media and message_type and extension):
            await message.answer("❌ Не удалось определить тип файла.")
            return
        
        # Генерируем имя файла
        file_name = f"{media.file_unique_id}{extension}"
        relative_path = os.path.join("history_files", file_name)
        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        # Скачиваем файл и сохраняем в Django FileField
        file_info = await message.bot.get_file(media.file_id)
        await message.bot.download_file(file_info.file_path, destination=absolute_path)

        if not os.path.exists(absolute_path):
            await message.answer("❌ Не удалось сохранить файл. Проверь MEDIA_ROOT.")
            return

        with open(absolute_path, "rb") as f:
            django_file = File(f, name=os.path.basename(relative_path))

            # Сохраняем в историю
            await create_history(
                telegram_user=telegram_user,
                role="user",
                message_type=message_type,
                content=caption_text,
                file=django_file
            )

        system_message = await message.answer(f"📁 {message_type.capitalize()} получен. Загружаю в AI...")

        # Клиент AI
        api_key = telegram_user.access_token or GEMINI_API_KEY
        if not api_key:
            await message.answer(
                "🔑 У вас не установлен API ключ для Google AI.\n"
                "Отправьте команду /set_access_key чтобы его установить."
            )
            return
        
        client = await genai_client(api_key=api_key)

        # Генерация ответа (файл подхватится из истории)
        response_ai = await genai_chat_generation(
            client=client,
            user_id=user_id,
            message=caption_text or ""
        )

        if response_ai.text:
            await create_history(
                telegram_user=telegram_user,
                role="model",
                message_type="text",
                content=response_ai.text
            )
            await system_message.delete()
            await safe_send_plain(message, response_ai.text)
        else:
            await message.answer("🤔 AI не вернул текст.")

    except Exception as e:
        await message.answer(f"⚠ Ошибка при обработке файла: {e}")
    finally:
        await state.clear()
