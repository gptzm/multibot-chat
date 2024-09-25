# MultiBot Chat

MultiBot Chat 是一个基于 Streamlit 的多机器人聊天应用，支持多种大语言模型（LLM）API，包括 AzureOpenAI、ChatGLM、CoZe、Qwen、Ollama、DeepSeek、Moonshot 和 Yi。

## 功能特点

- 支持多个 AI 聊天机器人同时对话
- 可以自定义每个机器人的系统提示（System Prompt）
- 支持多种大语言模型 API
- 用户注册和登录功能
- 聊天历史记录保存和查看
- 可调整的对话上下文长度

## 安装

1. 克隆仓库：
``` bash
git clone https://github.com/yourusername/multibot-chat.git
cd multibot-chat
```

2. 创建并激活虚拟环境（可选但推荐）：
``` bash
python -m venv venv
source venv/bin/activate # 在 Windows 上使用 venv\Scripts\activate
```

3. 安装依赖：
``` bash
pip install -r requirements.txt
```

## 配置

1. 在项目根目录创建 `.streamlit/secrets.toml` 文件，并添加必要的 API 密钥和其他敏感信息。

2. 根据需要修改 `bot/config.py` 文件中的模型配置。

## 运行

在项目根目录下运行以下命令：
``` bash
streamlit run app.py
```

或者，您可以使用提供的脚本：

- 在 Windows 上：双击 `multibot.bat`
- 在 Linux/Mac 上：运行 `./multibot.sh`

## 使用方法

1. 注册新用户或登录现有账户
2. 在侧边栏中添加新的聊天机器人
3. 选择要启用的机器人
4. 在聊天输入框中输入消息，与多个机器人同时对话
5. 使用侧边栏中的选项管理聊天设置和历史记录


