import json
import hashlib
import os
import streamlit as st
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from utils.crypto_utils import encrypt_data, decrypt_data
import logging
import time

from config import (
    TOKEN_EXPIRATION, USER_DATA_FILE, LOG_LEVEL, TOKEN_DIR, SECRET_KEY
)

logging.basicConfig(level=LOG_LEVEL)
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
    token = serializer.dumps({'username': username, 'created_at': time.time()}, salt=SECRET_KEY)
    save_session_state_to_file(token)
    return token

def verify_token(token):
    try:
        serializer = URLSafeTimedSerializer(SECRET_KEY)
        data = serializer.loads(token, salt=SECRET_KEY, max_age=TOKEN_EXPIRATION)
        username = data['username']
        created_at = data['created_at']
        
        if time.time() - created_at > TOKEN_EXPIRATION:
            LOGGER.warning(f"Token expired for user: {username}")
            destroy_token(token)
            return False
        
        session_data = load_token_from_file(token)
        if session_data:
            session_data = json.loads(session_data)
            for key, value in session_data.items():
                if not hasattr(st.session_state, key):
                    setattr(st.session_state, key, value)
            return True
    except (SignatureExpired, BadSignature):
        LOGGER.warning("Invalid or expired token")
    except Exception as e:
        LOGGER.error(f"Error verifying token: {str(e)}")
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