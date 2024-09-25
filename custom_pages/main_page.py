# *-* coding:utf-8 *-*
import streamlit as st
import logging
import random
from utils.chat_utils import get_response_from_bot, delete_bot, display_chat
from bot.bot_session_manager import BotSessionManager
import utils.user_manager as user_manager
from bot.config import ENGINE_CONFIG
from config import DEFAULT_SECRET_KEY

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

EMOJI_OPTIONS = ["🤖", "🦾", "🧠", "💡", "🔮", "🎭", "🦄", "🐼", "🦊", "🐶", "🐱", "🦁", "🐯", "🐻", "🐨", "😄", "🤡", "👻", "😈", "🤠", "🙊", "😽", "👽", "🧑‍🎓", "🧑‍💼", "🧑‍🎨", "🧑‍✈️", "🥷"]

try:
    SECRET_KEY = st.secrets['SECRET_KEY']
    LOGGER.info("成功从 .secrets 文件读取 SECRET_KEY")
except Exception as e:
    SECRET_KEY = DEFAULT_SECRET_KEY  # 默认值

ENGINE_OPTIONS = list(ENGINE_CONFIG.get('engines', {}).keys())

bot_manager = None

@st.dialog('编辑Bot', width='large')
def edit_bot(bot):
    idx = bot_manager.get_bot_idx(bot)
    
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

            bot['enable'] = st.toggle('启用', value=bot.get('enable', False))
            
            st.markdown(f"**engine:** {bot.get('engine', '')}")
            
            # 根据配置动态生成输入字段
            for field in ENGINE_CONFIG['engines'][bot['engine']]['fields']:
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
            col1, col_empty, col2, col3 = st.columns(4, gap="small")

            with col1:
                if st.form_submit_button("删除", use_container_width=True):
                    bot_manager.delete_bot(bot['name'])
                    st.rerun()

            with col2:
                if st.form_submit_button("创建副本", use_container_width=True):
                    bot_manager.create_bot_copy(bot)
                    st.rerun()

            with col3:
                if st.form_submit_button("保存", use_container_width=True, type="primary"):
                    bot_manager.update_bot(bot, idx)
                    st.rerun()

@st.dialog('新增机器人', width='large')
def add_new_bot():
    engine = st.selectbox("选择引擎", options=ENGINE_OPTIONS, key="__add_new_bot_engine", index=ENGINE_OPTIONS.index(st.session_state.get('engine', ENGINE_OPTIONS[0])))
    st.session_state.engine = engine
    LOGGER.info(f"Selected engine: {engine}")
    new_bot = {
        'id': str(random.randint(10000000000000000,99999999999999999)),
        'name': f"Bot {len(st.session_state.bots) + 1}",
        'engine': engine,
        'avatar': None,  # 默认头像
    }

    if 'avatar' in st.session_state:
        new_bot['avatar'] = st.session_state.avatar

    default_bot = bot_manager.get_default_bot(engine)

    with st.form("新增Bot"):
        col1, col2 = st.columns(2, gap="small")
        with col1:
            LOGGER.info(f"Selected avatar: {new_bot['avatar']}")
            new_bot['avatar'] = st.selectbox("头像", options=EMOJI_OPTIONS, key="__new_bot_avatar", index=EMOJI_OPTIONS.index(new_bot['avatar']) or 0)
            if new_bot['avatar'] in EMOJI_OPTIONS:
                st.session_state.avatar = new_bot['avatar']

            new_bot['name'] = st.text_input("机器人名称", value=new_bot['name'], help="请输入机器人的名称", key="__new_bot_name")
            
            new_bot['enable'] = st.toggle('启用', value=default_bot.get('enable', True))
            
            st.markdown(f"**engine:** {engine}")

            LOGGER.info(f"Selected name: {new_bot['name']}")

            # 根据配置动态生成输入字段
            for field in ENGINE_CONFIG['engines'][engine]['fields']:
                if field['type'] == 'text':
                    new_bot[field['name']] = st.text_input(field['label'], key=f"__new_bot_{field['name']}", value=default_bot.get(field['name'], None))
                elif field['type'] == 'password':
                    new_bot[field['name']] = st.text_input(field['label'], type="password", key=f"__new_bot_{field['name']}", value=default_bot.get(field['name'], None))
                elif field['type'] == 'slider':
                    new_bot[field['name']] = st.slider(field['label'], min_value=field['min'], max_value=field['max'], step=field['step'], key=f"__new_bot_{field['name']}", value=default_bot.get(field['name'], None))
            
        with col2:
            new_bot['system_prompt'] = st.text_area("系统提示", value=default_bot.get('system_prompt', ''), height=400, help="请输入系统提示信息", key="__new_bot_system_prompt")
            LOGGER.info(f"Selected system_prompt: {new_bot['system_prompt']}")

        col_left, col_center, col_right = st.columns(3, gap="small")
        with col_center:
            LOGGER.info(f"Selected enable: {new_bot['enable']}")

            if st.form_submit_button("保存", use_container_width=True):
                # 验证必填字段
                missing_fields = [field['label'] for field in ENGINE_CONFIG['engines'][engine]['fields'] 
                                    if field['required'] and not new_bot.get(field['name'])]
                if missing_fields:
                    st.error(f"以下字段为必填项: {', '.join(missing_fields)}")
                else:
                    bot_manager.update_default_bot(new_bot)
                    bot_manager.add_bot(new_bot)
                    st.rerun()

