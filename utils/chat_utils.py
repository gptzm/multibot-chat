import logging
import markdown
from bot.chat_router import ChatRouter
import streamlit.components.v1 as components
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import json
import random

class NewlineExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(NewlinePreprocessor(md), 'newline', 175)

class NewlinePreprocessor(Preprocessor):
    def run(self, lines):
        return [line + '  ' if line.strip() else line for line in lines]

LOGGER = logging.getLogger(__name__)

def delete_bot(bots, bot_name):
    return [bot for bot in bots if bot['name'] != bot_name]

def get_response_from_bot(prompt, bot, chat_config):
    results = []

    chat_router = ChatRouter(bot, chat_config)
    response_content = chat_router.send_message(prompt)
    # LOGGER.info(response_content)

    if 'history' not in bot:
        bot['history'] = []

    return response_content

def display_chat(bot, history):
    if not bot:
        return

    bot_html = f"""
    <style>
        .copy-button {{
            margin: 0 10px;
            border: none;
            border-radius: 5px;
            padding: 5px;
            cursor: pointer;
            transition: all 0.3s;
            background-color: #f8f8f800;
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
        }}
        .copy-button:hover {{
            background-color: #f0f0f0;
        }}
        .copy-button:active {{
            background-color: #e0e0e0;
        }}
        .chat-container {{
            border: 1px solid #ccc;
            min-height: 10em;
            border-radius: 10px;
            padding: 10px;
            background-color: #f9f9f9;
            height: 360px;
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
    <div id='chat-container-{bot['id']}' class='chat-container'>
    """

    for entry in history:
        content_markdown = markdown.markdown(
            str(entry['content']),
            extensions=[NewlineExtension(), "codehilite", "tables", "admonition", "sane_lists", "attr_list","meta", "toc"]
        )
        content_markdown_json = json.dumps(entry['content']).replace("'",'\\x27')
        random_id = str(random.randint(100000000000, 999999999999))


        if bot['enable']:
            LOGGER.info(f'\n\n\n[{entry["role"]}]:\n')
            LOGGER.info(str(entry['content']))
            LOGGER.info(content_markdown)

        if entry['role'] == 'user':
            bot_html += f"""<div class='message-user'>
                                <div style='display: flex; align-items: flex-end; max-width: 70%;'>
                                    <button onclick="copy_{random_id}(this)" class="copy-button">📋</button>
                                    <div class='message-user-content'>
                                        {content_markdown}
                                    </div>
                                </div>
                                <div class='user-avatar'>😄​</div>
                            </div>"""
            
        if entry['role'] == 'assistant':
            bot_html += f"""<div class='message-assistant'>
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
