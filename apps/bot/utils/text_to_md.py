import re
from typing import List, Tuple

from aiogram.exceptions import TelegramBadRequest

# Ограничение Telegram на длину текста — безопасно используем чуть меньше.
MAX_CHUNK_SIZE = 4000

# Символы, которые нужно экранировать для MarkdownV2
_MD_V2_ESCAPE = r"_*[]()~`>#+-=|{}.!"

_md_v2_escape_re = re.compile(f"([{re.escape(_MD_V2_ESCAPE)}])")


def escape_md_v2(text: str) -> str:
    """Escape text for Telegram MarkdownV2 (for non-code parts)."""
    if not text:
        return text
    # replace backslashes first to avoid double-escaping
    text = text.replace("\\", "\\\\")
    return _md_v2_escape_re.sub(r"\\\1", text)


def split_preserve_codeblocks(text: str) -> List[Tuple[str, str]]:
    """
    Разбивает входной текст на список кортежей (kind, content),
    где kind == "text" или "code". Код определяется тройными backticks ```...```.
    """
    pattern = re.compile(
        r"```(?:([\w+-]+)\n)?(.*?)```", re.DOTALL
    )  # захват языка (опционально) и содержимого
    parts: List[Tuple[str, str]] = []
    last = 0
    for m in pattern.finditer(text):
        if m.start() > last:
            parts.append(("text", text[last : m.start()]))
        lang = m.group(1) or ""
        code = m.group(2) or ""
        # сохраняем вместе с языком — восстановим при отправке
        if lang:
            parts.append(("code", f"{lang}\n{code}"))
        else:
            parts.append(("code", code))
        last = m.end()
    if last < len(text):
        parts.append(("text", text[last:]))
    return parts


def chunk_parts(
    parts: List[Tuple[str, str]], max_size: int = MAX_CHUNK_SIZE
) -> List[str]:
    """
    Собирает готовые к отправке чанки, не разрывая код-блоки.
    Если один код-блок длиннее max_size — дробит его по строкам.
    """
    chunks: List[str] = []
    cur = ""

    def push_cur():
        nonlocal cur
        if cur:
            chunks.append(cur)
            cur = ""

    for kind, content in parts:
        if kind == "text":
            safe = escape_md_v2(content)
            # если текущий + safe влезают — добавляем; иначе дробим safe по словам
            if len(cur) + len(safe) <= max_size:
                cur += safe
            else:
                # пытаться ломать по переносам/пробелам
                segs = re.split(r"(\s+)", safe)
                for seg in segs:
                    if not seg:
                        continue
                    if len(cur) + len(seg) <= max_size:
                        cur += seg
                    else:
                        push_cur()
                        # если сегмент сам длиннее max_size, нужно резать его
                        while len(seg) > max_size:
                            chunks.append(seg[:max_size])
                            seg = seg[max_size:]
                        cur += seg
        else:  # code
            code_block = f"```\n{content}\n```"
            if len(code_block) <= max_size:
                # если не влезает в текущий, пушим текущий и добавляем код целиком
                if len(cur) + len(code_block) <= max_size:
                    cur += code_block
                else:
                    push_cur()
                    cur += code_block
            else:
                # код очень длинный — дробим его по строкам внутри блока
                push_cur()
                lines = content.splitlines(keepends=True)
                buf = ""
                for line in lines:
                    prospective = buf + line
                    if (
                        len(prospective) + 6 <= max_size
                    ):  # +6 for triple backticks and newlines
                        buf = prospective
                    else:
                        # flush current buf as a code block
                        chunks.append(f"```\n{buf}\n```")
                        buf = line
                if buf:
                    chunks.append(f"```\n{buf}\n```")
                cur = ""
    push_cur()
    return chunks


async def safe_send_markdown(message, text: str):
    """
    Отправляет текст в Telegram безопасно с MarkdownV2.
    При ошибке парсинга (TelegramBadRequest) — повторно отправляет проблемный кусок без parse_mode.
    """
    if not text:
        await message.answer("(пустой ответ)")
        return

    parts = split_preserve_codeblocks(text)
    chunks = chunk_parts(parts, MAX_CHUNK_SIZE)

    for chunk in chunks:
        try:
            await message.answer(chunk, parse_mode="MarkdownV2")
        except TelegramBadRequest as e:
            # Попытка диагностировать — если это проблема с парсингом сущностей,
            # отправим chunk как plain text (без parse_mode), чтобы гарантированно доставилось.
            try:
                await message.answer(chunk)  # plain text
            except Exception:
                # Last resort: разобьём chunk на мелкие части и отправим как plain text
                for i in range(0, len(chunk), 2000):
                    try:
                        await message.answer(chunk[i : i + 2000])
                    except Exception:
                        # ничего не делаем — мы не хотим, чтобы бот падал
                        pass


async def safe_send_plain(message, text, chunk_size=4000):
    """
    Отправляет текст без Markdown, разбивая длинные слова и сообщения.
    :param message: объект aiogram types.Message
    :param text: исходный текст
    :param chunk_size: максимальный размер одного сообщения
    """

    # Разбиваем длинные слова (> 50 символов) пробелами
    def split_long_words(t):
        return re.sub(r"(\S{50})(?=\S)", r"\1 ", t)

    text = split_long_words(text)

    # Разбиваем текст на куски до chunk_size
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    for chunk in chunks:
        try:
            await message.answer(chunk, parse_mode=None)  # Без parse_mode
        except TelegramBadRequest:
            # На всякий случай повторим с подрезкой
            await message.answer(chunk[: chunk_size - 50], parse_mode=None)
