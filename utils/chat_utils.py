import logging
import markdown
from bot.chat_router import ChatRouter
import streamlit.components.v1 as components

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
    <div id='chat-container-{bot['id']}' class='chat-container' style='border: 1px solid #ccc; min-height: 10em;border-radius: 10px; padding: 10px; background-color: #f9f9f9; height:360px; overflow-y: scroll; '>
    """

    for entry in history:
        # LOGGER.warn(entry)
        content_markdown = markdown.markdown(str(entry['content']))
        if entry['role'] == 'user':
            bot_html += f"""<div style='display: flex; justify-content: flex-end; margin-bottom: 10px;'>
                                <div style='background-color: #e0ffe0; border-radius: 10px; padding: 10px; max-width: 70%;'>
                                    {content_markdown}
                                </div>
                                <div style='background-color: #eee; width: 40px; height: 40px; border-radius: 50%; margin-left: 10px; display: flex; justify-content: center; align-items: center; font-size: 32px;'>😄​</div>
                            </div>"""
            
        if entry['role'] == 'assistant':
            bot_html += f"""<div style='display: flex; margin-bottom: 10px;'>
                            <div style='background-color: #eee; width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 32px;'>{bot.get('avatar', '🤖')}</div>
                            <div style='background-color: #f0f0f0; border-radius: 10px; padding: 10px; max-width: 70%;'>
                                {content_markdown}
                            </div>
                        </div>"""
    
    bot_html += f"""
    </div>
    <script>
        var chatContainer = document.getElementById('chat-container-{bot['id']}');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    </script>
    """
    components.html(bot_html, height=400)