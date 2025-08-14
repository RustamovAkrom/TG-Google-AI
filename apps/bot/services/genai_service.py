from asgiref.sync import sync_to_async
from django.conf import settings
import google.genai as genai
from google.genai import types
from .models_service import get_chat_histories
import os
import asyncio
import mimetypes


@sync_to_async
def genai_client(api_key: str = None) -> genai.Client:
    return genai.Client(api_key=api_key)


@sync_to_async
def _create_chat_sync(client: genai.Client, model: str, config, history: list):
    return client.chats.create(model=model, config=config, history=history)


@sync_to_async
def _send_message_sync(chat, message):
    return chat.send_message(message=message)


async def genai_chat_generation(
    client: genai.Client,
    user_id: str,
    message: list | str,
    model: str = "gemini-2.0-flash",
    config=None
):

    history = await get_chat_histories(user_id=user_id)
    contents = []

    for h in history:
        parts = []
        if h.content:
            parts.append(types.Part(text=h.content))  # текстовая часть

        if h.file:
            abs_path = os.path.join(settings.MEDIA_ROOT, h.file.name)
            if os.path.exists(abs_path):
                with open(abs_path, "rb") as f:
                    data = f.read()
                mime_type = mimetypes.guess_type(abs_path)[0] or "application/octet-stream"
                parts.append(
                    types.Part.from_bytes(data=data, mime_type=mime_type)
                )

        if parts:
            contents.append(types.UserContent(parts=parts))

    # Добавляем текущий запрос (message может быть текст или файл)
    user_parts = [types.Part(text=message)] if isinstance(message, str) else []
    # ... handle if message includes file similarly ...
    if user_parts:
        contents.append(types.UserContent(parts=user_parts))

    chat = await _create_chat_sync(client, model, config, history=contents)
    response = await _send_message_sync(chat, message=message)
    return response
