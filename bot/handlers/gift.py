import random
import string

from aiogram import types, Dispatcher
from aiogram.filters import Command

from bot.config import ADMIN_IDS
from bot.utils.db import create_gift_card, redeem_gift_card, update_user_balance, get_user_balance, is_gift_code_unique, get_user_language
from bot.utils.lang import get_translation

def generate_gift_code():
    return '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) for _ in range(4))

async def create_gift_handler(message: types.Message):
    user_id = message.from_user.id
    user_id_str = str(user_id)
    lang_code = get_user_language(user_id)

    if user_id_str not in ADMIN_IDS:
        unauthorized_command = get_translation(lang_code, "admin.unauthorized_command")
        await message.reply(unauthorized_command)
        return

    args = message.text.split()[1:]
    if not args or not args[0].isdigit():
        provide_valid_amount = get_translation(lang_code, "gift.provide_valid_amount")
        await message.reply(provide_valid_amount)
        return
    
    amount = float(args[0])
    if amount == 0:
        gift_amount_zero = get_translation(lang_code, "gift.gift_amount_zero")
        await message.reply(gift_amount_zero)
        return
    
    code = generate_gift_code()
    while not is_gift_code_unique(code):
        code = generate_gift_code()

    create_gift_card(code, amount)
    gift_card_created = get_translation(lang_code, "gift.gift_card_created", code=code, amount=amount)
    await message.reply(gift_card_created)

async def redeem_gift_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    lang_code = get_user_language(user_id)

    args = message.text.split()[1:]
    if not args:
        provide_gift_code = get_translation(lang_code, "gift.provide_gift_code")
        await message.reply(provide_gift_code)
        return
    
    code = args[0]
    
    amount = redeem_gift_card(code, user_id)
    if amount is not None:
        balance = get_user_balance(user_id)
        new_balance = balance + amount
        update_user_balance(user_id, new_balance)
        gift_card_redeemed = get_translation(lang_code, "gift.gift_card_redeemed", amount=amount)
        await message.reply(gift_card_redeemed)
        
        for admin_id in ADMIN_IDS:
            admin_notification = get_translation(lang_code, "gift.admin_notification", first_name=first_name, user_id=user_id, code=code)
            await message.bot.send_message(admin_id, admin_notification)
    else:
        invalid_gift_code = get_translation(lang_code, "gift.invalid_gift_code")
        await message.reply(invalid_gift_code)

def register_gift_handlers(dp: Dispatcher):
    dp.message(Command(commands=['redeem_gift']))(redeem_gift_handler)
