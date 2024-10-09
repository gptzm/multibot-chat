import openai
# *-* coding:utf-8 *-*
import requests
import json
import logging
import random
from openai import OpenAI
import streamlit as st
from utils.chat_utils import get_response_from_bot, get_response_from_bot_group, display_chat, display_group_chat

from utils.user_manager import user_manager  # 确保这行导入存在
from config import LOGGER
from bot.bot_session_manager import BotSessionManager

BASS_LLM_API_KEY = 'ollama'
BASS_LLM_MODEL = 'qwen2.5:3b'
BASS_LLM_BASE_URL = 'http://127.0.0.1:11434/v1'

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def plan_task_with_openai(prompt, bots):
    # """
    # 使用 OpenAI 的功能来生成任务计划。

    # :param prompt: 用户输入的提示信息
    # :param bots: 可用 bot 的列表，每个 bot 是一个包含名称和功能的字典
    # :return: 任务计划
    # """
    # try:
        LOGGER.info('------------------------')
        # 构建工具列表
        tools = []
        for bot in bots:
            tool = {
                "type": "function",
                "function": {
                    "name": f"call_bot_id_{bot['id']}",
                    "description": f"这个工具的名字是【{bot['name']}】\n作用是：\n{bot.get('system_prompt','')[0:100]}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": f"结合上下文，指明该步骤里需要解决的问题"
                            }
                        },
                        "required": ["prompt"],
                        "additionalProperties": False
                    }
                }
            }
            tools.append(tool)

        LOGGER.info(tools)

        # 使用 OpenAI 的 API 生成任务计划
        client = OpenAI(api_key=BASS_LLM_API_KEY, base_url=BASS_LLM_BASE_URL)
        completion = client.chat.completions.create(
            model=BASS_LLM_MODEL,
            messages=[{"role": "system", "content": "你是一个工具调用规划器，总是能结合上下文分步骤调用tools中合适的下一个工具",},{"role": "user", "content": f"请你调用工具：计算1234*555，再将等式其翻译成英文",}],
            temperature=0.5,
            tools=tools,
        )

        # 解析响应
        LOGGER.info(completion)
        finish_reason = completion.choices[0].finish_reason
        message = completion.choices[0].message.content
        tool_calls = completion.choices[0].message.tool_calls
        if tool_calls:
            tool_calls_info = [{"name": tool_call.function.name, "arguments": tool_call.function.arguments} for tool_call in tool_calls]
        else:
            tool_calls_info = []
            st.session_state.bot_manager = BotSessionManager('zm')
        print(f"Generated task plan: finish_reason={finish_reason}, message={message}, tool_calls={tool_calls_info}")

        # 提取bot的id和arguments中的prompt
        for tool_call_info in tool_calls_info:
            bot_id = tool_call_info["name"].split("_")[-1]
            arguments = json.loads(tool_call_info["arguments"])
            prompt = arguments.get("prompt", "")
            # 调用send_message_group
            response = get_response_from_bot_group(prompt, {"id": bot_id}, [])
            print(f"Response from bot {bot_id}: {response}")

        return [message]
    # except Exception as e:
    #     return f"生成任务计划出错: {str(e)}"
# 示例使用
bots = [
    {
      "id": "e08a7aa3-d936-4817-96b7-c64be05ddca3",
      "name": "翻译",
      "engine": "AzureOpenAI",
      "avatar": "\ud83e\udd20",
      "enable": False,
      "model": "gpt-4o",
      "api_endpoint": "https://eastus-zmopenai.openai.azure.com/",
      "api_key": "b66794b580f949bba5b06901747750a7",
      "temperature": 1.0,
      "system_prompt": "你能够翻译任何语言"
    },
    {
      "id": "a476c7cb-8299-4a5d-b56e-79b717da924a",
      "name": "计算器",
      "engine": "ChatGLM",
      "avatar": "\ud83e\uddd1\u200d\ud83d\udcbc",
      "enable": False,
      "model": "glm-4-air",
      "api_key": "8a3d80ad0aaa33926239dbc2a770f0c6.mbach4qquWD1GUNj",
      "temperature": 1.0,
      "system_prompt": "你能够计算任意两个数字之间的运算结果"
    },
]

prompt = "分析一下这段文字的情感，并提取其中的实体。"
task_plan = plan_task_with_openai(prompt, bots)
print(task_plan)