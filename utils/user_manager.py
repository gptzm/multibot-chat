import json
import hashlib
import os
import streamlit as st
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from utils.crypto_utils import encrypt_data, decrypt_data
import logging
import time
import re
from config import (
    TOKEN_EXPIRATION, USER_DATA_FILE, LOG_LEVEL, TOKEN_DIR, SECRET_KEY, ENABLED_REGISTER
)

logging.basicConfig(level=LOG_LEVEL)
LOGGER = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        self._token = None
        self._username = None

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def load_users(self):
        if not os.path.exists(USER_DATA_FILE):
            return {}
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_users(self, users):
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as file:
            json.dump(users, file, ensure_ascii=False, indent=4)

    def register(self, username, password):
        if not ENABLED_REGISTER:
            st.warning("暂未开放注册")
            return False

        if not re.match(r'^[a-zA-Z0-9@\._]{1,32}$', username):
            return False
        users = self.load_users()
        if username in users:
            st.warning("已存在此账号")
            return False
        users[username] = self.hash_password(password)
        self.save_users(users)
        return True
    
    def login(self, username, password):
        users = self.load_users()
        if username not in users or users[username] != self.hash_password(password):
            return False
        self._username = username
        self._token = self.generate_token(username)
        return True

    def change_password(self, username, old_password, new_password):
        users = self.load_users()
        if username not in users or users[username] != self.hash_password(old_password):
            return False
        users[username] = self.hash_password(new_password)
        self.save_users(users)
        return True

    def get_logged_in_username(self):
        return self._username

    def save_token_to_file(self, data):
        if not os.path.exists(TOKEN_DIR):
            os.makedirs(TOKEN_DIR)
        token_file = os.path.join(TOKEN_DIR, f"{self._token}.token")
        encrypted_data = encrypt_data(data)
        with open(token_file, 'w') as f:
            f.write(encrypted_data)

    def load_token_from_file(self):
        token_file = os.path.join(TOKEN_DIR, f"{self._token}.token")
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                encrypted_data = f.read()
            return decrypt_data(encrypted_data)
        return None

    def destroy_token(self):
        if self._token:
            token_file = os.path.join(TOKEN_DIR, f"{self._token}.token")
            if os.path.exists(token_file):
                os.remove(token_file)
        self._token = None
        self._username = None

    def generate_token(self, username):
        serializer = URLSafeTimedSerializer(SECRET_KEY)
        token = serializer.dumps({'username': username, 'created_at': time.time()}, salt=SECRET_KEY)
        self._token = token
        self._username = username
        self.save_session_state_to_file()  # 使用 st.session_state 而不是 token
        return token

    def verify_token(self, token=None):
        if token is not None:
            self._token = token
        if not self._token:
            return False
        try:
            serializer = URLSafeTimedSerializer(SECRET_KEY)
            data = serializer.loads(self._token, salt=SECRET_KEY, max_age=TOKEN_EXPIRATION)
            username = data['username']
            created_at = data['created_at']

            if time.time() - created_at > TOKEN_EXPIRATION:
                LOGGER.warning(f"Token expired for user: {username}")
                self.destroy_token()
                return False
            
            session_data = self.load_token_from_file()
            if session_data:
                session_data = json.loads(session_data)
                for key, value in session_data.items():
                    if not hasattr(st.session_state, key):
                        setattr(st.session_state, key, value)
                self._username = username
                return True
        except (SignatureExpired, BadSignature):
            LOGGER.warning("Invalid or expired token")
        except Exception as e:
            LOGGER.error(f"Error verifying token: {str(e)}")
        return False

    def save_session_state_to_file(self):
        if not self._token:
            return
        
        session_data = dict(st.session_state)

        # 只保留特定属性
        for key in list(session_data.keys()):
            if key not in ['logged_in', 'username', 'bots', 'default_bot', 'chat_config']:
                del session_data[key]
        
        LOGGER.info(f"Saving session state. Username: {session_data.get('username')}")
        data = json.dumps(session_data)
        self.save_token_to_file(data)

    def get_username_from_token(self):
        if not self._token:
            return None
        data = self.load_token_from_file()
        if data:
            session_data = json.loads(data)
            return session_data.get('username')
        return None

# 创建全局 UserManager 实例
user_manager = UserManager()