def main_page():
    # st.toast(f'main_{random.random()}')
    global bot_manager
    LOGGER.info(f"Entering main_page. Username: {st.session_state.get('username')}")
    if 'username' not in st.session_state or not st.session_state['username']:
        st.error("用户名未设置，请重新登录")
        st.session_state.logged_in = False
        st.rerun()
    
    bot_manager = BotSessionManager(st.session_state.username)
    
    # 使用 bot_manager 的属性更新 st.session_state
    st.session_state.bots = bot_manager.bots
    st.session_state.history_versions = bot_manager.history_versions
    st.session_state.current_history_version = bot_manager.current_history_version

    if 'chat_config' not in st.session_state:
        st.session_state.chat_config = {
            'history_length': 10,
        }

    with st.sidebar:
        with st.expander("我的"):
            st.text(f"当前用户：{st.session_state.username}")
            if st.button("修改密码", use_container_width=True):
                st.session_state.page = "change_password_page"
                st.rerun()
            if st.button("退出登录", use_container_width=True):
                user_manager.destroy_token(st.session_state.token)
                st.session_state.page = "login_page"
                st.session_state.logged_in = False
                st.rerun()

        with st.expander("聊天设置"):
            st.session_state.chat_config['history_length'] = st.slider("携带对话条数", min_value=1, max_value=20, value=st.session_state.chat_config.get('history_length', 10))

        with st.expander("历史话题", expanded=True):
            history_options = [f"{v['name']}" for i, v in enumerate(st.session_state.history_versions)]
            
            # 确保 current_history_version 在有效范围内
            if st.session_state.current_history_version >= len(history_options):
                st.session_state.current_history_version = len(history_options) - 1 if history_options else 0
            
            def on_history_change():
                new_version_index = history_options.index(st.session_state.history_version_selector)
                participating_bots = bot_manager.get_participating_bots(new_version_index)
                
                # 更新 bot_manager 的 current_history_version
                bot_manager.current_history_version = new_version_index
                
                # 保存新的版本索引到 session_state
                st.session_state.current_history_version = new_version_index
                
                # 更新机器人状态：启用所有参与聊天的机器人
                for bot in st.session_state.bots:
                    bot['enable'] = bot['id'] in participating_bots
                
                # 保存更新后的数据
                bot_manager.save_data_to_file()
                
                # 更新 session_state 中的机器人数据
                st.session_state.bots = bot_manager.bots

                # 设置一个标志来触发重新渲染
                st.session_state.history_changed = True

            st.selectbox(
                "切换话题",
                options=history_options,
                index=st.session_state.current_history_version,
                key="history_version_selector",
                on_change=on_history_change
            )

            if st.button("清理所有历史话题", use_container_width=True):
                bot_manager.clear_all_histories()
                st.success("所有历史话题已清理")
                st.rerun()

        if len(st.session_state.bots) > 0:
            with st.expander("Bot管理", expanded=True):
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

    input_box = st.container()
    st.markdown("---")
    output_box = st.container()

    with input_box:
        enabled_bots = [bot for bot in st.session_state.bots if bot['enable']]
        if not any(bot_manager.get_current_history(bot['name']) for bot in enabled_bots):
            st.markdown("# 开始对话吧\n发送消息后，可以同时和已启用的多个Bot聊天。")
        
        col1, col2 = st.columns([9, 1], gap="small")
        
        with col1:
            prompt = st.chat_input("输入消息...")

        with col2:
            if st.button("新话题", use_container_width=True):
                if bot_manager.create_new_history_version():
                    st.success("已创建新话题")
                    st.rerun()

    with output_box:
        enabled_bots = [bot for bot in st.session_state.bots if bot['enable']]
        if not enabled_bots:
            if prompt:
                st.warning("请至少启用一个机器人，才能进行对话")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("## 快速开始")
                if st.button("创建第一个Bot并开始聊天", type="primary"):
                    st.session_state.avatar = random.choice(EMOJI_OPTIONS)
                    add_new_bot()

            with col2:
                st.markdown("## 主要功能")
                st.markdown("""
                - 创建多个AI聊天机器人，对比不同的system prompt
                - 同时与多个Bot进行对话，直观比较不同模型的回答
                - 保存和回顾历史对话，分析不同智能体的表现
                - 自定义Bot的个性和能力，测试各种参数设置
                """)

            return

        num_bots = len(enabled_bots)
        num_cols = min(2, num_bots)
        
        cols = st.columns(num_cols)

        for i, bot in enumerate(enabled_bots):
            if prompt:
                response_content = get_response_from_bot(prompt, bot, st.session_state.chat_config)
                bot_manager.add_message_to_history(bot['name'], {"role": "user", "content": prompt})
                bot_manager.add_message_to_history(bot['name'], {"role": "assistant", "content": response_content})
                bot_manager.update_history_names(specific_index=bot_manager.current_history_version)
                    
            col = cols[i % num_cols]

            with col:
                button_box, title_box = st.columns([1, 10], gap="small")
                with title_box:
                    st.markdown(f"<h3 style='padding:0;'>{bot['name']}</h3> {bot['engine']} {bot.get('model', '')}", unsafe_allow_html=True)
                with button_box:
                    if st.button(bot.get('avatar', '') or '🤖', key=f"__edit_enabled_bot_{i}"):
                        edit_bot(bot)
                
                # 显示当前对话
                current_history = bot_manager.get_current_history(bot['name'])
                if current_history:
                    display_chat(bot, current_history)
                
                # 显示历史对话
                all_histories = bot_manager.get_all_histories(bot['name'])
                non_empty_histories = [h for h in all_histories[:-1] if h['history']]  # 跳过当前对话，只保留非空历史
                if non_empty_histories:  # 如果有非空的历史版本
                    num_topics = len(non_empty_histories)
                    with st.expander(f"其他{num_topics}个话题"):
                        for i, history in enumerate(reversed(non_empty_histories)):
                            st.markdown(f"**{history['name']}** - {history['timestamp']}")
                            display_chat(bot, history['history'])
                            if i < len(non_empty_histories) - 1:
                                st.markdown("---")

    # LOGGER.info(st.session_state.bots)
    bot_manager.save_data_to_file()
    bot_manager.save_data_to_file()