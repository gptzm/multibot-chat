import logging
import markdown
from bot.chat_router import ChatRouter
import streamlit.components.v1 as components
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import html
import random
import streamlit as st
import re
from bs4 import BeautifulSoup
import base64

LOGGER = logging.getLogger(__name__)

def get_response_from_bot(prompt, bot, history):
    bot_manager = st.session_state.bot_manager
    # 每次调用时获取最新的chat_config
    latest_chat_config = bot_manager.get_chat_config()
    LOGGER.info(f"Latest chat_config: {latest_chat_config}")
    chat_router = ChatRouter(bot, latest_chat_config)
    response_content = chat_router.send_message(prompt, history)
    LOGGER.info(f"Response content: {response_content}")
    return response_content

def get_response_from_bot_group(prompt, bot, group_history):
    bot_manager = st.session_state.bot_manager
    # 每次调用时获取最新的chat_config
    latest_chat_config = bot_manager.get_chat_config()
    LOGGER.info(f"Latest chat_config for group chat: {latest_chat_config}")
    chat_router = ChatRouter(bot, latest_chat_config)
    response_content = chat_router.send_message_group(prompt, group_history)
    LOGGER.info(f"Response content: {response_content}")
    return response_content

def process_svg_content(content):
    def replace_svg_block(match):
        svg_content = match.group(2)
        # 使用 BeautifulSoup 解析 SVG 内容
        try:
            soup = BeautifulSoup(svg_content, 'html.parser')
            svg = soup.find('svg')
        except Exception as e:
            LOGGER.error(f"错误解析SVG内容: {e}")
            return match.group(0)
            
        if svg:
            # 移除所有脚本和事件属性
            for tag in svg.find_all():
                for attr in list(tag.attrs):
                    if attr.startswith('on') or attr == 'href':
                        del tag[attr]
            # 移除所有 script 标签
            for script in svg.find_all('script'):
                script.decompose()

            # 将SVG转换为base64编码
            svg_string = str(svg)
            svg_bytes = svg_string.encode('utf-8')
            base64_svg = base64.b64encode(svg_bytes).decode('utf-8')
            
            # 使用Markdown语法引用base64编码的SVG
            return f'![SVG图片](data:image/svg+xml;base64,{base64_svg})'
        
        return match.group(0)
    
    # 修改正则表达式以匹配 Markdown 处理后的内容
    pattern = r'```(svg)\n(.*?)```'
    return re.sub(pattern, replace_svg_block, content, flags=re.MULTILINE|re.DOTALL|re.IGNORECASE)

def get_chat_container_style():
    return f"""
    <style>
        .message:hover .copy-button {{
            visibility: visible;
        }}
        .message img{{
            max-width: 100%;
            height: auto;
        }}
        .copy-button {{
            visibility: hidden;
            font-size: 1.2em;
            margin: 0 8px;
            border: none;
            border-radius: 5px;
            padding: 2px;
            cursor: pointer;
            background-color: #f8f8f800;
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
        }}
        .copy-button:hover {{
            background-color: #f0f0f0;
            transition: all 0.3s;
        }}
        .copy-button:active {{
            background-color: #e0e0e0;
            transition: all 0.3s;
        }}
        .chat-container {{
            border: 1px solid #ccc;
            min-height: 10em;
            border-radius: 10px;
            padding: 10px;
            background-color: #f9f9f9;
            overflow-y: scroll;
        }}
        .message-user {{
            display: flex;
            justify-content: flex-end;
            margin-bottom: 10px;
        }}
        .message-user-content {{
            background-color: #e0ffe0;
            border-radius: 10px;
            padding: 0 15px;
            overflow-wrap: break-word;
            word-break: break-all;
        }}
        .user-avatar {{
            background-color: #eee;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-left: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 32px;
        }}
        .message-assistant {{
            display: flex;
            margin-bottom: 15px;
        }}
        .bot-avatar {{
            background-color: #eee;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 32px;
        }}
        .message-assistant-content {{
            background-color: #f0f0f0;
            border-radius: 10px;
            padding: 0 15px;
            overflow-wrap: break-word;
            word-break: break-all;
        }}
        .bot-name {{
            margin-top: 5px;
            margin-bottom: 10px;
        }}
        .tips {{
            width: 100%;
            text-align: center;
            color: #bbb;
            user-select: none;
            margin-top: 15px;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
    </style>
    """

