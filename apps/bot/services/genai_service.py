from asgiref.sync import sync_to_async
from django.conf import settings
import google.genai as genai
from google.genai import types
from .models_service import get_chat_histories, get_user_ai_config
import os
import mimetypes


def trim_history(contents, max_chars=settings.GEMINI_MAX_HISTORY_CHARS):
    total = 0
    trimmed = []
    for c in reversed(contents):  # берём с конца (самые свежие)
        size = sum(len(p.text) for p in c.parts if hasattr(p, "text"))
        if total + size > max_chars:
            break
        trimmed.append(c)
        total += size
    return list(reversed(trimmed))


def build_genai_config(user_settings):
    return types.GenerateContentConfig(
        max_output_tokens=user_settings.max_output_tokens or settings.GEMINI_MAX_OUTPUT_TOKENS,
        top_k=user_settings.top_k or settings.GEMINI_TOP_K,
        top_p=user_settings.top_p or settings.GEMINI_TOP_P,
        temperature=user_settings.temperature or settings.GEMINI_TEMPERATURE,
        seed=user_settings.seed or settings.GEMINI_SEED,
        tools=[
            (
                types.Tool(url_context=types.UrlContext())
                if t.get("type") == "url_context"
                else (
                    types.Tool(google_search=types.GoogleSearch())
                    if t.get("type") == "google_search"
                    else None
                )
            )
            for t in user_settings.tools
        ],
        safety_settings=[
            types.SafetySetting(category=s["category"], threshold=s["threshold"])
            for s in user_settings.safety_settings
        ],
    )


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
    config=None,
):
    
    history = await get_chat_histories(user_id=user_id, limit=settings.GEMINI_MAX_HISTORY_LIMIT)
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
                mime_type = (
                    mimetypes.guess_type(abs_path)[0] or "application/octet-stream"
                )
                parts.append(types.Part.from_bytes(data=data, mime_type=mime_type))

        if parts:
            contents.append(types.UserContent(parts=parts))

    # Добавляем текущий запрос (message может быть текст или файл)
    user_parts = [types.Part(text=message)] if isinstance(message, str) else []
    # ... handle if message includes file similarly ...
    if user_parts:
        contents.append(types.UserContent(parts=user_parts))
    
    # Trip Content
    contents = trim_history(contents, max_chars=settings.GEMINI_MAX_HISTORY_CHARS)

    if config:
        chat = await _create_chat_sync(client, model, config, history=contents)
    else:
        ai_settings = await get_user_ai_config(user_id=user_id)
        config = build_genai_config(ai_settings)
        chat = await _create_chat_sync(
            client, ai_settings.model_name, config, history=contents
        )

    response = await _send_message_sync(chat, message=message)
    return response
