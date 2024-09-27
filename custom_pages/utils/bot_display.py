import streamlit as st
from utils.chat_utils import get_response_from_bot, get_response_from_bot_group, display_chat, display_group_chat
from custom_pages.utils.dialogs import edit_bot, add_new_bot
from datetime import datetime, date
import random
from config import EMOJI_OPTIONS, ENGINE_OPTIONS

def display_active_bots(bot_manager, prompt, show_bots):
    num_bots = len(show_bots)
    num_cols = min(2, num_bots)
    cols = st.columns(num_cols)

    for i, bot in enumerate(show_bots):
        if not bot['enable']:
            continue
        col = cols[i % num_cols]
        with col:
            button_box, title_box = st.columns([1, 10], gap="small")
            
            # 获取当前bot的历史记录
            current_history = bot_manager.get_current_history_by_bot(bot)
            
            if prompt:
                response_content = get_response_from_bot(prompt, bot, bot_manager.get_current_history_by_bot(bot))
                bot_manager.add_message_to_history(bot['id'], {"role": "user", "content": prompt})
                bot_manager.add_message_to_history(bot['id'], {"role": "assistant", "content": response_content})
                bot_manager.fix_history_names(bot_manager.current_history_version)
                current_history = bot_manager.get_current_history_by_bot(bot)

            if current_history:
                display_chat(bot, current_history)

                with button_box:
                    show_bot_avatar(bot)
                with title_box:
                    show_bot_title(bot)

def display_inactive_bots(bot_manager, show_bots):
    show_bots = show_bots + [{'id': 'new_bot', 'avatar': '⚡', 'name': '新增一个Bot', 'engine': f'支持{len(ENGINE_OPTIONS)}种API引擎'}]

    num_bots = len(show_bots)
    
    if st.session_state.page == 'main_page':
        num_cols = min(2, num_bots)
        title_box_width = 10
    else:
        num_cols = 4
        title_box_width = 4

    cols = st.columns(num_cols, gap="large")

    for i, bot in enumerate(show_bots):
        col = cols[i % num_cols]
        with col:
            button_box, title_box = st.columns([1, title_box_width], gap="small")
            
            with button_box:
                if bot['id'] == 'new_bot':
                    if st.button(bot.get('avatar', '') or '🤖', key=f"__edit_enabled_bot_{bot['id']}"):
                        st.session_state.avatar = random.choice(EMOJI_OPTIONS)
                        add_new_bot()
                else:
                    show_bot_avatar(bot)
                    
            with title_box:
                show_bot_title(bot)
                if bot['id'] == 'new_bot':
                    if st.button("创建Bot好友", key=f"create_new_bot_{bot['id']}", type="primary"):
                        st.session_state.avatar = random.choice(EMOJI_OPTIONS)
                        add_new_bot()
                else:
                    show_toggle_bot_enable(bot)
                    if st.session_state.page == 'main_page':
                        all_histories = bot_manager.get_all_histories(bot)
                        non_empty_histories = [h for h in all_histories[:-1] if h['history']]

                        if non_empty_histories:
                            num_topics = len(non_empty_histories)
                            with st.expander(f"查看 {num_topics} 个历史话题"):
                                for i, history in enumerate(reversed(non_empty_histories)):
                                    try:
                                        timestamp = datetime.fromisoformat(history['timestamp'])
                                    except ValueError:
                                        timestamp = datetime.strptime(history['timestamp'], "%Y-%m-%d %H:%M:%S")
                                    
                                    today = date.today()
                                    if timestamp.date() == today:
                                        formatted_time = f"今天 {timestamp.strftime('%H:%M')}"
                                    else:
                                        formatted_time = timestamp.strftime("%Y年%m月%d日 %H:%M")
                                    
                                    st.markdown(f"**{history['name']}** - {formatted_time}")
                                    display_chat(bot, history['history'])
            
            if i < len(show_bots) - num_cols:
                st.markdown("---")

def display_group_chat_area(bot_manager, show_bots, histories):
    col1, col2 = st.columns([1,1], gap="small")
    with col1:
        if histories:
            participating_bots = bot_manager.get_participating_bots_in_current_group_history()
            display_group_chat(participating_bots, histories)
            
            # 添加删除最近回复的按钮
            if histories:
                if st.button(f"删除最后一条的回复", key="delete_last_reply"):
                    bot_manager.remove_last_group_message()
                    st.rerun()
    with col2:
        enabled_bots = [bot for bot in show_bots if bot['enable']]
        disabled_bots = [bot for bot in show_bots if not bot['enable']]

        st.markdown("### 幕僚")
        st.session_state.auto_speak = st.checkbox("幕僚自动发言", value=True)
        if enabled_bots:
            num_bots = len(enabled_bots)
            num_cols = min(2, num_bots)

            cols = st.columns(num_cols)

            for i, bot in enumerate(enabled_bots):
                col = cols[i % num_cols]
                with col:
                    if st.button(f"{bot.get('avatar', '🤖')} {bot['name']}\n\n{bot['engine']} {bot['model']}", key=f"group_bot_{bot['id']}", use_container_width=True):
                        chat_config = bot_manager.get_chat_config()
                        group_user_prompt = chat_config.get('group_user_prompt')
                        response_content = get_response_from_bot_group(group_user_prompt, bot, histories)
                        bot_manager.add_message_to_group_history("assistant", response_content, bot=bot)
                        bot_manager.save_data_to_file()
                        st.rerun()
        
        st.markdown("### 观众")
        st.markdown("未启用的Bot作为观众，点击按钮可以手动发言")
        if disabled_bots:
            num_bots = len(disabled_bots)
            num_cols = min(2, num_bots)

            cols = st.columns(num_cols)

            for i, bot in enumerate(disabled_bots):
                col = cols[i % num_cols]
                with col:
                    if st.button(f"{bot.get('avatar', '🤖')} {bot['name']}\n\n{bot['engine']} {bot['model']}", key=f"group_bot_{bot['id']}", use_container_width=True):
                        chat_config = bot_manager.get_chat_config()
                        group_user_prompt = chat_config.get('group_user_prompt')
                        response_content = get_response_from_bot_group(group_user_prompt, bot, histories)
                        bot_manager.add_message_to_group_history("assistant", response_content, bot=bot)
                        bot_manager.save_data_to_file()
                        st.rerun()
# 辅助函数保持不变
def show_bot_avatar(bot):
    if st.button(bot.get('avatar', '') or '🤖', key=f"__avatar_edit_bot_{bot['id']}"):
        edit_bot(bot)

def show_bot_title(bot):
   st.markdown(f"<h3 style='padding:0;'>{bot['name']}</h3> {bot['engine']} {bot.get('model', '')}", unsafe_allow_html=True)

def show_toggle_bot_enable(bot):
    def make_update_bot_enable(bot_id):
        def update_bot_enable():
            bot = next((b for b in st.session_state.bots if b['id'] == bot_id), None)
            if bot:
                bot['enable'] = not bot['enable']
                st.session_state.bot_manager.update_bot(bot)
        return update_bot_enable

    st.toggle("启用 / 禁用", value=bot['enable'], key=f"toggle_{bot['id']}", on_change=make_update_bot_enable(bot['id']))