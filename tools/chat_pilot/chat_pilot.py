import json
import streamlit as st
from config import LOGGER
from utils.base_llm import base_llm_completion


def plan_task_with_openai(prompt, group_prompt, group_history, bots, tools):
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
                        "description": f"这个角色是【{bot['name']}】\n角色的定位和作用是：\n{bot.get('system_prompt','')[0:100]}",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string", "description": "这里提示该角色应该在上一个角色输出的基础上做进一步行动，明确告知本步骤中的主要任务是什么，但此处不要提示任何具体的信息"},
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
        prompt = '仔细理解近几轮的对话，结合上下文揣测用户当前的意图，思考需要如何围绕用户的意图分步骤继续讨论，根据角色定位仔细挑选最最适合对应步骤的1~3个角色，并按顺序依次调用这些角色。如果有涉及多个步骤，后续每个角色不要给太具体的信息，都应该在上一个角色的基础上讨论自己的步骤。'
        if group_prompt:
            prompt = f'{prompt}\n用户对每个参与讨论的角色的要求是：{group_prompt}'
        completion = base_llm_completion(
            prompt,
            system_prompt=f'你是一个角色调用路由，能够拆分逐层深入的思考路径，并深入理解每个角色的定位和分工，规划不同的角色如何按顺序参与讨论，你需要分步骤调用这些角色，可以给角色一些大方向的提示，但注意你不要直接提供过于具体的信息或者直接回复用户。',
            history=group_history[-10:],
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
    return plan_task_with_openai(content, group_prompt, group_history, st.session_state.bot_manager.bots, st.session_state.tool_manager.tools)