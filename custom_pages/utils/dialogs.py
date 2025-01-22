# *-* coding:utf-8 *-*
import streamlit as st
import random
from bot.config import ENGINE_CONFIG
from config import EMOJI_OPTIONS, ENGINE_OPTIONS, LOGGER, SHOW_SECRET_INFO, GUEST_USERNAMES, DEVELOPER_USERNAME
import json

@st.dialog('编辑Bot', width='large')
def edit_bot(bot):
    bot_manager = st.session_state.bot_manager

    with st.form('edit_bot_form') as form:
        col1, col2 = st.columns(2, gap="small")
        
        with col1:
            bot['avatar'] = st.selectbox("头像", options=EMOJI_OPTIONS, index=EMOJI_OPTIONS.index(bot.get('avatar', '') or '🤖'))
            new_name = st.text_input(
                "name",
                value=bot.get('name', ''),
            )
            
            if new_name != bot['name'] and new_name in [b['name'] for b in st.session_state.bots]:
                st.error(f"机器人名称 {new_name} 已存在，请选择其他名称")
            else:
                bot['name'] = new_name

            bot['enable'] = st.toggle('启用 / 禁用', value=bot.get('enable', True))
            
            st.markdown(f"**engine:** {bot.get('engine', '')}")
            
            # 根据配置动态生成输字段
            for field in ENGINE_CONFIG['engines'][bot['engine']]['fields']:
                if st.session_state.username != DEVELOPER_USERNAME and field.get('is_secret', False):
                    if not st.session_state.username or not SHOW_SECRET_INFO or st.session_state.username in GUEST_USERNAMES:
                        continue
                
                if field['type'] == 'text':
                    bot[field['name']] = st.text_input(field['label'], value=bot.get(field['name'], ''))
                elif field['type'] == 'password':
                    bot[field['name']] = st.text_input(field['label'], type="password", value=bot.get(field['name'], ''))
                elif field['type'] == 'slider':
                    bot[field['name']] = st.slider(field['label'], min_value=field['min'], max_value=field['max'], step=field['step'], value=bot.get(field['name'], field['min']))
        
        with col2:
            bot['system_prompt'] = st.text_area(
                "System Prompt",
                value=bot.get('system_prompt', ''),
                height=400,
            )

        with st.container():
            col1, col2, col3 = st.columns(3, gap="small")

            with col1:
                if st.form_submit_button("保存", use_container_width=True, type="primary"):
                    bot_manager.update_bot(bot)
                    st.rerun()

            with col2:
                if st.form_submit_button("创建副本", use_container_width=True):
                    new_bot = bot_manager.create_bot_copy(bot)
                    st.success(f"已创建 {new_bot['name']}")
                    st.rerun()

            with col3:
                if st.form_submit_button("删除", use_container_width=True):
                    bot_manager.delete_bot(bot)
                    st.rerun()

@st.dialog('新增机器人', width='large')
def add_new_bot():
    bot_manager = st.session_state.bot_manager
    
    selected_engine_name = st.radio(
        "选择引擎",
        options=[ENGINE_CONFIG['engines'][name]['name'] for name in ENGINE_OPTIONS],
        horizontal=True,
        label_visibility="collapsed",
        key="engine_radio"
    )

    selected_engine = next(name for name in ENGINE_OPTIONS if ENGINE_CONFIG['engines'][name]['name'] == selected_engine_name)
    
    st.session_state.engine = selected_engine

    LOGGER.info(f"Selected engine: {selected_engine}")
    new_bot = {
        'id': str(random.randint(10000000000000000,99999999999999999)),
        'name': f"Bot {len(st.session_state.bots) + 1}",
        'engine': selected_engine,
        'avatar': None,  # 默认头像
    }

    if 'avatar' in st.session_state:
        new_bot['avatar'] = st.session_state.avatar

    default_bot = bot_manager.get_default_bot(selected_engine)

    with st.form(f"新增Bot_{selected_engine}"):
        col1, col2 = st.columns(2, gap="small")
        with col1:
            LOGGER.info(f"Selected avatar: {new_bot['avatar']}")
            new_bot['avatar'] = st.selectbox("头像", options=EMOJI_OPTIONS, key=f"__new_bot_avatar_{selected_engine}", index=EMOJI_OPTIONS.index(new_bot['avatar']) if new_bot['avatar'] in EMOJI_OPTIONS else 0)
            if new_bot['avatar'] in EMOJI_OPTIONS:
                st.session_state.avatar = new_bot['avatar']

            new_bot['name'] = st.text_input("机器人名称", value=new_bot['name'], help="请输入机器人的名称", key=f"__new_bot_name_{selected_engine}")
            
            new_bot['enable'] = st.toggle('启用 / 禁用', value=default_bot.get('enable', True), key=f"__new_bot_enable_{selected_engine}")
            
            st.markdown(f"**engine:** {selected_engine}")

            LOGGER.info(f"Selected name: {new_bot['name']}")

            # 根据配置动态生成输入字段
            for field in ENGINE_CONFIG['engines'][selected_engine]['fields']:
                if field['type'] == 'text':
                    new_bot[field['name']] = st.text_input(field['label'], key=f"__new_bot_{field['name']}_{selected_engine}", value=default_bot.get(field['name'], None))
                elif field['type'] == 'password':
                    new_bot[field['name']] = st.text_input(field['label'], type="password", key=f"__new_bot_{field['name']}_{selected_engine}", value=default_bot.get(field['name'], None))
                elif field['type'] == 'slider':
                    new_bot[field['name']] = st.slider(field['label'], min_value=field['min'], max_value=field['max'], step=field['step'], key=f"__new_bot_{field['name']}_{selected_engine}", value=default_bot.get(field['name'], None))
        
        with col2:
            new_bot['system_prompt'] = st.text_area("系统提示", value=default_bot.get('system_prompt', ''), height=400, help="请输入系统提示信息", key=f"__new_bot_system_prompt_{selected_engine}")
            LOGGER.info(f"Selected system_prompt: {new_bot['system_prompt']}")

        col_left, col_center, col_right = st.columns(3, gap="small")
        with col_center:
            LOGGER.info(f"Selected enable: {new_bot['enable']}")

            if st.form_submit_button("保存", use_container_width=True):
                # 验证必填字段
                missing_fields = [field['label'] for field in ENGINE_CONFIG['engines'][selected_engine]['fields'] 
                                    if field['required'] and not new_bot.get(field['name'])]
                if missing_fields:
                    st.error(f"以下字段为必填项: {', '.join(missing_fields)}")
                else:
                    bot_manager.update_default_bot(new_bot)
                    bot_manager.add_bot(new_bot)
                    st.rerun()


@st.dialog('编辑Bot配置', width='large')
def edit_bot_config():
    bot_manager = st.session_state.bot_manager
    
    config_json = json.dumps(bot_manager.get_bot_config(), indent=2)
    st.markdown("<font color='red'><strong>复制以下内容可快速粘贴导入其他账号。注意：其中含有大模型密钥，请妥善保管</strong></font>", unsafe_allow_html=True)
    new_config = st.text_area("Bot配置", value=config_json, height=300)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("保存",use_container_width=True):
            try:
                new_config_dict = json.loads(new_config)
                if bot_manager.validate_bot_config(new_config_dict):
                    bot_manager.update_bot_config(new_config_dict)
                    st.success("配置已更新")
                    st.rerun()
                else:
                    st.error("无效的配置格式")
            except json.JSONDecodeError:
                st.error("无效的JSON格式")
            st.rerun()
    with col2:
        if st.button("取消", key="cancel_button", use_container_width=True):
            st.rerun()