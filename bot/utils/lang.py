import os
import json

language_dict = {
    "ar": {"language": "Arabic", "emoji": "🇸🇦"},
    "ca": {"language": "Catalan", "emoji": "🇨🇦"},
    "cs": {"language": "Czech", "emoji": "🇨🇿"},
    "de": {"language": "German", "emoji": "🇩🇪"},
    "el": {"language": "Greek", "emoji": "🇬🇷"},
    "en": {"language": "English", "emoji": "🇬🇧"},
    "es": {"language": "Spanish", "emoji": "🇪🇸"},
    "eu": {"language": "Basque", "emoji": "🇪🇺"},
    "fa": {"language": "Persian", "emoji": "🇮🇷"},
    "fr": {"language": "French", "emoji": "🇫🇷"},
    "he": {"language": "Hebrew", "emoji": "🇮🇱"},
    "id": {"language": "Indonesian", "emoji": "🇮🇩"},
    "it": {"language": "Italian", "emoji": "🇮🇹"},
    "ja": {"language": "Japanese", "emoji": "🇯🇵"},
    "ko": {"language": "Korean", "emoji": "🇰🇷"},
    "pl": {"language": "Polish", "emoji": "🇵🇱"},
    "pt": {"language": "Portuguese", "emoji": "🇵🇹"},
    "ru": {"language": "Russian", "emoji": "🇷🇺"},
    "si": {"language": "Slovenian", "emoji": "🇸🇮"},
    "tr": {"language": "Turkish", "emoji": "🇹🇷"},
    "uk": {"language": "Ukrainian", "emoji": "🇺🇦"},
    "uz": {"language": "Uzbek", "emoji": "🇺🇿"},
    "yue": {"language": "Cantonese", "emoji": "🇭🇰"}
}

def get_translation(lang_code, key, **kwargs):
    lang_file_path = f'./bot/lang/{lang_code}.json'
    
    if not os.path.exists(lang_file_path):
        raise FileNotFoundError(f"{lang_file_path} doesn't exist.")
    
    with open(lang_file_path, 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    keys = key.split('.')
    translation = translations
    for k in keys:
        translation = translation.get(k, {})
    
    if isinstance(translation, str):
        translation = translation.format(**kwargs)
    
    return translation

def get_country_list():
    country_list = []
    for filename in os.listdir("./bot/lang"):
        if filename.endswith(".json"):
            lang_code = filename.split('.')[0]

            if lang_code in language_dict:
                country_info = language_dict[lang_code]
                country_list.append((lang_code, country_info['emoji'], country_info['language']))

    return country_list
