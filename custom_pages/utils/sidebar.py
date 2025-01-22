import streamlit as st
import random
from config import EMOJI_OPTIONS, SHOW_SECRET_INFO, GUEST_USERNAMES
from utils.user_manager import user_manager
from custom_pages.utils.dialogs import edit_bot, add_new_bot, edit_bot_config
import logging
import re

LOGGER = logging.getLogger(__name__)

def render_sidebar():
    bot_manager = st.session_state.bot_manager
    chat_config = bot_manager.get_chat_config()

    with st.sidebar:

        with st.expander("我的"):
            st.markdown(f"当前用户：{st.session_state.username}")
            st.warning("不要把您的密码告诉任何人，以免大模型密钥被盗用！")
            
            if st.session_state.username not in GUEST_USERNAMES:
                if SHOW_SECRET_INFO or not st.session_state.bots:
                    if st.button("导入配置", use_container_width=True):
                        edit_bot_config()
                if st.button("修改密码", use_container_width=True):
                    st.session_state.page = "change_password_page"
                    st.rerun()

            if st.button("退出登录", use_container_width=True):
                confirm_action_logout()
        
        with st.expander("聊天设置", expanded=True):

            if st.session_state.page == "group_page":
                if st.button("返回对话模式",use_container_width=True):
                    st.session_state.page = "main_page"
                    bot_manager.set_last_visited_page("main_page")
                    st.rerun()
            else:
                if st.button("切换到群聊模式",use_container_width=True, type='primary'):
                    st.session_state.page = "group_page"
                    bot_manager.set_last_visited_page("group_page")
                    st.rerun()

            new_config = {}
            force_system_prompt = st.text_area("强制系统提示词", value=chat_config.get('force_system_prompt', ''), key="force_system_prompt", placeholder='强制所有Bot使用此提示词，如果留空则遵循Bot设置')
            if force_system_prompt != chat_config.get('force_system_prompt'):
                chat_config['force_system_prompt'] = force_system_prompt
                bot_manager.update_chat_config(chat_config)
                bot_manager.save_data_to_file()  # 立即保存到文件
                LOGGER.info(f"Updated and saved force_system_prompt: {force_system_prompt}")

            if st.session_state.page == "group_page":
                new_config['group_user_prompt'] = st.text_area("群聊接力提示词", value=chat_config.get('group_user_prompt',''), height=68, placeholder='提示Bot在群聊时应该如何接力，如果留空则由Bot自由发挥')
                new_config['group_history_length'] = st.slider("群聊携带对话条数", min_value=1, max_value=20, value=chat_config['group_history_length'], help="Bot在参与群聊时可以看到多少条历史消息")
            else:
                new_config['history_length'] = st.slider("携带对话条数", min_value=1, max_value=20, value=chat_config['history_length'])
            
            bot_manager.update_chat_config(new_config)

        if st.session_state.page == "group_page":
            with st.expander("群聊历史话题", expanded=True):
                group_history_options = [f"{v['name']}" for v in bot_manager.group_history_versions]
                
                current_index = min(bot_manager.current_group_history_version_idx, len(group_history_options) - 1)
                
                new_index = st.selectbox(
                    "可以回到旧话题继续聊天",
                    options=range(len(group_history_options)),
                    format_func=lambda i: group_history_options[i],
                    index=current_index
                )

                if new_index != bot_manager.current_group_history_version_idx:
                    bot_manager.current_group_history_version_idx = new_index
                    bot_manager.save_data_to_file()
                    st.rerun()

                if st.button("清理所有历史话题", use_container_width=True):
                    confirm_action_clear_grouop_histsorys()

        else:
            if st.session_state.page == "main_page":
                with st.expander("历史话题", expanded=True):
                    history_versions = bot_manager.history_versions
                    history_options = [f"{v['name']}" for v in history_versions]
                    
                    # 确保 current_history_version_idx 在有效范围内
                    current_history_version_idx = min(bot_manager.current_history_version_idx, len(history_options) - 1)
                    
                    def on_history_change():
                        new_version_index = st.session_state.history_version_selector
                        participating_bots = bot_manager.get_participating_bots(new_version_index)
                        
                        # 更新 bot_manager 的 current_history_version_idx
                        bot_manager.current_history_version_idx = new_version_index
                        
                        # 更新机器人状态：启用所有参与聊天的机器人
                        for bot in bot_manager.bots:
                            bot['enable'] = bot['id'] in participating_bots and bot_manager.get_current_history_by_bot(bot)
                        
                        # 保存更新后的数据
                        bot_manager.save_data_to_file()

                    st.selectbox(
                        "可以回到旧话题继续聊天",
                        options=range(len(history_options)),
                        format_func=lambda i: history_options[i],
                        index=current_history_version_idx,
                        key="history_version_selector",
                        on_change=on_history_change
                    )

                    if st.button("清理所有历史话题", use_container_width=True):
                        confirm_action_clear_historys()

        with st.expander("Bot管理"):
            with st.container():
                for i, bot in enumerate(st.session_state.bots):
                    bot_name_display = f"{bot.get('avatar', '') or '🤖'} **{bot['name']}**" if bot['enable'] else f"{bot.get('avatar', '🤖')} ~~{bot['name']}~~"
                    system_prompt = bot.get('system_prompt','')
                    system_prompt_warp = re.sub(r'((?:[\u0100-\u9fff]|[^\u0000-\u00ff]{1,2}){1,20})', r'\1\n\n', system_prompt[0:100])
                    if st.button(bot_name_display, key=f"__edit_bot_{i}", help=f"{system_prompt_warp}\n\n***【点击按钮可编辑】***".strip(), use_container_width=True):
                        edit_bot(bot)
    
            if st.button("新增Bot", type="primary", use_container_width=True):
                st.session_state.avatar = random.choice(EMOJI_OPTIONS)
                add_new_bot()


@st.dialog('清空所有历史对话', width='small')
def confirm_action_clear_historys():
    bot_manager = st.session_state.bot_manager
    st.markdown('确定要清理所有历史话题吗？')
    st.warning('此操作不可撤销。', icon="⚠️")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("确认", key="confirm_button", use_container_width=True):
            bot_manager.clear_all_histories()
            st.rerun()
    with col2:
        if st.button("取消", key="cancel_button", use_container_width=True):
            st.rerun()


@st.dialog('清空所有历史群聊', width='small')
def confirm_action_clear_grouop_histsorys():
    bot_manager = st.session_state.bot_manager
    st.markdown('确定要清理所有群聊历史话题吗？')
    st.warning('此操作不可撤销。', icon="⚠️")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("确认", key="confirm_button", use_container_width=True):
            bot_manager.clear_all_group_histories()
            st.rerun()
    with col2:
        if st.button("取消", key="cancel_button", use_container_width=True):
            st.rerun()

@st.dialog('退出登录', width='small')
def confirm_action_logout():
    st.markdown('确定要退出吗？')
    col1, col2 = st.columns(2)
    with col1:
        if st.button("确认", key="confirm_button", use_container_width=True):
            # 清除会话状态
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # 重置必要的状态
            st.session_state.logged_in = False
            st.session_state.page = "login_page"
            # 销毁token
            user_manager.destroy_token()
            st.rerun()
    with col2:
        if st.button("取消", key="cancel_button", use_container_width=True):
            st.rerun()
            