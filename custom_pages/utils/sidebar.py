import streamlit as st
import random
from config import EMOJI_OPTIONS
from utils.user_manager import user_manager
from custom_pages.utils.dialogs import edit_bot, add_new_bot, edit_bot_config, confirm_action
import logging

LOGGER = logging.getLogger(__name__)

def render_sidebar():
    bot_manager = st.session_state.bot_manager
    chat_config = bot_manager.get_chat_config()

    with st.sidebar:
        with st.expander("我的"):
            st.text(f"当前用户：{st.session_state.username}")
            if st.button("修改密码", use_container_width=True):
                st.session_state.page = "change_password_page"
                st.rerun()
            if st.button("退出登录", use_container_width=True):
                if confirm_action("确定要退出登录吗？"):
                    user_manager.destroy_token()
                    st.session_state.page = "login_page"
                    st.session_state.logged_in = False
                    st.rerun()
            if st.button("编辑配置", use_container_width=True):
                edit_bot_config()

        with st.expander("聊天设置"):
            new_config = {}
            force_system_prompt = st.text_area("强制系统提示词", value=chat_config.get('force_system_prompt', ''), key="force_system_prompt", placeholder='强制所有Bot使用此提示词，如果留空则遵循Bot设置')
            if force_system_prompt != chat_config.get('force_system_prompt'):
                chat_config['force_system_prompt'] = force_system_prompt
                bot_manager.update_chat_config(chat_config)
                bot_manager.save_data_to_file()  # 立即保存到文件
                LOGGER.info(f"Updated and saved force_system_prompt: {force_system_prompt}")
            if st.session_state.page == "group_page":
                new_config['group_user_prompt'] = st.text_area("群聊接力提示词", value=chat_config.get('group_user_prompt',''), height=40, placeholder='提示Bot在群聊时应该如何接力，如果留空则让Bot自由发挥')
                new_config['group_history_length'] = st.slider("群聊携带对话条数", min_value=1, max_value=20, value=chat_config['group_history_length'])
            else:
                new_config['history_length'] = st.slider("携带对话条数", min_value=1, max_value=20, value=chat_config['history_length'])
            
            bot_manager.update_chat_config(new_config)

        if st.session_state.page == "group_page":
            with st.expander("群聊历史话题", expanded=True):
                group_history_options = [f"{v['name']}" for v in bot_manager.group_history_versions]
                
                current_index = min(bot_manager.current_group_history_version, len(group_history_options) - 1)
                
                new_index = st.selectbox(
                    "可以回到旧话题继续聊天",
                    options=range(len(group_history_options)),
                    format_func=lambda i: group_history_options[i],
                    index=current_index
                )

                if new_index != bot_manager.current_group_history_version:
                    bot_manager.current_group_history_version = new_index
                    bot_manager.save_data_to_file()
                    st.rerun()

                if st.button("清理所有历史话题", use_container_width=True):
                    if confirm_action("确定要清理所有群聊历史话题吗？此操作不可撤销。"):
                        bot_manager.clear_all_group_histories()
                        st.rerun()

        else:
            if st.session_state.page != "group_page":
                with st.expander("历史话题", expanded=True):
                    history_versions = bot_manager.history_versions
                    history_options = [f"{v['name']}" for v in history_versions]
                    
                    # 确保 current_history_version 在有效范围内
                    current_history_version = min(bot_manager.current_history_version, len(history_options) - 1)
                    
                    def on_history_change():
                        new_version_index = st.session_state.history_version_selector
                        participating_bots = bot_manager.get_participating_bots(new_version_index)
                        
                        # 更新 bot_manager 的 current_history_version
                        bot_manager.current_history_version = new_version_index
                        
                        # 更新机器人状态：启用所有参与聊天的机器人
                        for bot in bot_manager.bots:
                            bot['enable'] = bot['id'] in participating_bots and bot_manager.get_current_history_by_bot(bot)
                        
                        # 保存更新后的数据
                        bot_manager.save_data_to_file()

                    st.selectbox(
                        "可以回到旧话题继续聊天",
                        options=range(len(history_options)),
                        format_func=lambda i: history_options[i],
                        index=current_history_version,
                        key="history_version_selector",
                        on_change=on_history_change
                    )

                    if st.button("清理所有历史话题", use_container_width=True):
                        if confirm_action("确定要清理所有历史话题吗？此操作不可撤销。"):
                            bot_manager.clear_all_histories()
                            st.rerun()

        if len(st.session_state.bots) > 0:
            with st.expander("Bot管理"):
                if not st.session_state.bots:
                    if bot_manager.filename:
                        bot_manager.load_encrypted_bots_from_file()

                with st.container():
                    for i, bot in enumerate(st.session_state.bots):
                        bot_name_display = f"{bot.get('avatar', '') or '🤖'} **{bot['name']}**" if bot['enable'] else f"{bot.get('avatar', '🤖')} ~~{bot['name']}~~"
                        if st.button(bot_name_display, key=f"__edit_bot_{i}", use_container_width=True):
                            edit_bot(bot)
        
                if st.button("新增Bot", type="primary", use_container_width=True):
                    st.session_state.avatar = random.choice(EMOJI_OPTIONS)
                    add_new_bot()
        

        if st.session_state.page == "group_page":
            if st.button("返回对话模式",use_container_width=True):
                st.session_state.page = "main_page"
                st.rerun()
        else:
            if st.button("切换到群聊模式",use_container_width=True):
                st.session_state.page = "group_page"
                st.rerun()
