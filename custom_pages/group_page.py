import streamlit as st
from utils.user_manager import user_manager
from custom_pages.utils.sidebar import render_sidebar
from config import LOGGER
from custom_pages.utils.welcome_message import display_welcome_message
from custom_pages.utils.bot_display import display_group_chat_area, display_inactive_bots
from utils.chat_utils import get_response_from_bot_group

def group_page():
    LOGGER.info(f"进入 group_page。用户名: {st.session_state.get('username')}")
    if not user_manager.verify_token(st.session_state.get('token')):
        st.error("用户未登录或会话已过期,请重新登录")
        st.session_state.page = "login_page"
        st.rerun()
    
    bot_manager = st.session_state.bot_manager

    render_sidebar()

    input_box = st.container()
    st.markdown("---")
    output_box = st.container()

    is_current_history_empty = bot_manager.is_current_group_history_empty()
    enabled_bots = [bot for bot in st.session_state.bots if bot['enable']]

    with input_box:
        if is_current_history_empty:
            st.markdown("# 开始群聊\n发送消息后,所有启用的 Bot 将参与讨论。")
        
        col1, col2 = st.columns([9, 1], gap="small")
        
        with col1:
            prompt = st.chat_input("按Enter键发送消息，按Shift+Enter键可换行")

        with col2:
            if st.button("新话题", use_container_width=True):
                if bot_manager.create_new_group_history_version():
                    st.success("已创建新群聊话题")
                    st.rerun()
                else:
                    st.warning("无法创建新群聊话题，当前话题可能为空")

    with output_box:
        group_history = bot_manager.get_current_group_history()

        if prompt:
            bot_manager.add_message_to_group_history("user", prompt)
            group_history = bot_manager.get_current_group_history()  # 更新群聊历史
            for bot in enabled_bots:
                group_user_prompt = bot_manager.get_chat_config().get('group_user_prompt')
                response_content = get_response_from_bot_group(group_user_prompt, bot, bot_manager.get_chat_config(), group_history)
                bot_manager.add_message_to_group_history("assistant", response_content, bot=bot)
                group_history = bot_manager.get_current_group_history()  # 再次更新群聊历史
            
        if not group_history:
            display_welcome_message(bot_manager)
            if st.session_state.bots:
                st.markdown("---")
                display_inactive_bots(bot_manager, st.session_state.bots)
        else:
            display_group_chat_area(bot_manager, enabled_bots, group_history)

    # 保存当前的 session_state 到文件
    bot_manager.save_data_to_file()
    user_manager.save_session_state_to_file()

    # 如果有新消息，重新加载页面
    if prompt:
        st.rerun()
