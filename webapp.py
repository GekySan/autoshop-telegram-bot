import sqlite3
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import base64
import time
import logging

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3FT0Ym8b3myVxhQW7ESuuu6lo
dGAsUJs4fq+Ey//jm27jQ7HHHDmP1YJO7XE7Jf/0DTEJgcw4EZhJFVwsk6d3+4fy
Bsn0tKeyGMiaE6cVkX0cy6Y85o8zgc/CwZKc0uw6d5siAo++xl2zl+RGMXCELQVE
ox7pp208zTvown577wIDAQAB
-----END PUBLIC KEY-----""" # https://api.cryptapi.io/pubkey/
ALLOWED_IPS = ["145.239.119.223", "135.125.112.47"] # https://docs.cryptapi.io/#tag/Callbacks
ALLOWED_IPS.append("127.0.0.1") # ONLY FOR TEST

def load_public_key(pem_str):
    public_key = serialization.load_pem_public_key(pem_str.encode())
    return public_key

def verify_signature(data, signature, public_key):
    try:
        public_key.verify(
            base64.b64decode(signature),
            data.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False

def log_request_to_db(id_telegram, params):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
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
        INSERT INTO logs_paiement (
            id_telegram, uuid, address_in, confirmations, txid_in, txid_out, 
            value_coin, value_forwarded_coin, price, coin, result, processed, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        id_telegram, params['uuid'], params['address_in'], 
        params['confirmations'], params['txid_in'], params['txid_out'], 
        params['value_coin'], params['value_forwarded_coin'], 
        params['price'], params['coin'], params['result'], False, int(time.time())
    ))

    conn.commit()
    conn.close()

@app.route('/cryptapi/<id_telegram>/', methods=['POST'])
def callback_handler(id_telegram):
    ip = request.remote_addr
    if ip not in ALLOWED_IPS:
        return jsonify(status="forbidden"), 403

    signature = request.headers.get("x-ca-signature")
    data = request.get_data(as_text=True)

    if not signature:
        return jsonify(status="error", message="Missing signature"), 400

    if verify_signature(data, signature, public_key):
        params = request.form.to_dict()
        log_request_to_db(id_telegram, params)
        return jsonify(status="success")
    else:
        return jsonify(status="error", message="Invalid signature"), 400

if __name__ == '__main__':
    try:
        public_key = load_public_key(PUBLIC_KEY_PEM)
    except Exception as e:
        print(f"Can't load public key: {e}")
        exit(1)
    
    app.run(host='0.0.0.0', port=2468)
