import sqlite3
import time

from bot.config import DATABASE

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                btc_address TEXT,
                eth_address TEXT,
                ltc_address TEXT,
                balance_eur REAL DEFAULT 0,
                creation_time INTEGER,
                lang TEXT DEFAULT 'en'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_paiement (
                id_telegram TEXT,
                uuid TEXT,
                address_in TEXT,
                confirmations INTEGER,
                txid_in TEXT,
                txid_out TEXT,
                value_coin REAL,
                value_forwarded_coin REAL,
                price REAL,
                coin TEXT,
                result TEXT,
                processed BOOLEAN DEFAULT 0,
                timestamp INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gift_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                amount REAL,
                used BOOLEAN DEFAULT 0,
                redeemed_by INTEGER
            )
        ''')

        conn.commit()

def save_user(user_id, first_name, last_name, username, btc_address, eth_address, ltc_address):
    creation_time = int(time.time())
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (user_id, first_name, last_name, username, btc_address, eth_address, ltc_address, creation_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                username=excluded.username,
                btc_address=excluded.btc_address,
                eth_address=excluded.eth_address,
                ltc_address=excluded.ltc_address
        ''', (user_id, first_name, last_name, username, btc_address, eth_address, ltc_address, creation_time))
        
        conn.commit()

def set_user_language(user_id, lang):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET lang = ? WHERE user_id = ?
        ''', (lang, user_id))
        conn.commit()

def get_user_language(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT lang FROM users WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        return row[0] if row else 'en'

def get_user_addresses(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT btc_address, eth_address, ltc_address FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()

        if row:
            return row[0], row[1], row[2]
        return None, None, None
    
def get_user_creation_time(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT creation_time FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()

        if row:
            return row[0]
        return None
    
def get_user_balance(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT balance_eur FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()

        if row:
            return row[0]
        return 0

def update_user_balance(user_id, new_balance):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET balance_eur = ? WHERE user_id = ?', (new_balance, user_id))
        
        conn.commit()

def get_all_user_ids():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        rows = cursor.fetchall()

        return [row[0] for row in rows]

def create_gift_card(code, amount):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO gift_cards (code, amount) VALUES (?, ?)', (code, amount))

        conn.commit()

def is_gift_code_unique(code):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM gift_cards WHERE code = ?', (code,))
        row = cursor.fetchone()

        return row is None

def redeem_gift_card(code, user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT amount, used FROM gift_cards WHERE code = ?', (code,))
        row = cursor.fetchone()

        if row and not row[1]:
            amount = row[0]
            cursor.execute('UPDATE gift_cards SET used = 1, redeemed_by = ? WHERE code = ?', (user_id, code))
            
            conn.commit()
            return amount
        return None
