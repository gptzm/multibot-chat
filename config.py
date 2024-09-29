import os
import tempfile
import streamlit as st
import logging
from bot.config import ENGINE_CONFIG

# token 的过期时间（以秒为单位）
# 默认为 86400 秒（1天）
TOKEN_EXPIRATION = 86400

# token 文件存储的基础目录
# 如果不设置（即为空字符串），系统会使用系统临时目录：
# 如果设置路径，将使用 TOKEN_BASEDIR 下的 'streamlit_tokens' 文件夹
TOKEN_BASEDIR = ""
if TOKEN_BASEDIR:
    TOKEN_DIR = os.path.join(TOKEN_BASEDIR, 'streamlit_tokens')
else:
    TOKEN_DIR = os.path.join(tempfile.gettempdir(), 'streamlit_tokens')

# 默认密钥，用于加密和解密 token
# 在生产环境中，更建议设置在 ~/.streamlit/secrets.toml 中
# 必须是 32 字节长度的大小写字母数字字符串
SECRET_KEY = 'fG7g5OlCWEXKzDSPOrt8sccn68ZWtf0S'

# 用户数据文件的路径
USER_DATA_FILE = 'users.json'

# 表情选项
EMOJI_OPTIONS = ["🤖", "🦾", "🧠", "💡", "🔮", "🎭", "🦄", "🐼", "🦊", "🐶", "🐱", "🦁", "🐯", "🐻", "🐨", "😄", "🤡", "👻", "😈", "🤠", "🙊", "😽", "👽", "🧑‍🎓", "🧑‍💼", "🧑‍🎨", "🧑‍✈️", "🥷"]

# 引擎选项
ENGINE_OPTIONS = list(ENGINE_CONFIG.get('engines', {}).keys())

# 定义群聊和私聊的emoji表情
GROUP_CHAT_EMOJI = "👥"
PRIVATE_CHAT_EMOJI = "👤"

# 是否显示密钥信息
SHOW_SECRET_INFO = True

# 日志设置
LOG_LEVEL = 'INFO'
logging.basicConfig(level=LOG_LEVEL)
LOGGER = logging.getLogger(__name__)
