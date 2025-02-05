import streamlit as st
from utils.user_manager import user_manager  # 确保这行导入存在
import re
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

def register_page():
    st.title("注册")
    
    with st.form("注册表单"):
        new_user = st.text_input("用户名")
        new_password = st.text_input("密码", type='password')
        confirm_password = st.text_input("确认密码", type="password")
        
        # 生成验证码
        if 'captcha_text' not in st.session_state or 'captcha_image' not in st.session_state:
            st.session_state.captcha_text, st.session_state.captcha_image = generate_captcha()
        
        col1, col2 = st.columns(2)
        submit_button = st.form_submit_button("注 册", type='primary', use_container_width=True)

        with col1:
            # 验证码输入框
            captcha_input = st.text_input("请输入验证码")
        
        if submit_button:
            if captcha_input.upper() != st.session_state.captcha_text:
                st.error("验证码错误")
            elif not re.match(r'^[a-zA-Z0-9@\._]{1,32}$', new_user):
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
            
            # 重新生成验证码
            st.session_state.captcha_text, st.session_state.captcha_image = generate_captcha()

        with col2:
            # 显示验证码图像
            st.text('')
            st.image(st.session_state.captcha_image, use_container_width=True)
        
    
    if st.button("我已有账号", use_container_width=True):
        st.session_state.page = "login_page"
        del st.session_state.captcha_text
        del st.session_state.captcha_image
        st.rerun()