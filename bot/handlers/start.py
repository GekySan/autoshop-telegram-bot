from aiogram import types, Dispatcher
from aiogram.filters import CommandStart

from bot.keyboards.inline import create_main_keyboard
from bot.utils.db import save_user, get_user_language
from bot.utils.payment import init_addresses
from bot.utils.lang import get_translation

async def command_start_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name else "❌"
    username = message.from_user.username if message.from_user.username else "❌"
    lang_code = get_user_language(user_id)

    btc_address, eth_address, ltc_address = init_addresses(user_id)

    save_user(user_id, first_name, last_name, username, btc_address, eth_address, ltc_address)

    user_id = message.from_user.id
    main_keyboard = create_main_keyboard(user_id)
    welcome_message = get_translation(lang_code, "start.welcome_message", first_name=first_name)
    main_keyboard = create_main_keyboard(user_id)

    await message.answer(welcome_message, reply_markup=main_keyboard)

def register_handlers(dp: Dispatcher):
    dp.message(CommandStart())(command_start_handler)
