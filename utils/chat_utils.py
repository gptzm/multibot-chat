import logging
import markdown
from bot.chat_router import ChatRouter
import streamlit.components.v1 as components
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import json
import random
import streamlit as st


class NewlineExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(NewlinePreprocessor(md), 'newline', 175)

class NewlinePreprocessor(Preprocessor):
    def run(self, lines):
        return [line + '  ' if line.strip() else line for line in lines]

LOGGER = logging.getLogger(__name__)

def get_response_from_bot(prompt, bot, history):
    bot_manager = st.session_state.bot_manager
    # 每次调用时获取最新的chat_config
    latest_chat_config = bot_manager.get_chat_config()
    LOGGER.info(f"Latest chat_config: {latest_chat_config}")
    chat_router = ChatRouter(bot, latest_chat_config)
    response_content = chat_router.send_message(prompt, history)
    return response_content

def get_response_from_bot_group(prompt, bot, group_history):
    bot_manager = st.session_state.bot_manager
    # 每次调用时获取最新的chat_config
    latest_chat_config = bot_manager.get_chat_config()
    LOGGER.info(f"Latest chat_config for group chat: {latest_chat_config}")
    chat_router = ChatRouter(bot, latest_chat_config)
    response_content = chat_router.send_message_group(prompt, group_history)
    return response_content


def get_chat_container_style():
    return f"""
    <style>
        .message:hover .copy-button {{
            visibility: visible;
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
            padding: 10px;
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
            margin-bottom: 10px;
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
            padding: 10px;
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
        content_markdown = markdown.markdown(
            str(entry['content']),
            extensions=[NewlineExtension(), "codehilite", "tables", "admonition", "sane_lists", "attr_list","meta", "toc"]
        )
        content_markdown_json = json.dumps(entry['content']).replace("'",'\\x27')
        random_id = str(random.randint(100000000000, 999999999999))

        if entry['role'] == 'user':
            bot_html += f"""<div class='message message-user'>
                                <div style='display: flex; align-items: flex-end; max-width: 70%;'>
                                    <button onclick="copy_{random_id}(this)" class="copy-button">📋</button>
                                    <div class='message-user-content'>
                                        {content_markdown}
                                    </div>
                                </div>
                                <div class='user-avatar'>😄​</div>
                            </div>"""
            
        if entry['role'] == 'assistant':
            bot_html += f"""<div class='message message-assistant'>
                            <div class='bot-avatar'>{bot.get('avatar', '🤖')}</div>
                            <div style='display: flex; align-items: flex-end; max-width: 70%;'>
                                <div class='message-assistant-content'>
                                    {content_markdown}
                                </div>
                                <button onclick="copy_{random_id}(this)" class="copy-button">📋</button>
                            </div>
                        </div>"""
        
        bot_html += f"""<script>
                            function copy_{random_id}(element){{
                                navigator.clipboard.writeText({content_markdown_json}).then(() => {{
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
        content = entry['content']
        content_markdown = markdown.markdown(
            str(content),
            extensions=[NewlineExtension(), "codehilite", "tables", "admonition", "sane_lists", "attr_list","meta", "toc"]
        )
        content_markdown_json = json.dumps(repr(content)).replace("'",'\\x27')
        random_id = str(random.randint(100000000000, 999999999999))

        if role == 'user':
            bot_html += f"""<div class='message message-user'>
                                <div style='display: flex; align-items: flex-end; max-width: 70%;'>
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
                                <div style='display: flex; align-items: flex-end; max-width: 70%;'>
                                    <div class='message-assistant-content'>
                                        <strong>{bot.get('name')}:</strong><br>
                                        {content_markdown}
                                    </div>
                                    <button onclick="copy_{random_id}(this)" class="copy-button">📋</button>
                                </div>
                            </div>"""
        
        bot_html += f"""<script>
                            function copy_{random_id}(element){{
                                navigator.clipboard.writeText({content_markdown_json}).then(() => {{
                                    const lastInnerHTML = element.innerHTML;
                                    element.innerHTML = '✅';
                                    setTimeout(() => {{
                                        element.innerHTML = lastInnerHTML;
                                    }}, 300);
                                }});
                            }}
                        </script>"""
    
    bot_html += """
        </div>
        <script>
            var chatContainer = document.getElementById('group-chat-container');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        </script>
    """
    components.html(bot_html, height=600)
