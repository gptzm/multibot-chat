import streamlit as st
import json
import os
from utils.crypto_utils import encrypt_data, decrypt_data
import logging
from datetime import datetime
import uuid
from bot.config import ENGINE_CONFIG

LOGGER = logging.getLogger(__name__)
    
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
        self.fix_history_names()

    def save_data_to_file(self):
        self.ensure_valid_history_version()
        if not self._filename:
            return
        LOGGER.info(f'保存bots\n\n{self.bots}')
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
                self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}}]
                self.current_history_version = 0
                return

            with open(file_path, 'r') as f:
                encrypted_data = f.read()
            decrypted_data = decrypt_data(encrypted_data)
            data = json.loads(decrypted_data)
            self.bots = data.get('bots', [])
            self.history_versions = data.get('history_versions', [{'timestamp': datetime.now().isoformat(), 'histories': {}}])
            self.current_history_version = data.get('current_history_version', 0)
            self.bot_id_map = data.get('bot_id_map', {})
            # st.info(dict(data))
            self.fix_bot_setting()
            # st.info(dict(st.session_state))
        except Exception as e:
            LOGGER.error(f"加载配置文件时出错：{str(e)}")
            self.bots = []
            self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}}]
            self.current_history_version = 0

    def ensure_valid_history_version(self):
        if not self.history_versions:
            self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}}]
            self.current_history_version = 0
        elif self.current_history_version >= len(self.history_versions):
            self.current_history_version = len(self.history_versions) - 1

    def fix_history_names(self, specific_index=None):
        versions_to_update = [self.history_versions[specific_index]] if specific_index is not None else self.history_versions
        for idx, version in enumerate(versions_to_update):
            if specific_index is not None:
                idx = specific_index
            
            if 'name' not in version or version['name'] == '新话题':
                first_prompt = self.get_first_prompt(version['histories'])
                if first_prompt:
                    content = first_prompt.replace('\n', ' ').replace('\r', '')
                    if len(content) > 20:
                        content = f"{content[:20]}..."
                    version['name'] = f"{idx+1}. {content}"
                else:
                    version['name'] = f"新话题"

    def get_first_prompt(self, histories):
        for history in histories.values():
            for message in history:
                if message['role'] == 'user':
                    return message['content']
        return None

    def fix_bot_setting(self):
        # 确保每个机器人都有一个唯一的ID
        existing_ids = set()
        for bot in reversed(self.bots):
            if 'id' not in bot or bot['id'] in existing_ids:
                bot['id'] = str(uuid.uuid4())
            existing_ids.add(bot['id'])
        
        # 更新bot_id_map
        self.bot_id_map = {bot['name']: bot['id'] for bot in self.bots}

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

    def update_bot(self, bot):
        if 'id' not in bot:
            st.error("机器人缺少ID")
            return
        
        if bot['name'].strip() == '':
            st.error("机器人名称不能为空")
            return
        
        # 找到要更新的机器人索引
        idx = next((i for i, b in enumerate(self.bots) if b['id'] == bot['id']), -1)
        
        if idx == -1:
            st.error("找不到要更新的机器人")
            return
        
        if bot['name'] in [b['name'] for i, b in enumerate(self.bots) if i != idx]:
            st.error(f"机器人 {bot['name']} 已存在")
            return

        old_name = self.bots[idx]['name']
        old_id = self.bots[idx]['id']
        if 'avatar' not in bot:
            bot['avatar'] = '🤖'  # 确保有头像字段
        
        # 保存bot的enable状态
        if 'enable' not in bot:
            bot['enable'] = self.bots[idx].get('enable', True)  # 如果原来没有enable字段，默认为True
        
        self.bots[idx] = bot
        self.bot_id_map[bot['name']] = old_id
        if old_name != bot['name']:
            del self.bot_id_map[old_name]
        
        # 如果所有机器人都被禁用，给出警告
        if not any(b['enable'] for b in self.bots):
            st.warning("所有机器人都已被禁用。请至少启用一个机器人以进行对话。")

        # 更新session_state中的bots
        if 'bots' in st.session_state:
            st.session_state.bots[idx] = bot
        
        self.save_data_to_file()

    def delete_bot(self, bot):
        bot_id = bot['id']
        self.bots = [b for b in self.bots if b['id'] != bot_id]
        for version in self.history_versions:
            version['histories'].pop(bot_id, None)
        self.bot_id_map.pop(bot['name'], None)
        self.fix_bot_setting()
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
        return True

    def is_current_history_empty(self):
        if self.current_history_version < len(self.history_versions):
            current_history = self.history_versions[self.current_history_version]['histories']
            return all(len(history) == 0 for history in current_history.values())
        return True

    def get_participating_bots(self, version_index):
        if 0 <= version_index < len(self.history_versions):
            return set(self.history_versions[version_index]['histories'].keys())
        return set()

    def add_message_to_history(self, bot_name, message):
        bot_id = self.bot_id_map.get(bot_name)
        if bot_id and self.current_history_version < len(self.history_versions):
            current_version = self.history_versions[self.current_history_version]
            current_version['histories'].setdefault(bot_id, []).append(message)

    def get_default_bot(self, engine):
        if 'default_bots' not in st.session_state:
            st.session_state.default_bots = {}
        
        if engine not in st.session_state.default_bots:
            default_bot = {
                'model': '',
                'system_prompt': '用中文回答问题',
                'temperature': 1.0, 
                'enable': True,
            }
            
            # 使用 ENGINE_CONFIG 中的默认值
            for field in ENGINE_CONFIG['engines'][engine]['fields']:
                field_default_value = field.get('default', '')
                LOGGER.info(f'{field["name"]} = {field_default_value}')
                if field_default_value:
                    default_bot[field['name']] = field_default_value

            st.session_state.default_bots[engine] = default_bot

        return st.session_state.default_bots[engine]

    def update_default_bot(self, bot):
        engine = bot['engine']
        default_bot = self.get_default_bot(engine)
        for key in bot:
            if key in default_bot:
                default_bot[key] = bot[key]
        st.session_state.default_bots[engine] = default_bot
        self.save_data_to_file()

    def create_bot_copy(self, bot):
        bot_copy = json.loads(json.dumps(bot))
        bot_copy['name'] = f"{bot['name']} 副本"
        bot_copy['history'] = []
        bot_copy['id'] = str(uuid.uuid4())  # 生成唯一ID
        self.add_bot(bot_copy)
        self.save_data_to_file()
        return bot_copy

    def get_all_histories(self, bot):
        bot_id = bot['id']
        return [{'name': version['name'], 'timestamp': version['timestamp'], 'history': version['histories'].get(bot_id, [])} 
                for version in self.history_versions]

    def clear_all_histories(self):
        self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}}]
        self.current_history_version = 0
        self.fix_history_names()

    def get_current_history_by_bot(self, bot):
        bot_id = bot['id']
        if bot_id and self.current_history_version < len(self.history_versions):
            current_version = self.history_versions[self.current_history_version]
            return current_version['histories'].get(bot_id, [])
        return []

    def get_currently_enabled_bots(self):
        return set(bot['name'] for bot in self.bots if bot.get('enable', False))

    def is_all_current_histories_empty(self):
        return all(not self.get_current_history_by_bot(bot) for bot in st.session_state.bots)

