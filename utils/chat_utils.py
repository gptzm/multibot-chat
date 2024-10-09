import logging
import markdown
from bot.chat_router import ChatRouter
import streamlit.components.v1 as components
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import html
import random
import streamlit as st
from bs4 import BeautifulSoup
import base64
from utils.chat_styles import get_chat_container_style

LOGGER = logging.getLogger(__name__)

class SVGProcessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        in_block = False
        block_content = []
        block_type = ''
        
        for line in lines:
            if line.strip().startswith('```') and not in_block:
                block_type = line.strip()[3:].lower()
                if block_type in ['svg', 'xml', 'html']:
                    in_block = True
                    block_content = []
                else:
                    new_lines.append(line)
            elif line.strip() == '```' and in_block:
                in_block = False
                content_string = '\n'.join(block_content)
                try:
                    soup = BeautifulSoup(content_string, 'html.parser')
                    root = soup.find()
                    if root and root.name == 'svg':
                        svg_bytes = str(root).encode('utf-8')
                        base64_svg = base64.b64encode(svg_bytes).decode('utf-8')
                        new_lines.append(f'![SVG图片](data:image/svg+xml;base64,{base64_svg})')
                    else:
                        new_lines.extend([f'```{block_type}'] + block_content + ['```'])
                except Exception as e:
                    LOGGER.error(f"错误解析{block_type.upper()}内容: {e}")
                    new_lines.extend([f'```{block_type}'] + block_content + ['```'])
            elif in_block:
                block_content.append(line)
            else:
                new_lines.append(line)
        
        return new_lines
class SVGExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(SVGProcessor(md), 'svg_processor', 175)
class CodeProcessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        in_block = False
        block_content = []
        block_type = ''
        
        for line in lines:
            if line.strip().startswith('```') and not in_block:
                block_type = line.strip()[3:].lower() or 'text'
                in_block = True
                block_content = []
                new_lines.append(f'<div class="code-block"><div class="code-header"><span class="code-language">{block_type}</span><button class="code-copy-btn" onclick="copyCode(this)"><span>复制</span></button></div>')
                new_lines.append(line)
            elif line.strip() == '```' and in_block:
                in_block = False
                new_lines.extend(block_content)
                new_lines.append(line)
                new_lines.append('</div>')
            elif in_block:
                block_content.append(line)
            else:
                new_lines.append(line)
        
        return new_lines

class CodeExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(CodeProcessor(md), 'code_processor', 175)

# 移除原有的process_svg_content函数

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

def display_chat(bot, history):
    if not bot:
        return

    bot_html = f"""
        {get_chat_container_style()}
        <div id='chat-container-{bot['id']}' class='chat-container' style='height: 360px;'>
    """

    for entry in history:
        content = entry.get('content', '')
        content_markdown = markdown.markdown(
            str(content),
            extensions=[
                SVGExtension(),
                "nl2br",
                "codehilite",
                "tables",
                "admonition",
                "sane_lists",
                "attr_list",
                "toc",
                "fenced_code",
                CodeExtension(),
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
        content_markdown = markdown.markdown(
            str(content),
            extensions=[
                SVGExtension(),
                "nl2br",
                "codehilite",
                "tables",
                "admonition",
                "sane_lists",
                "attr_list",
                "toc",
                "fenced_code",
                CodeExtension(),
            ]
        )

        content_markdown_repr = repr(entry['content'])
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
                            function copy_{random_id}(element) {{
                                const textToCopy = {content_markdown_repr};

                                if (navigator.clipboard && navigator.clipboard.writeText) {{
                                    // 使用 Clipboard API 复制
                                    navigator.clipboard.writeText(textToCopy).then(() => {{
                                        showCopyTextSuccess(element);
                                        return;
                                    }});
                                }} else if(fallbackCopyText(textToCopy, element)) {{
                                    // 使用备用方法复制
                                    showCopyTextSuccess(element);
                                }}
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
        <script>
            function fallbackCopyText(text, element) {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';  // 避免影响页面布局
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                try {
                    if (document.execCommand('copy')) {
                        document.body.removeChild(textarea);
                        return true;
                    } else {
                        console.error('execCommand 复制失败');
                        document.body.removeChild(textarea);
                        return false;
                    }
                } catch (err) {
                    console.error('execCommand 复制出错: ', err);
                    document.body.removeChild(textarea);
                    return false;
                }
            }

            function showCopyTextSuccess(element) {
                element.innerHTML = '✅';
                setTimeout(() => {
                    element.innerHTML = '📋';
                }, 500);
            }

            function showCopyCodeSuccess(element) {
                element.innerHTML = '已复制';
                setTimeout(() => {
                    element.innerHTML = '复制';
                }, 500);
            }
        </script>
        <script>
            function copyCode(button) {
                const codeBlock = button.closest('.code-block').querySelector('pre');
                const code = codeBlock.innerText;
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    // 使用 Clipboard API 复制
                    navigator.clipboard.writeText(code).then(() => {
                        showCopyCodeSuccess(button);
                        return;
                    });
                } else if(fallbackCopyText(code, button)) {
                    // 使用备用方法复制
                    showCopyCodeSuccess(button);
                }
            }
        </script>
    """
    components.html(bot_html, height=600)