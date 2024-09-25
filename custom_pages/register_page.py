import streamlit as st
import utils.user_manager as user_manager

def register_page():
    st.title("注册")
    new_user = st.text_input("用户名")
    new_password = st.text_input("密码", type='password')
    confirm_password = st.text_input("确认密码", type="password")
    
    if st.button("注册", type='primary', use_container_width=True):
        if new_password != confirm_password:
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
    
    if st.button("登录", use_container_width=True):
        st.session_state.page = "login_page"
        st.rerun()
        