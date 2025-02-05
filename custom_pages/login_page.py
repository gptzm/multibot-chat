import streamlit as st
from utils.user_manager import user_manager
from captcha.image import ImageCaptcha
import random
import string
import io
import base64

def generate_captcha():
    # 生成随机验证码
    captcha_text = ''.join(random.choices(string.digits, k=4))
    
    # 创建验证码图像
    image = ImageCaptcha(width=180, height=40, font_sizes=(30, 35, 40))
    
    # 将图像转换为base64编码
    buffered = io.BytesIO()
    image.write(captcha_text, buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return captcha_text, f"data:image/png;base64,{img_str}"

def login_page():
    st.title("登录")
    
    # 生成验证码
    if 'captcha_text' not in st.session_state or 'captcha_image' not in st.session_state:
        st.session_state.captcha_text, st.session_state.captcha_image = generate_captcha()
    
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type='password')
        
        col1, col2 = st.columns(2)
        submit_button = st.form_submit_button("登 录", type='primary', use_container_width=True)
        with col1:
            # 验证码输入框
            captcha_input = st.text_input("请输入验证码")

        if submit_button:
            if captcha_input.upper() != st.session_state.captcha_text:
                st.error("验证码错误")
            elif user_manager.login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                token = user_manager.generate_token(st.session_state.username)
                redirect_url = f"/?token={token}"
                st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}">', unsafe_allow_html=True)
            else:
                st.warning("用户名或密码错误")
            
            st.session_state.captcha_text, st.session_state.captcha_image = generate_captcha()

        with col2:
            # 显示验证码图像
            st.text('')
            st.image(st.session_state.captcha_image, use_container_width=True)

    if st.button("我要注册新账号", use_container_width=True):
        st.session_state.page = "register_page"
        del st.session_state.captcha_text
        del st.session_state.captcha_image
        st.rerun()
