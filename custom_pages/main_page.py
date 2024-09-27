# *-* coding:utf-8 *-*
import streamlit as st
import logging
from bot.bot_session_manager import BotSessionManager
from utils.user_manager import user_manager
from config import LOGGER
from custom_pages.utils.sidebar import render_sidebar
from custom_pages.utils.welcome_message import display_welcome_message
from custom_pages.utils.bot_display import display_active_bots, display_inactive_bots

bot_manager = st.session_state.bot_manager

def main_page():
    LOGGER.info(f"Entering main_page. Username: {st.session_state.get('username')}")
    
    render_sidebar()

    input_box = st.container()
    st.markdown("---")
    output_box = st.container()

    is_current_history_empty = bot_manager.is_current_history_empty()
    enabled_bots = [bot for bot in st.session_state.bots if bot['enable']]

    with input_box:
        if not any(bot_manager.get_current_history_by_bot(bot) for bot in enabled_bots):
            st.markdown("# 开始对话吧\n发送消息后，可以同时和已启用的多个Bot聊天。")
        
        col1, col2 = st.columns([9, 1], gap="small")
        
        with col1:
            prompt = st.chat_input("按Enter键发送消息，按Shift+Enter键可换行")

        with col2:
            if st.button("新话题", use_container_width=True):
                if bot_manager.create_new_history_version():
                    st.success("已创建新话题")
                    st.rerun()

    with output_box:
        if bot_manager.is_current_history_empty() and not prompt:
            if prompt:
                st.warning("请至少启用一个机器人，才能进行对话")
            display_welcome_message(bot_manager)
            if is_current_history_empty and not prompt:
                st.markdown("---")

        show_bots = st.session_state.bots if is_current_history_empty and not prompt else enabled_bots

        if show_bots:
            if is_current_history_empty and not prompt:
                display_inactive_bots(bot_manager, show_bots)
            else:
                display_active_bots(bot_manager, prompt, show_bots)

    # 每次加载完页面后将当前的session_state保存到对应的文件中
    bot_manager.save_data_to_file()

    # 每次加载完页面后将当前的session_state保存到对应的文件中
    user_manager.save_session_state_to_file()
