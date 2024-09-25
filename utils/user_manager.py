import json
import hashlib
import os
import streamlit as st
from itsdangerous import URLSafeTimedSerializer
import tempfile
from utils.crypto_utils import encrypt_data, decrypt_data
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

USER_DATA_FILE = 'users.json'

try:
    SECRET_KEY = st.secrets['SECRET_KEY']
    LOGGER.info("成功从 .secrets 文件读取 SECRET_KEY")
except FileNotFoundError:
    SECRET_KEY = 'fG7g5OlCWEXKzDSPOrt8sccn68ZWtf0S'  # 默认值
except KeyError:
    SECRET_KEY = 'fG7g5OlCWEXKzDSPOrt8sccn68ZWtf0S'  # 默认值

TOKEN_EXPIRATION = 86400  # 1天的秒数
TOKEN_DIR = os.path.join(tempfile.gettempdir(), 'streamlit_tokens')

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_users(users):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

def register(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    if username not in users or users[username] != hash_password(password):
        return False
    st.session_state.logged_in = True
    st.session_state.username = username
    return True

def change_password(username, old_password, new_password):
    users = load_users()
    if username not in users or users[username] != hash_password(old_password):
        return False
    users[username] = hash_password(new_password)
    save_users(users)
    return True

def get_logged_in_username():
    return st.session_state.get('username') if st.session_state.get('logged_in') else None

def save_token_to_file(token, data):
    if not os.path.exists(TOKEN_DIR):
        os.makedirs(TOKEN_DIR)
    token_file = os.path.join(TOKEN_DIR, f"{token}.token")
    encrypted_data = encrypt_data(data)
    with open(token_file, 'w') as f:
        f.write(encrypted_data)

def load_token_from_file(token):
    token_file = os.path.join(TOKEN_DIR, f"{token}.token")
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            encrypted_data = f.read()
        return decrypt_data(encrypted_data)
    return None

def destroy_token(token):
    token_file = os.path.join(TOKEN_DIR, f"{token}.token")
    if os.path.exists(token_file):
        os.remove(token_file)

def generate_token(username):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    token = serializer.dumps(username, salt=SECRET_KEY)
    save_session_state_to_file(token)
    return token

def verify_token(token):
    try:
        data = load_token_from_file(token)
        if data:
            session_data = json.loads(data)
            for key, value in session_data.items():
                if not hasattr(st.session_state, key):
                    setattr(st.session_state, key, value)
            return True
    except Exception:
        pass
    return False

def save_session_state_to_file(token):
    session_data = dict(st.session_state)
    # 只保留特定属性
    for key in list(session_data.keys()):
        if key not in ['logged_in', 'username', 'bots', 'default_bot', 'chat_config']:
            del session_data[key]

    # 不保存以 __ 开头的属性
    for key in list(session_data.keys()):
        if key.startswith("__"):
            del session_data[key]
    
    LOGGER.info(f"Saving session state. Username: {session_data.get('username')}")
    data = json.dumps(session_data)
    save_token_to_file(token, data)

def get_username_from_token(token):
    data = load_token_from_file(token)
    if data:
        session_data = json.loads(data)
        return session_data.get('username')
    return None