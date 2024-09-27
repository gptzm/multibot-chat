import streamlit as st
from utils.user_manager import user_manager  # 确保这行导入存在
import re

def register_page():
    st.title("注册")
    new_user = st.text_input("用户名")
    new_password = st.text_input("密码", type='password')
    confirm_password = st.text_input("确认密码", type="password")
    
    if st.button("注 册", type='primary', use_container_width=True):
        if not re.match(r'^[a-zA-Z0-9@\._]{1,32}$', new_user):
            st.error("用户名只能包含字母、数字、@、.和_，长度不能超过32个字符")
        elif new_password != confirm_password:
            st.error("密码和确认密码不匹配")
        elif user_manager.register(new_user, new_password):
            st.success("账户创建成功")
            if user_manager.login(new_user, new_password):
                st.session_state.logged_in = True
                st.session_state.username = new_user
                token = user_manager.generate_token(st.session_state.username)
                redirect_url = f"/?token={token}"
                st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}">', unsafe_allow_html=True)
            else:
                st.error("自动登录失败，请手动登录")
                st.session_state.page = "login_page"
                st.rerun()
        else:
            st.warning("用户名已存在")
    
    if st.button("登 录", use_container_width=True):
        st.session_state.page = "login_page"
        st.rerun()