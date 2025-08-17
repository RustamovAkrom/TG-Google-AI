import os

from aiogram import types


async def find_extension_from_handle_media(
    message: types.Message,
) -> tuple[
    types.PhotoSize | types.Video | types.Audio | types.Document | None,
    str | None,
    str | None,
    str | None,
]:

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

__all__ = ("find_extension_from_handle_media", )
