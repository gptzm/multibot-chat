import streamlit as st
import json
import os
from utils.crypto_utils import encrypt_data, decrypt_data
import logging
from datetime import datetime
import uuid
from bot.config import ENGINE_CONFIG
from config import USER_CONFIG_BASEDIR

LOGGER = logging.getLogger(__name__)
    
class BotSessionManager:
    def __init__(self, username):
        self._filename = username
        LOGGER.info(f"初始化 BotSessionManager，用户名: {username}")
        if not username:
            raise ValueError("用户名未设置")
        
        # 设置所有值的默认值
        self.bots = []
        self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}, 'name': '新话题'}]
        self.group_history_versions = [{'timestamp': datetime.now().isoformat(), 'group_history': [], 'name': '新群聊话题'}]
        self.current_history_version_idx = 0
        self.current_group_history_version_idx = 0
        self.bot_id_map = {}
        self.auto_speak = True
        self.chat_config = {
            'history_length': 10,
            'group_history_length': 20,
            'force_system_prompt': '',
            'group_user_prompt': '',
        }
        self.last_visited_page = 'main_page'

        # 加载数据并更新相应的属性
        self.load_data_from_file()
        self.fix_bot_setting()
        self.fix_history_names()
        self.fix_group_history_names()

    def load_data_from_file(self):
        if not self._filename:
            LOGGER.error("无法加载：用户名未设置")
            return
        try:
            file_path = f"{USER_CONFIG_BASEDIR}/{self._filename}.encrypt"
            if not os.path.exists(file_path):
                LOGGER.info(f"欢迎新用户: {self._filename}")
                return  # 使用默认值

            with open(file_path, 'r') as f:
                encrypted_data = f.read()
            decrypted_data = decrypt_data(encrypted_data)
            data = json.loads(decrypted_data)
            
            # 自动更新从文件读取到的参数
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            # 更新 chat_config，保留默认值
            if 'chat_config' in data:
                self.chat_config.update(data['chat_config'])

            if 'last_visited_page' in data:
                self.last_visited_page = data['last_visited_page']

        except Exception as e:
            LOGGER.error(f"加载配置文件时出错：{str(e)}")
            # 出错时保留默认值

    def save_data_to_file(self):
        self.ensure_valid_history_version()
        self.ensure_valid_group_history_version()
        if not self._filename:
            return
        
        # 创建一个不包含历史记录的 bots 副本
        bots_without_history = []
        for bot in self.bots:
            bot_copy = bot.copy()
            bot_copy.pop('history', None)
            bot_copy.pop('group_history', None)
            bots_without_history.append(bot_copy)
        
        data = {
            'bots': bots_without_history,
            'history_versions': self.history_versions,
            'group_history_versions': self.group_history_versions,
            'current_history_version_idx': self.current_history_version_idx,
            'current_group_history_version_idx': self.current_group_history_version_idx,
            'bot_id_map': self.bot_id_map,
            'chat_config': self.chat_config,
            'auto_speak': self.auto_speak,
            'last_visited_page': self.last_visited_page
        }
        encrypted_data = encrypt_data(json.dumps(data))
        with open(f"{USER_CONFIG_BASEDIR}/{self._filename}.encrypt", 'w') as f:
            f.write(encrypted_data)
    
    def ensure_valid_history_version(self):
        if not self.history_versions:
            self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}, 'name': '新话题'}]
            self.current_history_version_idx = 0
        elif self.current_history_version_idx >= len(self.history_versions):
            self.current_history_version_idx = len(self.history_versions) - 1

    def ensure_valid_group_history_version(self):
        if not self.group_history_versions:
            self.group_history_versions = [{'timestamp': datetime.now().isoformat(), 'group_history': [], 'name': '新群聊话题'}]
            self.current_group_history_version_idx = 0
        elif self.current_group_history_version_idx >= len(self.group_history_versions):
            self.current_group_history_version_idx = len(self.group_history_versions) - 1

    def remove_empty_new_history_version(self):
        self.history_versions = [
            version for version in self.history_versions
            if not (version['name'] == '新话题' and all(len(h) == 0 for h in version['histories'].values()))
        ]

    def remove_empty_new_group_history_version(self):
        self.group_history_versions = [
            version for version in self.group_history_versions
            if not (version['name'] == '新群聊话题' and len(version['group_history']) == 0)
        ]
    
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
                    version['name'] = f"对话{idx+1}. {content}"
                else:
                    version['name'] = f"新话题"

    def fix_group_history_names(self, specific_index=None):
        group_versions_to_update = [self.group_history_versions[specific_index]] if specific_index is not None else self.group_history_versions
        for idx, version in enumerate(group_versions_to_update):
            if specific_index is not None:
                idx = specific_index
            
            if 'name' not in version or version['name'] == '新群聊话题':
                first_prompt = self.get_first_group_prompt(version['group_history'])
                if first_prompt:
                    content = first_prompt.replace('\n', ' ').replace('\r', '')
                    if len(content) > 20:
                        content = f"{content[:20]}..."
                    version['name'] = f"群聊{idx+1}. {content}"
                else:
                    version['name'] = f"新群聊话题"

    def get_first_prompt(self, histories):
        for history in histories.values():
            for message in history:
                if message['role'] == 'user':
                    return message['content']
        return None

    def get_first_group_prompt(self, group_history):
        for message in group_history:
            if message.get('role') == 'user':
                return message.get('content', '')
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
            st.warning("所有机器人都已被禁用")

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
        
        self.remove_empty_new_history_version()

        new_version = {
            'timestamp': datetime.now().isoformat(),
            'histories': {bot['id']: [] for bot in self.bots if bot['enable']},
            'name': '新话题'
        }

        self.history_versions.append(new_version)
        self.current_history_version_idx = len(self.history_versions) - 1
            
        self.fix_history_names()
        self.save_data_to_file()
        return True

    def create_new_group_history_version(self):
        if self.is_current_group_history_empty():
            return False
        
        self.remove_empty_new_group_history_version()

        new_version = {
            'timestamp': datetime.now().isoformat(),
            'group_history': [],
            'name': '新群聊话题'
        }

        self.group_history_versions.append(new_version)
        self.current_group_history_version_idx = len(self.group_history_versions) - 1
            
        self.fix_group_history_names()
        self.save_data_to_file()
        return True

    def is_current_history_empty(self):
        if self.current_history_version_idx < len(self.history_versions):
            current_history = self.history_versions[self.current_history_version_idx]['histories']
            return all(len(history) == 0 for history in current_history.values())
        return True

    def is_current_group_history_empty(self):
        if self.current_group_history_version_idx < len(self.group_history_versions):
            current_group_history = self.group_history_versions[self.current_group_history_version_idx]['group_history']
            return len(current_group_history) == 0
        return True

    def get_participating_bots(self, version_index):
        if 0 <= version_index < len(self.history_versions):
            return set(self.history_versions[version_index]['histories'].keys())
        return set()

    def add_message_to_history(self, bot_id, message):
        if not message:
            return
        
        if bot_id and self.current_history_version_idx < len(self.history_versions):
            current_version = self.history_versions[self.current_history_version_idx]
            current_version['histories'].setdefault(bot_id, []).append(message)
        self.save_data_to_file()

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
        self.history_versions = [{'timestamp': datetime.now().isoformat(), 'histories': {}, 'name': '新话题'}]
        self.current_history_version_idx = 0
        self.fix_history_names()
        self.save_data_to_file()

    def clear_all_group_histories(self):
        self.group_history_versions = [{'timestamp': datetime.now().isoformat(), 'group_history': [], 'name': '新群聊话题'}]
        self.current_group_history_version_idx = 0
        
        # 清理所有机器人的群聊历史
        for bot in self.bots:
            if 'group_history' in bot:
                bot['group_history'] = []
        
        self.fix_group_history_names()
        self.save_data_to_file()  # 确保更改被保存到文件

    def get_current_history_by_bot(self, bot):
        bot_id = bot['id']
        if bot_id and self.current_history_version_idx < len(self.history_versions):
            current_version = self.history_versions[self.current_history_version_idx]
            return current_version['histories'].get(bot_id, [])
        return []

    def add_message_to_group_history(self, role, content, bot=None, tool=None):
        if not content:
            return
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if bot:
            message["bot_id"] = bot["id"]
            message["bot_name"] = bot["name"]
        if tool:
            message["tool_name"] = tool["name"]
        self.group_history_versions[self.current_group_history_version_idx]['group_history'].append(message)
        self.save_data_to_file()

    def get_current_group_history(self):
        if self.current_group_history_version_idx < len(self.group_history_versions):
            current_version = self.group_history_versions[self.current_group_history_version_idx]
            return current_version.get('group_history', [])
        return []

    def get_participating_bots_in_current_group_history(self):
        if self.current_group_history_version_idx < len(self.group_history_versions):
            current_version = self.group_history_versions[self.current_group_history_version_idx]
            bot_ids = set(message['bot_id'] for message in current_version['group_history'] if message['role'] == 'assistant' and 'bot_id' in message)
            return [bot for bot in self.bots if bot['id'] in bot_ids]
        return []

    def get_bot_config(self):
        return {
            'bots': self.bots,
            'history_versions': self.history_versions,
            'group_history_versions': self.group_history_versions,
            'current_history_version_idx': self.current_history_version_idx,
            'current_group_history_version_idx': self.current_group_history_version_idx,
            'bot_id_map': self.bot_id_map,
            'chat_config': self.chat_config
        }

    def validate_bot_config(self, config):
        required_keys = ['bots', 'history_versions', 'group_history_versions', 
                         'current_history_version_idx', 'current_group_history_version_idx', 'bot_id_map', 'chat_config']
        return all(key in config for key in required_keys)

    def update_bot_config(self, new_config):
        self.bots = new_config['bots']
        self.history_versions = new_config['history_versions']
        self.group_history_versions = new_config['group_history_versions']
        self.current_history_version_idx = new_config['current_history_version_idx']
        self.current_group_history_version_idx = new_config['current_group_history_version_idx']
        self.bot_id_map = new_config['bot_id_map']
        self.chat_config = new_config['chat_config']
        self.save_data_to_file()

    def get_chat_config(self):
        return self.chat_config

    def update_chat_config(self, new_config):
        self.chat_config.update(new_config)
        self.save_data_to_file()

    def get_default_history_by_bot(self, bot):
        bot_id = bot['id']
        if bot_id and len(self.history_versions) > 0:
            default_version = self.history_versions[0]
            return default_version['histories'].get(bot_id, [])
        return []

    def get_default_group_history(self):
        if len(self.group_history_versions) > 0:
            default_version = self.group_history_versions[0]
            return default_version.get('group_history', [])
        return []

    def add_message_to_default_history(self, bot_id, message):
        if bot_id and len(self.history_versions) > 0:
            default_version = self.history_versions[0]
            default_version['histories'].setdefault(bot_id, []).append(message)
        self.save_data_to_file()

    def add_message_to_default_group_history(self, role, message, bot={}):
        if len(self.group_history_versions) > 0:
            default_version = self.group_history_versions[0]
            default_version['group_history'].append({
                'bot_id': bot.get('id',''),
                'role': role,
                'content': message
            })
        self.save_data_to_file()

    def remove_last_group_message(self):
        if self.current_group_history_version_idx < len(self.group_history_versions):
            current_version = self.group_history_versions[self.current_group_history_version_idx]
            if current_version['group_history']:
                current_version['group_history'].pop()
                self.save_data_to_file()

    # 移除最后几条bot的回复，特点是role不是user
    def remove_recently_bot_group_message(self):
        if self.current_group_history_version_idx < len(self.group_history_versions):
            current_version = self.group_history_versions[self.current_group_history_version_idx]
            while len(current_version['group_history']) > 0 and current_version['group_history'][-1]['role'] != 'user':
                current_version['group_history'].pop()
                self.save_data_to_file()

    def get_auto_speak(self):
        return self.auto_speak

    def set_auto_speak(self, value):
        self.auto_speak = value
        self.save_data_to_file()

    def set_last_visited_page(self, page):
        self.last_visited_page = page
        self.save_data_to_file()
    
    def get_last_visited_page(self):
        return self.last_visited_page
    
    def get_bot_by_id(self, bot_id):
        return next((bot for bot in self.bots if bot['id'] == bot_id), None)
    
    def get_bot_by_name(self, bot_name):
        return next((bot for bot in self.bots if bot['name'] == bot_name), None)