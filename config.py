import os
import tempfile

# 是否启用自动登录功能
# 如果设置为 True，系统将为用户自动创建临时账号
AUTO_LOGIN = False

# token 的过期时间（以秒为单位）
# 默认为 86400 秒（1天）
# 如果 AUTO_LOGIN 为 True，此值会被自动设置为一个非常大的数（99999999999999），相当于永不过期
TOKEN_EXPIRATION = 86400

# token 文件存储的基础目录
# 如果不设置（即为空字符串），系统会根据 AUTO_LOGIN 的值选择合适的目录：
# - 如果 AUTO_LOGIN 为 True，将使用用户主目录下的 'streamlit_tokens' 文件夹
# - 如果 AUTO_LOGIN 为 False，将使用系统临时目录下的 'streamlit_tokens' 文件夹
TOKEN_BASEDIR = ""

# 根据 AUTO_LOGIN 和 TOKEN_BASEDIR 的设置来确定最终的 TOKEN_DIR
if AUTO_LOGIN:
    TOKEN_EXPIRATION = 99999999999999
    TOKEN_DIR = os.path.join(os.path.expanduser("~"), 'streamlit_tokens')
elif TOKEN_BASEDIR:
    TOKEN_DIR = os.path.join(TOKEN_BASEDIR, 'streamlit_tokens')
else:
    TOKEN_DIR = os.path.join(tempfile.gettempdir(), 'streamlit_tokens')

# 密钥，用于加密和解密 token
# 在生产环境中，应该使用更安全的方式来存储和获取这个密钥
SECRET_KEY = 'fG7g5OlCWEXKzDSPOrt8sccn68ZWtf0S'

# 用户数据文件的路径
USER_DATA_FILE = 'users.json'

# 日志级别
LOG_LEVEL = 'INFO'