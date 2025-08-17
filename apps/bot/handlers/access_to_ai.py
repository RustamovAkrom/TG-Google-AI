from aiogram import Router, filters, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from apps.bot.services import set_telegram_user_access_token


router = Router()


class AccessTokenProcess(StatesGroup):
    waiting_for_access_key = State()


@router.message(filters.Command("set_access_key"))
async def set_access_key_state(message: types.Message, state: FSMContext):
    await state.set_state(AccessTokenProcess.waiting_for_access_key)
    await message.answer("🔑 Пожалуйста, введите ваш API ключ Google AI:")


@router.message(AccessTokenProcess.waiting_for_access_key)
async def set_access_key_handle(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    access_key = message.text.strip()

    is_success = await set_telegram_user_access_token(user_id, access_key)
    if is_success:
        await state.clear()
        await message.answer(
            "✅ Ваш персональный API ключ сохранён! Теперь бот будет использовать его."
        )
    else:
        await state.clear()
        await message.answer("❌ваш ключ доступа не сохранился")
