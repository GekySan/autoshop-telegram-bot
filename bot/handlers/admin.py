from aiogram import types, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command

import asyncio

from bot.config import ADMIN_IDS
from bot.utils.db import get_all_user_ids, get_user_language
from bot.handlers.gift import create_gift_handler

from bot.utils.lang import get_translation

async def dm_all_handler(message: types.Message):
    user_id = message.from_user.id
    lang_code = get_user_language(user_id)

    unauthorized_command = get_translation(lang_code, "admin.unauthorized_command")
    provide_message = get_translation(lang_code, "admin.provide_message")
    message_sent = get_translation(lang_code, "admin.message_sent")

    if str(message.from_user.id) not in ADMIN_IDS:
        await message.reply(unauthorized_command)
        return

    if not message.text.startswith('/dm_all '):
        await message.reply(provide_message)
        return

    user_ids = get_all_user_ids()
    non_admin_user_ids = [user_id for user_id in user_ids if str(user_id) not in ADMIN_IDS]
    message_to_send = message.text[len('/dm_all '):]

    tasks = [message.bot.send_message(user_id, message_to_send, parse_mode=ParseMode.HTML) for user_id in non_admin_user_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            print(f"Error sending message: {result}")

    await message.reply(message_sent)

def register_admin_handlers(dp: Dispatcher):
    dp.message(Command(commands=['dm_all']))(dm_all_handler)
    dp.message(Command(commands=['create_gift']))(create_gift_handler)
