import streamlit as st
import json
import os
from utils.crypto_utils import encrypt_data, decrypt_data
import logging
from datetime import datetime
import uuid

LOGGER = logging.getLogger(__name__)

if 'SECRET_KEY' in st.secrets:
    SECRET_KEY = st.secrets['SECRET_KEY']
else:
    SECRET_KEY = 'd0GiE5r03cy66SP'

class BotSessionManager:
    def __init__(self, username):
        self._filename = username
        LOGGER.info(f"初始化 BotSessionManager，用户名: {username}")
        if not username:
            raise ValueError("用户名未设置")
        self.bots = []
        self.history_versions = []
        self.current_history_version = 0
        self.bot_id_map = {}  # 用于存储 bot_name 到 bot_id 的映射
        
        self.load_data_from_file()
        self.update_history_names()

    def save_data_to_file(self):
        self.ensure_valid_history_version()
        if not self._filename:
            return
        data = {
            'bots': self.bots,
            'history_versions': self.history_versions,
            'current_history_version': self.current_history_version,
            'bot_id_map': self.bot_id_map
        }
        encrypted_data = encrypt_data(json.dumps(data))
        with open(f"user_config/{self._filename}.encrypt", 'w') as f:
            f.write(encrypted_data)

    def load_data_from_file(self):
        if not self._filename:
            LOGGER.error("无法加载：用户名未设置")
            return
        try:
            file_path = f"user_config/{self._filename}.encrypt"
            if not os.path.exists(file_path):
                LOGGER.info(f"欢迎新用户: {self._filename}")
                self.bots = []
                self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}, 'name': '新话题'}]
                self.current_history_version = 0
                return

            with open(file_path, 'r') as f:
                encrypted_data = f.read()
            decrypted_data = decrypt_data(encrypted_data)
            data = json.loads(decrypted_data)
            self.bots = data.get('bots', [])
            self.history_versions = data.get('history_versions', [{'timestamp': datetime.now().isoformat(), 'histories': {}, 'name': '新话题'}])
            self.current_history_version = data.get('current_history_version', 0)
            self.bot_id_map = data.get('bot_id_map', {})
            # st.info(dict(data))
            self.fix_bot_setting()
            # st.info(dict(st.session_state))
        except Exception as e:
            LOGGER.error(f"加载配置文件时出错：{str(e)}")
            self.bots = []
            self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}, 'name': '新话题'}]
            self.current_history_version = 0

    def ensure_valid_history_version(self):
        if not self.history_versions:
            self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}, 'name': '新话题'}]
            self.current_history_version = 0
        elif self.current_history_version >= len(self.history_versions):
            self.current_history_version = len(self.history_versions) - 1

    def update_history_names(self):
        for idx, version in enumerate(self.history_versions):
            if 'name' not in version or version['name'] == '新话题':
                first_prompt = self.get_first_prompt(version['histories'])
                if first_prompt:
                    content = first_prompt
                    if len(content) > 20:
                        content = f"{content[:20]}..."
                    version['name'] = f"{idx+1}. {content}"
                else:
                    version['name'] = '新话题'

    def get_first_prompt(self, histories):
        for history in histories.values():
            for message in history:
                if message['role'] == 'user':
                    return message['content']
        return None

    def fix_bot_setting(self):
        # 确保至少有一个机器人启用
        if not any(bot.get('enable', False) for bot in self.bots):
            if self.bots:
                self.bots[0]['enable'] = True
        
        # 确保每个机器人都有一个唯一的ID
        existing_ids = set()
        for bot in self.bots:
            if 'id' not in bot or bot['id'] in existing_ids:
                bot['id'] = str(uuid.uuid4())
            existing_ids.add(bot['id'])
        
        # 更新bot_id_map
        self.bot_id_map = {bot['name']: bot['id'] for bot in self.bots}
        
        self.save_data_to_file()

    def load_bots_from_session(self):
        self.fix_bot_setting()
        return self.bots

    def add_bot(self, bot):
        if bot['name'].strip() == '':
            st.error(f"机器人名称不能为空")
            return
        
        if bot['name'] in [bot['name'] for bot in self.bots]:
            st.error(f"机器人 {bot['name']} 已存在")
            return
        
        bot_id = str(uuid.uuid4())  # 生成唯一ID
        bot['id'] = bot_id
        if 'avatar' not in bot:
            bot['avatar'] = '🤖'  # 设置默认头像
        self.bots.append(bot)
        self.bot_id_map[bot['name']] = bot_id
        for version in self.history_versions:
            version['histories'][bot_id] = []
        self.fix_bot_setting()
        self.save_data_to_file()

    def update_bot(self, bot, idx):
        if idx == -1:
            st.error(f"机器人设置可能已被更新")
            return
        
        if bot['name'].strip() == '':
            st.error(f"机器人名称不能为空")
            return
        
        if bot['name'] in [b['name'] for i, b in enumerate(self.bots) if i != idx]:
            st.error(f"机器人 {bot['name']} 已存在")
            return

        old_name = self.bots[idx]['name']
        old_id = self.bots[idx]['id']
        if 'avatar' not in bot:
            bot['avatar'] = '🤖'  # 确保有头像字段
        self.bots[idx] = bot
        self.bot_id_map[bot['name']] = old_id
        if old_name != bot['name']:
            del self.bot_id_map[old_name]
        self.save_data_to_file()

    def delete_bot(self, bot_name):
        bot_id = self.bot_id_map.get(bot_name)
        if bot_id:
            self.bots = [bot for bot in self.bots if bot['id'] != bot_id]
            for version in self.history_versions:
                version['histories'].pop(bot_id, None)
            del self.bot_id_map[bot_name]
        self.fix_bot_setting()
        self.save_data_to_file()

    def fix_bot_setting(self):
        # 确保至少有一个机器人启用
        if not any(bot.get('enable', False) for bot in self.bots):
            if self.bots:
                self.bots[0]['enable'] = True
        
        # 确保每个机器人都有一个唯一的ID
        existing_ids = set()
        for bot in self.bots:
            if 'id' not in bot or bot['id'] in existing_ids:
                bot['id'] = str(uuid.uuid4())
            existing_ids.add(bot['id'])
        
        # 更新bot_id_map
        self.bot_id_map = {bot['name']: bot['id'] for bot in self.bots}
        
        self.save_data_to_file()

    def fix_history_names(self):
        for idx, version in enumerate(self.history_versions):
            if version['name'] == '新话题':
                for bot_id, messages in version['histories'].items():
                    for message in messages:
                        if message['role'] == 'user':
                            content = message['content']
                            if len(content) > 20:
                                content = f"{content[:20]}..."
                            version['name'] = f"{idx+1}. {content}"
                            break
                    if version['name'] != '新话题':
                        break
            if version['name'] == '新话题':
                version['name'] = f"{idx+1}. 未命名话题"
        
        self.save_data_to_file()

    def create_new_history_version(self):
        if self.is_current_history_empty():
            return False
        new_version = {
            'timestamp': datetime.now().isoformat(),
            'histories': {bot['id']: [] for bot in self.bots if bot['enable']},
            'name': '新话题'
        }
        self.history_versions.append(new_version)
        self.current_history_version = len(self.history_versions) - 1
        self.save_data_to_file()
        self.fix_history_names()
        return True

    def is_current_history_empty(self):
        if self.current_history_version < len(self.history_versions):
            current_history = self.history_versions[self.current_history_version]['histories']
            return all(len(history) == 0 for history in current_history.values())
        return True

    def update_history_name(self, version_index, new_name):
        if 0 <= version_index < len(self.history_versions):
            self.history_versions[version_index]['name'] = new_name
            self.save_data_to_file()

    def get_participating_bots(self, version_index):
        if 0 <= version_index < len(self.history_versions):
            return set(self.history_versions[version_index]['histories'].keys())
        return set()

    def add_message_to_history(self, bot_name, message):
        bot_id = self.bot_id_map.get(bot_name)
        if bot_id and self.current_history_version < len(self.history_versions):
            current_version = self.history_versions[self.current_history_version]
            current_version['histories'].setdefault(bot_id, []).append(message)
            if current_version['name'] == '新话题' and message['role'] == 'user':
                idx = self.current_history_version
                content = message['content']
                if len(content) > 20:
                    content = f"{content[:20]}..."
                current_version['name'] = f"{idx+1}. {content}"
            self.save_data_to_file()

    def get_default_bot(self, engine):
        if 'default_bots' not in st.session_state:
            st.session_state.default_bots = {}
        
        if engine not in st.session_state.default_bots:
            default_bot = {
                'model': '',
                'system_prompt': '',
                'api_endpoint': os.getenv(f'{engine.upper()}_API_ENDPOINT', ''),
                'api_key': os.getenv(f'{engine.upper()}_API_KEY', ''),
                'bot_id': '',
                'temperature': 1.0, 
                'enable': True,
            }
            st.session_state.default_bots[engine] = default_bot

        return st.session_state.default_bots[engine]

    def update_default_bot(self, bot):
        engine = bot['engine']
        default_bot = self.get_default_bot(engine)
        for key in bot:
            if key in default_bot:
                default_bot[key] = bot[key]
        st.session_state.default_bots[engine] = default_bot

    def create_bot_copy(self, bot):
        bot_copy = json.loads(json.dumps(bot))
        bot_copy['name'] = f"{bot['name']} 副本"
        bot_copy['history'] = []
        self.add_bot(bot_copy)
        return bot_copy
    
    def get_bot_idx(self, bot):
        for idx, b in enumerate(self.bots):
            if b['name'] == bot['name'] and b.get('id') == bot.get('id'):
                return idx
        return -1

    def get_all_histories(self, bot_name):
        bot_id = self.bot_id_map.get(bot_name)
        if bot_id:
            return [{'name': version['name'], 'timestamp': version['timestamp'], 'history': version['histories'].get(bot_id, [])} 
                    for version in self.history_versions]
        return []

    def clear_all_histories(self):
        self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}, 'name': '新话题'}]
        self.current_history_version = 0
        self.save_data_to_file()
        self.fix_history_names()

    def get_current_history(self, bot_name):
        bot_id = self.bot_id_map.get(bot_name)
        if bot_id and self.current_history_version < len(self.history_versions):
            current_version = self.history_versions[self.current_history_version]
            return current_version['histories'].get(bot_id, [])
        return []

    def get_currently_enabled_bots(self):
        return set(bot['name'] for bot in self.bots if bot.get('enable', False))

    def fix_history_names(self):
        for idx, version in enumerate(self.history_versions):
            if 'name' not in version or version['name'] == '新话题':
                first_prompt = self.get_first_prompt(version['histories'])
                if first_prompt:
                    content = first_prompt.replace('\n', ' ').replace('\r', '')
                    if len(content) > 20:
                        content = f"{content[:20]}..."
                    version['name'] = f"{idx+1}. {content}"
                else:
                    version['name'] = f"{idx+1}. 新话题"
        self.save_data_to_file()
