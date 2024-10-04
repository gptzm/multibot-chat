import streamlit as st
from utils.user_manager import user_manager  # 确保这行导入存在

def change_password_page():
    st.title("修改密码")
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("请先登录以修改密码")
        st.session_state.page = "login_page"
        st.rerun()
    else:
        with st.form("修改密码表单"):
            old_password = st.text_input("旧密码", type='password')
            new_password = st.text_input("新密码", type='password')
            confirm_password = st.text_input("确认新密码", type="password")
            submit_button = st.form_submit_button("修改密码", type='primary', use_container_width=True)
        
        if submit_button:
            if new_password != confirm_password:
                st.error("新密码和确认密码不匹配")
            elif user_manager.change_password(st.session_state.username, old_password, new_password):
                st.success("密码修改成功")
            else:
                st.warning("旧密码错误")
        
        if st.button("返回", use_container_width=True):
            st.session_state.page = "main_page"
            st.rerun()
