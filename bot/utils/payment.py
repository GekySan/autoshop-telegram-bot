import sqlite3
import math
import asyncio

from aiogram import Bot

from bot.config import DATABASE, CALLBACK_URL, ADDRESSES, CONFIRMATIONS
from cryptapi import CryptAPIHelper

def init_addresses(user_id):
    """
    https://docs.cryptapi.io/#operation/create
    https://support.cryptapi.io/article/how-the-priority-parameter-works

    """
    user_callback_url = f"{CALLBACK_URL}{user_id}/"
    btc_ca = CryptAPIHelper('btc', ADDRESSES['btc'], user_callback_url, {'post': 1, 'confirmations': CONFIRMATIONS['btc'], 'priority': 'xxxxx-economic'}).get_address() # 🐀
    eth_ca = CryptAPIHelper('eth', ADDRESSES['eth'], user_callback_url, {'post': 1, 'confirmations': CONFIRMATIONS['eth'], 'priority': 'xxxx-economic'}).get_address() # 🐀
    ltc_ca = CryptAPIHelper('ltc', ADDRESSES['ltc'], user_callback_url, {'post': 1, 'confirmations': CONFIRMATIONS['ltc'], 'priority': 'fast'}).get_address() # 🚀

    btc_address = btc_ca['address_in']
    eth_address = eth_ca['address_in']
    ltc_address = ltc_ca['address_in']

    return btc_address, eth_address, ltc_address

async def check_and_process_logs(bot: Bot):
    while True:
        await process_logs(bot)
        await asyncio.sleep(10)

async def process_logs(bot: Bot):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, id_telegram, value_coin, price, coin FROM logs_paiement WHERE processed = 0")
    rows = cursor.fetchall()

    for row in rows:
        log_id, id_telegram, value_coin, price, coin = row
        result = math.ceil(value_coin * price * 100) / 100
        cursor.execute("SELECT balance_eur FROM users WHERE user_id = ?", (id_telegram,))
        balance_row = cursor.fetchone()

        if balance_row:
            new_balance = balance_row[0] + result
            cursor.execute("UPDATE users SET balance_eur = ? WHERE user_id = ?", (new_balance, id_telegram))

        await bot.send_message(id_telegram, f"Hello, you add {result}€ ({value_coin} {coin.upper()}) !")
        cursor.execute("UPDATE logs_paiement SET processed = 1 WHERE rowid = ?", (log_id,))

    conn.commit()
    conn.close()
