# *-* coding:utf-8 *-*
import streamlit as st
import os
import json
import utils.logging_utils as logging_utils
import importlib
import utils.user_manager as user_manager
from config import DEFAULT_SECRET_KEY, AUTO_LOGIN, SECRET_KEY

st.set_page_config(page_title="多Bot聊天", page_icon="🤖", layout="wide")

LOGGER = logging_utils.setup_logging()

try:
    SECRET_KEY = st.secrets['SECRET_KEY']
    LOGGER.info("成功从 .secrets 文件读取 SECRET_KEY")
except (FileNotFoundError, KeyError):
    SECRET_KEY = DEFAULT_SECRET_KEY  # 默认值

def load_page(page_name):
    module = importlib.import_module(f"custom_pages.{page_name}")
    return getattr(module, page_name)

if __name__ == "__main__":
    if not os.path.exists("user_config"):
        os.makedirs("user_config")
    query_params = st.query_params
    if 'token' in query_params:
        token = query_params['token']
        st.session_state['token'] = token
        if user_manager.verify_token(token):
            st.session_state.logged_in = True
            st.session_state.username = user_manager.get_username_from_token(token)
            LOGGER.info(f"使用token登录. Username: {st.session_state.username}")
        else:
            LOGGER.warning("无效的token")
            st.session_state.logged_in = False
            st.session_state.username = ''
    else:
        st.session_state['token'] = ''
        st.session_state.logged_in = False
        st.session_state.username = ''

    if 'page' not in st.session_state:
        st.session_state['page'] = "login_page"
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    col_empty, col_center, col_empty = st.columns([1, 1, 1], gap="small")
    if st.session_state.logged_in:
        if st.session_state.page == "change_password_page":
            change_password_page = load_page("change_password_page")
            with col_center:
                change_password_page()
        else:
            main_page = load_page("main_page")
            main_page()
    else:
        if st.session_state.page == "register_page":
            register_page = load_page("register_page")
            with col_center:
                register_page()
        else:
            login_page = load_page("login_page")
            with col_center:
                login_page()

    # 每次加载完页面后将当前的session_state保存到对应的文件中
    if st.session_state.logged_in and 'bot_manager' in globals():
        user_manager.save_session_state_to_file(st.session_state.token)