import json
import streamlit as st
from config import LOGGER
from utils.base_llm import base_llm_completion


def plan_task_with_openai(prompt, group_history, bots, tools):
    """
    使用 OpenAI 的功能来生成任务计划。

    :param prompt: 用户输入的提示信息
    :param bots: 可用 bot 的列表，每个 bot 是一个包含名称和功能的字典
    :return: 任务计划
    """
    try:
        function_calls = []
        function_call_names = []

        for bot in bots:
            if bot.get('enable', True):
                function_call = {
                    "type": "function",
                    "function": {
                        "name": f"call_bot_{bot['id']}",
                        "description": f"如果话题非常符合该角色的特长，请让该角色参与讨论！这个角色的定位是【{bot['name']}】\n作用是：\n{bot.get('system_prompt','')[0:100]}",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string", "description": "这里是需要该角色执行的指示"},
                            },
                            "additionalProperties": False
                        }
                    }
                }
                function_calls.append(function_call)
                function_call_names.append(f" - {bot['id']}：{bot['name']}")
    except Exception as e:
        return f"[ERROR] 获取角色信息时发生错误: {str(e)}"
        
    group_history = fix_messages(group_history)
    
    # function_call_names_string = "、".join(function_call_names)
    try:
        completion = base_llm_completion(
            '仔细理解user最新对话的关注点，结合上下文仔细斟酌最适合讨论这个话题的1~3个角色，并按顺序调用',
            system_prompt=f'你是一个角色调用路由，能够拆分逐层深入的思考路径，并深入理解每个角色的定位和分工，规划不同的角色如何按顺序参与讨论，你需要分步骤调用这些角色，但不要直接回复用户',
            history=group_history,
            tools=function_calls,
        )
        LOGGER.info(f'\n\ncompletion=\n{completion}\n\n')
    except Exception as e:
        return f"[ERROR] 调用本地模型时发生错误: {str(e)}"

    try:
        results = []
        if completion.choices[0].message.content:
            results.append(completion.choices[0].message.content)
        if completion.choices[0].message.tool_calls:
            for tool_call in completion.choices[0].message.tool_calls[:3]:
                LOGGER.info(f'\n\ntool_call=\n{tool_call}  {tool_call.type == "function"} and {tool_call.function.name.startswith("call_bot_")}\n\n')
                if tool_call.type == "function":
                    arguments = json.loads(tool_call.function.arguments)
                    if tool_call.function.name.startswith("call_bot_"):
                        bot_id = tool_call.function.name.replace("call_bot_", "")
                        results.append({"type": "call_bot", "id": bot_id, "prompt": arguments.get("prompt")})
                    # elif tool_call.function.name.startswith("call_tool_"):
                    #     tool_id = tool_call.function.name.replace("call_tool_", "")
                    #     results.append({"type": "call_tool", "id": tool_id})
                    elif st.session_state.bot_manager.get_bot_by_name(tool_call.function.name):
                        bot = st.session_state.bot_manager.get_bot_by_name(tool_call.function.name)
                        results.append({"type": "call_bot", "id": bot['id']})
        if results:
            return results
        else:
            return "好尴尬呀，没人想聊这个话题"
    except Exception as e:
        return f"[ERROR] 生成任务计划出错: {str(e)}"

def fix_messages(messages):
    messages = [{"role": msg.get("role"), "content": str(msg.get("content",""))} for msg in messages if msg['content']]
    if messages and messages[-1]['role'] != 'user':
        messages[-1]['role'] = 'user'
    return messages

def run(parameter, content, group_prompt, group_history):
    return plan_task_with_openai(content, group_history, st.session_state.bot_manager.bots, st.session_state.tool_manager.tools)