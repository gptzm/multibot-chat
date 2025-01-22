import os
import tempfile
import logging
import string
import random
from bot.config import ENGINE_CONFIG

# token 的过期时间（以秒为单位）
# 默认为 86400 秒（1天）
TOKEN_EXPIRATION = int(os.getenv('MULTIBOT_TOKEN_EXPIRATION', 86400))

# token 文件存储的基础目录
# 如果不设置（即为空字符串），系统会使用系统临时目录：
# 如果设置路径，将使用 TOKEN_BASEDIR 下的 'streamlit_tokens' 文件夹
TOKEN_BASEDIR = ""
if TOKEN_BASEDIR:
    TOKEN_DIR = os.path.join(TOKEN_BASEDIR, 'streamlit_tokens')
else:
    TOKEN_DIR = os.path.join(tempfile.gettempdir(), 'streamlit_tokens')

secret_key_file = os.getenv('MULTIBOT_SECRET_KEY_FILE', 'secret.key')

if os.path.exists(secret_key_file):
    with open(secret_key_file, 'r') as f:
        SECRET_KEY = f.read().strip()
else:
    characters = string.ascii_letters + string.digits
    SECRET_KEY = ''.join(random.choice(characters) for _ in range(32))
    with open(secret_key_file, 'w') as f:
        f.write(SECRET_KEY)

# 用户配置文件的存储基础目录
USER_CONFIG_BASEDIR = os.getenv('MULTIBOT_USER_CONFIG_BASEDIR', './user_config')

# 用户数据文件的路径
USER_DATA_FILE = os.getenv('MULTIBOT_USER_DATA_FILE', 'users.json')

# 表情选项
EMOJI_OPTIONS = ["🤖", "🦾", "🧠", "💡", "✏️", "🔭", "🔮", "🎭", "😄", "😘", "🤪", "🧐", "🤠", "🦄", "🐼", "🦊", "🐶", "🐱", "🦁", "🐯", "🐻", "🐨", "🤡", "👻", "😈", "🤠", "🙊", "😽", "🐷", "🐰", "🐼", "🐮", "🐺", "👽", "🧑‍🎓", "🧑‍💼", "🧑‍🎨", "🧑‍✈️", "🥷", "🧙", "🧞‍♂️"]

# 引擎选项
ENGINE_OPTIONS = list(ENGINE_CONFIG.get('engines', {}).keys())

# 引擎名称映射字典，key为引擎标识符，value为引擎显示名称
ENGINE_NAMES = {k: v.get('name',k) for k, v in ENGINE_CONFIG.get('engines', {}).items()}


# 定义群聊和私聊的emoji表情
GROUP_CHAT_EMOJI = "👥"
PRIVATE_CHAT_EMOJI = "👤"

# 访客账号，用逗号分隔开
GUEST_USERNAMES = [username.strip() for username in os.getenv('MULTIBOT_GUEST_USERNAMES', 'guest').split(',')]

# 开发者账号，可用于调试
DEVELOPER_USERNAME = os.getenv('MULTIBOT_DEVELOPER_USERNAME', '')

# 是否显示密钥信息
SHOW_SECRET_INFO = os.getenv('MULTIBOT_SHOW_SECRET_INFO', 'False').lower() == 'true'

# 允许注册
ENABLED_REGISTER = os.getenv('MULTIBOT_ENABLED_REGISTER', 'True').lower() == 'true'

# 日志设置
LOG_LEVEL = os.getenv('MULTIBOT_LOG_LEVEL', 'INFO')
logging.basicConfig(level=LOG_LEVEL)
LOGGER = logging.getLogger(__name__)

# 规划引擎所用模型，支持所有兼容OpenAI接口格式的引擎
BASS_LLM_MODEL = os.getenv('MULTIBOT_BASE_LLM_MODEL', 'qwen2.5:3b')
BASS_LLM_BASE_URL = os.getenv('MULTIBOT_BASE_LLM_BASE_URL', 'http://127.0.0.1:11434/v1')
BASS_LLM_API_KEY = os.getenv('MULTIBOT_BASE_LLM_API_KEY', 'ollama')