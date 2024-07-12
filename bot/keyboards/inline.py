from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from bot.utils.db import get_user_language
from bot.utils.lang import get_country_list, get_translation

def create_main_keyboard(user_id):
    lang_code = get_user_language(user_id)
    
    kdb_main = InlineKeyboardBuilder()
    
    button_profil = InlineKeyboardButton(text=get_translation(lang_code, "inline.profile_button"), callback_data='profil')
    button_shop = InlineKeyboardButton(text=get_translation(lang_code, "inline.buy_license_button"), callback_data='shop')
    button_top_up = InlineKeyboardButton(text=get_translation(lang_code, "inline.top_up_button"), callback_data='top_up')
    button_help = InlineKeyboardButton(text=get_translation(lang_code, "inline.help_button"), callback_data='help')

    kdb_main.add(button_profil, button_shop, button_top_up, button_help).adjust(2, 1, 1)
    return kdb_main.as_markup()

def create_home_keyboard(user_id):
    lang_code = get_user_language(user_id)
    button_home = InlineKeyboardButton(text=get_translation(lang_code, "inline.home_button"), callback_data='home')

    kdb_secondary = InlineKeyboardBuilder()
    kdb_secondary.row(button_home)
    return kdb_secondary.as_markup()

def create_profil_keyboard(user_id):
    lang_code = get_user_language(user_id)

    button_change_language = InlineKeyboardButton(text="🌐 Change the language", callback_data='change_language')
    button_home = InlineKeyboardButton(text=get_translation(lang_code, "inline.home_button"), callback_data='home')

    kdb_language = InlineKeyboardBuilder()
    kdb_language.row(button_change_language, button_home)
    return kdb_language.as_markup()

def create_language_keyboard(user_id):
    lang_code = get_user_language(user_id)

    kdb_language = InlineKeyboardBuilder()
    country_list = get_country_list()

    for lang_code_button, emoji, country in country_list:
        button_text = f"{emoji} {country}"
        kdb_language.add(InlineKeyboardButton(text=button_text, callback_data=f"lang_{lang_code_button}"))
    
    button_home = InlineKeyboardButton(text=get_translation(lang_code, "inline.home_button"), callback_data='home')
    kdb_language.add(button_home)

    kdb_language.adjust(4, 4, 4, 4, 4, 3, 1)
    return kdb_language.as_markup()
