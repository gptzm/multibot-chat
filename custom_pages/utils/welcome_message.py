import streamlit as st
import random
from config import EMOJI_OPTIONS
from custom_pages.utils.dialogs import add_new_bot

def display_welcome_message(bot_manager):
    col1, col2 = st.columns([1,1], gap="large")
    with col1:
        st.markdown("## 快速开始")
        if st.session_state.bots:
            if all(not b['enable'] for b in st.session_state.bots):
                if st.button("启用所有Bot"):
                    for bot in st.session_state.bots:
                        bot['enable'] = True
                        bot_manager.update_bot(bot)
                    st.rerun()
            else:
                st.markdown("在上方输入框内输入消息，按Enter键即可发送")
        else:
            if st.button("创建一个Bot好友并开始聊天", type="primary"):
                st.session_state.avatar = random.choice(EMOJI_OPTIONS)
                add_new_bot()
        st.markdown("您可以添加很多Bot好友，他们会以接龙的方式和您聊天")
        st.markdown("了解更多请访问[MultiBot-Chat开源项目主页](https://gitee.com/gptzm/multibot-chat)")
    with col2:
        if st.session_state.page == "group_page":
            st.markdown("## 群聊模式")
            st.markdown("""
            - 创建多个AI聊天机器人，让它们在群聊中接龙讨论
            - 观察不同Bot如何合作完成一个复杂话题
            - 模拟多方对话场景，测试Bot的协作能力
            - 比较不同模型在群聊中的表现和互动方式
            - 自定义Bot的角色和专长，探索多样化的群聊动态
            """)
            if st.button("返回对话模式", key="goto_main_page"):
                st.session_state.page = "main_page"
                st.rerun()
        else:
            st.markdown("## 对话模式")
            st.markdown("""
            - 创建多个AI聊天机器人，对比不同的system prompt
            - 同时与多个Bot进行对话，直观比较不同模型的回答
            - 保存和回顾历史对话，分析不同智能体的表现
            - 自定义Bot的个性和能力，测试各种参数设置
            """)
            if st.button("还可以试试群聊模式", key="goto_group_page"):
                st.session_state.page = "group_page"
                st.rerun()