def display_chat(bot, history):
    if not bot:
        return

    bot_html = f"""
        {get_chat_container_style()}
        <div id='chat-container-{bot['id']}' class='chat-container' style='height: 360px;'>
    """

    for entry in history:
        content = entry.get('content', '')
        content_process = process_svg_content(content)
        content_markdown = markdown.markdown(
            str(content_process),
            extensions=[
                "nl2br",
                "codehilite",
                "tables",
                "admonition",
                "sane_lists",
                "attr_list",
                "toc",
                "fenced_code",
            ]
        )
        
        content_markdown_repr = repr(entry['content'])
        random_id = str(random.randint(100000000000, 999999999999))

        if entry['role'] == 'user':
            bot_html += f"""<div class='message message-user'>
                                <div style='display: flex; align-items: flex-end; max-width: 80%;'>
                                    <button onclick="copy_{random_id}(this)" class="copy-button">📋</button>
                                    <div class='message message-user-content'>
                                        {content_markdown}
                                    </div>
                                </div>
                                <div class='user-avatar'>😄​</div>
                            </div>"""
            
        if entry['role'] == 'assistant':
            bot_html += f"""<div class='message message-assistant'>
                            <div class='bot-avatar'>{bot.get('avatar', '🤖')}</div>
                            <div style='display: flex; align-items: flex-end; max-width: 80%;'>
                                <div class='message-assistant-content'>
                                    {content_markdown}
                                </div>
                                <button onclick="copy_{random_id}(this)" ontouch="copy_{random_id}(this)" class="copy-button">📋</button>
                            </div>
                        </div>"""
        
        bot_html += f"""<script>
                            function copy_{random_id}(element){{
                                navigator.clipboard.writeText({content_markdown_repr}).then(() => {{
                                    const lastInnerHTML = element.innerHTML;
                                    element.innerHTML = '✅';
                                    setTimeout(() => {{
                                        element.innerHTML = lastInnerHTML;
                                    }}, 300);
                                }});
                            }}
                        </script>"""
        
    bot_html += f"""
        </div>
        <script>
            var chatContainer = document.getElementById('chat-container-{bot['id']}');
            var lastAssistantMessage = chatContainer.querySelector('.message-assistant:last-of-type');
            if (lastAssistantMessage) {{
                chatContainer.scrollTop = Math.max(0, lastAssistantMessage.offsetTop - 100);
            }} else {{
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }}
            
        </script>
    """
    components.html(bot_html, height=400)

def display_group_chat(bots, history):
    bot_html = f"""
        {get_chat_container_style()}
        <div id='group-chat-container' class='chat-container' style='height: 560px;'>
    """

    for entry in history:
        bot_id = entry.get('bot_id','')
        role = entry.get('role','')
        content = entry.get('content', '')
        content_process = process_svg_content(content)
        
        content_markdown = markdown.markdown(
            str(content_process),
            extensions=[
                "nl2br",
                "codehilite",
                "tables",
                "admonition",
                "sane_lists",
                "attr_list",
                "toc",
                "fenced_code",
            ]
        )
        
        
        LOGGER.info(f'替换后：{str(content_markdown)}')
        content_markdown_repr = repr(content_markdown)
        random_id = str(random.randint(100000000000, 999999999999))

        if 'tool_name' in entry:
            bot_html += f"""<div class='message message-assistant'>
                            <div class='bot-avatar'>🛠️</div>
                            <div style='display: flex; flex-direction: column; max-width: 80%;'>
                                <div class='bot-name'>{html.escape(entry['tool_name'])}</div>
                                <div style='display: flex; align-items: flex-end;'>
                                    <div class='message-assistant-content'>
                                        {content_markdown}
                                    </div>
                                    <button onclick="copy_{random_id}(this)" ontouch="copy_{random_id}(this)" class="copy-button">📋</button>
                                </div>
                            </div>
                        </div>"""
        elif role == 'user':
            bot_html += f"""<div class='message message-user'>
                                <div style='display: flex; align-items: flex-end; max-width: 80%;'>
                                    <button onclick="copy_{random_id}(this)" class="copy-button">📋</button>
                                    <div class='message-user-content'>
                                        {content_markdown}
                                    </div>
                                </div>
                                <div class='user-avatar'>😄​</div>
                            </div>"""
        else:
            bot = next((b for b in bots if b['id'] == bot_id), None)
            if bot:
                avatar = bot.get('avatar', '🤖')
                bot_html += f"""<div class='message message-assistant'>
                                <div class='bot-avatar'>{avatar}</div>
                                <div style='display: flex; flex-direction: column; max-width: 80%;'>
                                    <div class='bot-name'>{html.escape(bot.get('name'))}</div>
                                    <div style='display: flex; align-items: flex-end;'>
                                        <div class='message-assistant-content'>
                                            {content_markdown}
                                        </div>
                                        <button onclick="copy_{random_id}(this)" ontouch="copy_{random_id}(this)" class="copy-button">📋</button>
                                    </div>
                                </div>
                            </div>"""
        
        bot_html += f"""<script>
                            function copy_{random_id}(element){{
                                navigator.clipboard.writeText({content_markdown_repr}).then(() => {{
                                    const lastInnerHTML = element.innerHTML;
                                    element.innerHTML = '✅';
                                    setTimeout(() => {{
                                        element.innerHTML = lastInnerHTML;
                                    }}, 300);
                                }});
                            }}
                        </script>"""
    
    bot_manager = st.session_state.bot_manager
    chat_config = bot_manager.get_chat_config()
    group_user_prompt = chat_config.get('group_user_prompt', '').replace('\n', ' ').replace('\r', ' ')
    if len(group_user_prompt) > 20:
        group_user_prompt = group_user_prompt[:20] + '...'
    if group_user_prompt and history[-1].get('role') != 'user':
        bot_html += f'<div class="tips">Bot接力提示词：{html.escape(group_user_prompt)}</div>'

    bot_html += """
        </div>
        <script>
            var chatContainer = document.getElementById('group-chat-container');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        </script>
    """
    components.html(bot_html, height=600)