from aiogram import types, Dispatcher, F
from datetime import datetime
import sqlite3
import random
import string

from bot.config import MINIMUM, ADMIN_IDS
from bot.keyboards.inline import create_main_keyboard, create_profil_keyboard, create_language_keyboard, create_home_keyboard
from bot.utils.db import get_user_balance, update_user_balance, get_user_addresses, get_user_creation_time, set_user_language, get_user_language
from bot.utils.lang import language_dict, get_translation

async def handle_callback_home(callback_query: types.CallbackQuery):
    first_name = callback_query.from_user.first_name

    user_id = callback_query.from_user.id
    
    lang_code = get_user_language(user_id)
    main_keyboard = create_main_keyboard(user_id)
    welcome_message = get_translation(lang_code, "start.welcome_message", first_name=first_name)

    await callback_query.message.edit_text(welcome_message, reply_markup=main_keyboard)
    await callback_query.answer()

async def handle_callback_profil(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name
    last_name = callback_query.from_user.last_name if callback_query.from_user.last_name else "❌"
    username = f"@{callback_query.from_user.username}" if callback_query.from_user.username else "❌"
    creation_time = get_user_creation_time(user_id)
    creation_date = datetime.fromtimestamp(creation_time).strftime('%d/%m/%Y %H:%M')

    balance_eur = get_user_balance(user_id)

    lang_code = get_user_language(user_id)

    profil_keyboard = create_profil_keyboard(user_id)
    profil_info = get_translation(lang_code, "callback.profile_info", user_id=user_id, first_name=first_name, last_name=last_name, username=username, creation_date=creation_date, balance_eur=balance_eur)

    await callback_query.message.edit_text(profil_info, reply_markup=profil_keyboard) 
    await callback_query.answer()

async def handle_callback_help(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    
    lang_code = get_user_language(user_id)

    base_help_message = get_translation(lang_code, "callback.help_message.base")
    admin_help_message = get_translation(lang_code, "callback.help_message.admin")
    user_help_message = get_translation(lang_code, "callback.help_message.user")
    
    help_message = base_help_message
    if user_id in ADMIN_IDS:
        help_message += admin_help_message
    help_message += user_help_message

    home_keyboard = create_home_keyboard(user_id)

    await callback_query.message.edit_text(help_message, reply_markup=home_keyboard)
    await callback_query.answer()


async def handle_callback_top_up(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang_code = get_user_language(user_id)

    btc_address, eth_address, ltc_address = get_user_addresses(user_id)

    if btc_address and eth_address and ltc_address:
        top_up_message = get_translation(lang_code, "callback.top_up_message", btc_address=btc_address, minimum_btc=MINIMUM['btc'], eth_address=eth_address, minimum_eth=MINIMUM['eth'], ltc_address=ltc_address, minimum_ltc=MINIMUM['ltc'])
    else:
        top_up_message = get_translation(lang_code, "callback.no_addresses_found")
    home_keyboard = create_home_keyboard(user_id)

    await callback_query.message.edit_text(top_up_message, reply_markup=home_keyboard)
    await callback_query.answer()

async def handle_callback_shop(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang_code = get_user_language(user_id)
    balance = get_user_balance(user_id)
    cost = 5.00

    if balance >= cost:
        new_balance = balance - cost
        update_user_balance(user_id, new_balance)
        license_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        response_text = get_translation(lang_code, "callback.license_key", license_key=license_key)
    else:
        missing_amount = cost - balance
        response_text = get_translation(lang_code, "callback.insufficient_balance", missing_amount=missing_amount)
    home_keyboard = create_home_keyboard(user_id)

    await callback_query.message.edit_text(response_text, reply_markup=home_keyboard)
    await callback_query.answer()


async def handle_callback_change_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang_code = get_user_language(user_id)

    select_language = get_translation(lang_code, "callback.select_language")
    language_keyboard = create_language_keyboard(user_id)

    await callback_query.message.edit_text(select_language, reply_markup=language_keyboard)
    await callback_query.answer()


async def handle_callback_lang(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang_code = callback_query.data.split('_')[1]
    set_user_language(user_id, lang_code)
    home_keyboard = create_home_keyboard(user_id)
    
    await callback_query.message.edit_text(f"Language changed to {language_dict[lang_code]['emoji']} {language_dict[lang_code]['language']}!", reply_markup=home_keyboard)
    await callback_query.answer()


def register_handlers(dp: Dispatcher):
    dp.callback_query(F.data == 'profil')(handle_callback_profil)
    dp.callback_query(F.data == 'shop')(handle_callback_shop)
    dp.callback_query(F.data == 'help')(handle_callback_help)
    dp.callback_query(F.data == 'top_up')(handle_callback_top_up)
    dp.callback_query(F.data == 'home')(handle_callback_home)
    dp.callback_query(F.data == 'change_language')(handle_callback_change_language)
    dp.callback_query(F.data.startswith('lang_'))(handle_callback_lang)
