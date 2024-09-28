# *-* coding:utf-8 *-*
import streamlit as st
import logging
from utils.user_manager import user_manager
from config import LOGGER
from custom_pages.utils.sidebar import render_sidebar
from custom_pages.utils.welcome_message import display_welcome_message
from custom_pages.utils.bot_display import display_active_bots, display_inactive_bots
from config import PRIVATE_CHAT_EMOJI

def main_page():
    bot_manager = st.session_state.bot_manager
    bot_manager.load_data_from_file()  # 重新加载配置
    
    LOGGER.info(f"Entering main_page. Username: {st.session_state.get('username')}")
    
    render_sidebar()

    input_box = st.container()
    st.markdown("---")
    output_box = st.container()

    enabled_bots = [bot for bot in st.session_state.bots if bot['enable']]

    with input_box:
        if not any(bot_manager.get_current_history_by_bot(bot) for bot in enabled_bots):
            st.markdown(f"# {PRIVATE_CHAT_EMOJI}开始对话吧\n发送消息后，可以同时和已启用的多个Bot聊天。")
        
        col1, col2 = st.columns([9, 1], gap="small")
        
        with col1:
            prompt = st.chat_input("按Enter发送消息，按Shift+Enter换行")
            if prompt and not enabled_bots:
                st.warning("请至少启用一个机器人，才能进行对话")

        with col2:
            if st.button("新话题", use_container_width=True):
                if bot_manager.create_new_history_version():
                    st.rerun()
                else:
                    st.toast("无法创建新话题，当前话题可能为空")

    with output_box:

        if enabled_bots:
            display_active_bots(bot_manager=bot_manager, prompt=prompt, show_bots=enabled_bots)
            
        if bot_manager.is_current_history_empty():
            if st.session_state.bots:
                display_inactive_bots(bot_manager=bot_manager, show_bots=st.session_state.bots)
                st.markdown("---")
            display_welcome_message(bot_manager)
        
    
    # 保存当前的 session_state 到文件
    bot_manager.save_data_to_file()
    user_manager.save_session_state_to_file()

    if prompt and not bot_manager.is_current_history_empty():
        st.rerun()
