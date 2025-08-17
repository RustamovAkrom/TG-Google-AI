from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from apps.bot.services import create_feedback

router = Router()


class FeedbackGroup(StatesGroup):
    message = State()


@router.message(filters.Command("feedback"))
async def feedback_handle(message: types.Message, state: FSMContext):
    await state.set_state(FeedbackGroup.message)
    await message.answer("🔑 Пожалуйста, введите ваш Feedback:")


@router.message(FeedbackGroup.message)
async def create_feedback_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    message = message.text

    await create_feedback(user_id, message)
