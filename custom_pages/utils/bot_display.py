import streamlit as st
from utils.chat_utils import get_response_from_bot, get_response_from_bot_group, display_chat, display_group_chat
from custom_pages.utils.dialogs import edit_bot, add_new_bot
from datetime import datetime, date
import random
from config import EMOJI_OPTIONS


def show_bot_avatar(bot):
    if st.button(bot.get('avatar', '') or '🤖', key=f"__edit_enabled_bot_{bot['id']}"):
        edit_bot(bot)

def show_bot_title(bot):
   st.markdown(f"<h3 style='padding:0;'>{bot['name']}</h3> {bot['engine']} {bot.get('model', '')}", unsafe_allow_html=True)

def show_toggle_bot_enable(bot):
    def make_update_bot_enable(bot_id):
        def update_bot_enable():
            bot = next((b for b in st.session_state.bots if b['id'] == bot_id), None)
            if bot:
                bot['enable'] = not bot['enable']
                bot_manager.update_bot(bot)
        return update_bot_enable

    bot_manager = st.session_state.bot_manager
    st.toggle("启用 / 禁用", value=bot['enable'], key=f"toggle_{bot['id']}", on_change=make_update_bot_enable(bot['id']))

def show_button_group_chat(bot):
    bot_manager = st.session_state.bot_manager
    if st.button(f"{bot.get('avatar', '🤖')} {bot['name']}  {bot['engine']} {bot['model']}", key=f"group_bot_{bot['id']}", use_container_width=True):
        bot['group_history'] = bot_manager.get_current_group_history()
        group_user_prompt = bot_manager.get_chat_config().get('group_user_prompt')
        response_content = get_response_from_bot_group(group_user_prompt, bot, bot_manager.get_chat_config())
        bot_manager.add_message_to_group_history("assistant", response_content, bot=bot)
        bot_manager.save_data_to_file()
        st.rerun()

def display_active_bots(bot_manager, prompt, enabled_bots):
    num_bots = len(enabled_bots)
    num_cols = min(2, num_bots)
    cols = st.columns(num_cols)

    for i, bot in enumerate(enabled_bots):
        col = cols[i % num_cols]
        with col:
            button_box, title_box = st.columns([1, 10], gap="small")
            
            # 获取当前bot的历史记录
            current_history = bot_manager.get_current_history_by_bot(bot)
            
            if prompt and bot['enable']:
                chat_config = bot_manager.get_chat_config()
                response_content = get_response_from_bot(prompt, bot, chat_config)
                bot_manager.add_message_to_history(bot['id'], {"role": "user", "content": prompt})
                bot_manager.add_message_to_history(bot['id'], {"role": "assistant", "content": response_content})
                bot_manager.fix_history_names(bot_manager.current_history_version)
                
                # 更新当前历史记录
                current_history = bot_manager.get_current_history_by_bot(bot)

            # 显示当前对话
            if current_history:
                display_chat(bot, current_history)

            with button_box:
                show_bot_avatar(bot)
            with title_box:
                show_bot_title(bot)

def display_inactive_bots(bot_manager, show_bots):
    show_bots = show_bots + [{'id': 'new_bot', 'avatar': '⚡', 'name': '新增一个Bot', 'engine': '支持10种引擎'}]

    num_bots = len(show_bots)
    
    if st.session_state.page == 'main_page':
        num_cols = min(2, num_bots)
        title_box_width = 9
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
                    if st.button("创建新的Bot", key=f"create_new_bot_{bot['id']}"):
                        st.session_state.avatar = random.choice(EMOJI_OPTIONS)
                        add_new_bot()
                else:
                    show_toggle_bot_enable(bot)
                    if st.session_state.page == 'main_page':
                        # 显示历史对话
                        all_histories = bot_manager.get_all_histories(bot)
                        non_empty_histories = [h for h in all_histories[:-1] if h['history']]  # 跳过当前对话，只保留非空历史

                        if non_empty_histories:  # 如果有非空的历史版本
                            num_topics = len(non_empty_histories)
                            with st.expander(f"查看 {num_topics} 个历史话题"):
                                for i, history in enumerate(reversed(non_empty_histories)):
                                    try:
                                        timestamp = datetime.fromisoformat(history['timestamp'])
                                    except ValueError:
                                        # 如果fromisoformat失败，尝试使用strptime
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

def display_group_chat_area(bot_manager, enabled_bots, group_history):
    col1, col2 = st.columns([1,1], gap="small")
    with col1:
        # 显示群聊历史
        if group_history:
            participating_bots = bot_manager.get_participating_bots_in_current_group_history()
            display_group_chat(participating_bots, group_history)
    
    with col2:
        if group_history:
            st.text('点击下方按钮，可让指定Bot发言')

            num_cols = 2
            cols = st.columns(2)
                        
            # 显示所有bot的按钮
            for i, bot in enumerate(st.session_state.bots):
                col = cols[i % num_cols]
                with col:
                    if st.button(f"{bot.get('avatar', '🤖')} {bot['name']}  {bot['engine']} {bot['model']}", key=f"group_bot_{bot['id']}", use_container_width=True):
                        group_user_prompt = bot_manager.get_chat_config().get('group_user_prompt')
                        response_content = get_response_from_bot_group(group_user_prompt, bot, bot_manager.get_chat_config(), group_history)
                        bot_manager.add_message_to_group_history("assistant", response_content, bot=bot)
                        bot_manager.save_data_to_file()
                        st.rerun()