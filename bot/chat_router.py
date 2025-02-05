# *-* coding:utf-8 *-*
import requests
import json
import logging
import random
from openai import OpenAI
import streamlit as st

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# 定义一个通用的聊天路由组件
class ChatRouter:
    def __init__(self, bot_config, chat_config):
        """
        初始化路由器。
        
        参数:
            bot_config (dict): 机器人配置，包括engine, base_url, api_key, model等。
        """
        self.engine = bot_config.get('engine', '')
        self.api_endpoint = bot_config.get('api_endpoint', '')
        self.base_url = bot_config.get('base_url', '')
        self.api_key = bot_config.get('api_key', '')
        self.api_password = bot_config.get('api_password', '')
        self.model = bot_config.get('model')
        if chat_config.get('force_system_prompt'):
            self.system_prompt = chat_config['force_system_prompt']
        else:
            self.system_prompt = bot_config.get('system_prompt', '')
        self.group_user_prompt = chat_config.get('group_user_prompt', '')
        self.history_length = chat_config.get('history_length', 10)
        self.group_history_length = chat_config.get('group_history_length', 20)
        self.bot_id = bot_config.get('id', '')
        self.user_id = bot_config.get('user_id', random.randint(1000000000,9999999999))
        self.temperature = bot_config.get('temperature', 1.0)
    
    def send_message(self, prompt, history, input_type='text', image=None, tools=None):
        """
        发送消息到指定的大模型。
        
        参数:
            prompt (str): 用户输入的文本。
            history (list): 历史对话记录。
            input_type (str): 输入类型，'text' 或 'image'。
            image (bytes): 如果input_type是'image'，则提供图片的字节数据。
            tools (list): 可选的工具列表，用于增强模型能力。
        
        返回:
            response_content (str 或生成器): 模型的回复内容或流式数据。
        """
        
        history = history[-self.history_length:]

        LOGGER.info(f"Sending message with system_prompt: {self.system_prompt}")

        return str(self._call_engine_chat(prompt, history, input_type=input_type, image=image, tools=tools))

    def send_message_group(self, prompt, group_history, input_type='text', image=None, tools=None):
        """
        发送消息到指定的大模型。
        
        参数:
            prompt (str): 用户输入的文本。
            group_history (list): 群聊历史记录。
            input_type (str): 输入类型，'text' 或 'image'。
            image (bytes): 如果input_type是'image'，则提供图片的字节数据。
            tools (list): 可选的工具列表，用于增强模型能力。
        
        返回:
            response_content (str 或生成器): 模型的回复内容或流式数据。
        """

        group_history = group_history[-self.group_history_length:]

        LOGGER.info(f"Sending message with system_prompt: {self.system_prompt}")
        
        return str(self._call_engine_chat(prompt, group_history, input_type=input_type, image=image, tools=tools))
        
    def _call_engine_chat(self, prompt, history, input_type='text', image=None, tools=None):
        if self.engine == 'AzureOpenAI':
            return self._azure_openai_chat(prompt, history)
        elif self.engine == 'ChatGLM':
            return self._chatglm_chat(prompt, history)
        elif self.engine == 'CoZe':
            return self._coze_chat(prompt, history)
        elif self.engine == 'Qwen':
            return self._qwen_chat(prompt, history)
        elif self.engine == 'Ollama':
            return self._ollama_chat(prompt, history)
        elif self.engine == 'Qianfan':
            return self._qianfan_chat(prompt, history)
        elif self.engine == 'XingHuo':
            return self._xinghuo_chat(prompt, history)
        elif self.engine == 'DeepSeek':
            return self._deepseek_chat(prompt, history)
        elif self.engine == 'Moonshot':
            return self._moonshot_chat(prompt, history)
        elif self.engine == 'Yi':
            return self._yi_chat(prompt, history)
        elif self.engine == 'Groq':
            return self._groq_chat(prompt, history)
        elif self.engine == 'MiniMax':
            return self._minimax_chat(prompt, history)
        elif self.engine == 'Stepfun':
            return self._stepfun_chat(prompt, history)
        elif self.engine == '302AI':
            return self._302ai_chat(prompt, history)
        elif self.engine == 'siliconflow':
            return self._siliconflow_chat(prompt, history)
        elif self.engine == 'OpenAI':
            return self._openai_chat(prompt, history)
        else:
            return "不支持的引擎。"

    def _azure_openai_chat(self, prompt, history):
        
        try:
            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)
            # st.stop()
            if not messages:
                return
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key,
            }
            data = {
                "messages": messages,
                "temperature": self.temperature,
            }
            
            url = f"{self.api_endpoint}/openai/deployments/{self.model}/chat/completions?api-version=2024-02-01"
            response = requests.post(url, headers=headers, data=json.dumps(data))

            LOGGER.warning(f'  response.json():\n{response.json()}')
            response_json = response.json()
            if response_json.get('choices') and len(response_json['choices']) > 0:
                LOGGER.info(f'  response:\n\n\n {response_json}')
                if 'content' in response_json['choices'][0]['message']:
                    return str(response_json['choices'][0]['message']['content'])
                else:
                    return [str(response_json['choices'][0]),str(response_json['error']['message'])]
            else:
                return f"[AzureOpenAI] Error: {response_json['error']['message']}"
        except Exception as e:
            return "[AzureOpenAI] API 调用出错: " + str(e)
    
    def _chatglm_chat(self, prompt, history):
        try:
            from zhipuai import ZhipuAI
            client = ZhipuAI(api_key=self.api_key)
        
            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return
            
            payload = {
                "model": self.model or "glm-4",
                "messages": messages,
                "temperature": self.temperature,
            }
            
            json_response = client.chat.completions.create(**payload)
            
            LOGGER.info(f'  response:\n\n\n {json_response}')
            
            if json_response.choices and len(json_response.choices) > 0:
                return json_response.choices[0].message.content
            else:
                return f'[ChatGLM] Error:{json_response["error"]["message"]}'

        except Exception as e:
            LOGGER.error(f"[ChatGLM] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _coze_chat(self, prompt, history):
        # 实现与CoZe的交互
        
        try:
            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return
            
            payload = {
                "bot_id": str(self.bot_id),
                "user": str(self.user_id),
                "query": prompt,
                "chat_history": messages,
                "stream": False,
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }

            LOGGER.info(f'  headers:\n\n\n {headers}')
            LOGGER.info(f'  payload:\n\n\n {payload}')
            
            response = requests.post('https://api.coze.cn/open_api/v2/chat', json=payload, headers=headers)
            json_response = response.json()
            if json_response['msg'] != 'success':
                return f"[COZE] Error: {json_response['msg']}"
            answer = None
            for message in json_response['messages']:
                if message.get('type') == 'answer':
                    answer = message.get('content')
                    break
            if not answer:
                return "[COZE] Error: empty answer"
            return answer
        except Exception as e:
            return "错误: " + str(e)
    
    def _qwen_chat(self, prompt, history):
        # 实现与Qwen的交互
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[Qwen] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"[Qwen] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
    
    def _qianfan_chat(self, prompt, history):
        # 实现与Qianfan的交互
        try:
            url = "https://qianfan.baidubce.com/v2/chat/completions"

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')
            
            payload = json.dumps({
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
            }
            
            response = requests.request("POST", url, headers=headers, data=payload)
            LOGGER.info(f'  response:\n\n\n {response.text}')

            completion = json.loads(response.text)
            
            if 'choices' in completion and len(completion['choices']) > 0:
                return completion['choices'][0]['message']['content']
            else:
                return f"[QianFan] Error:{completion['error']['message']}"
        except Exception as e:
            LOGGER.error(f"[QianFan] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
    
    def _xinghuo_chat(self, prompt, history):
        # 实现与星火的交互
        try:
            client = OpenAI(
                api_key=self.api_password, # 控制台获取的APIPassword
                base_url="https://spark-api-open.xf-yun.com/v1",
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[Xinghuo] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"[Xinghuo] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _deepseek_chat(self, prompt, history):
        # 实现与DeepSeek的交互
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[DeepSeek] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"[DeepSeek] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _moonshot_chat(self, prompt, history):
        # 实现与Moonshot的交互
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.moonshot.cn/v1",
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[Moonshot] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"[Moonshot] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _yi_chat(self, prompt, history):
        # 实现与Yi的交互
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.lingyiwanwu.com/v1",
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[Yi] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"[Yi] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _groq_chat(self, prompt, history):
        # 实现与Groq的交互
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1",
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[Yi] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"Yi API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _minimax_chat(self, prompt, history):
        # 实现与MiniMax的交互
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.minimax.chat/v1",
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[MiniMax] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"MiniMax API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _stepfun_chat(self, prompt, history):
        # 实现与Stepfun的交互
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.stepfun.com/v1",
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[Stepfun] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"Stepfun API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _ollama_chat(self, prompt, history):
        # 实现与Ollama的交互
        try:
            
            LOGGER.info([self.api_key, self.base_url])
            client = OpenAI(
                api_key= self.api_key,
                base_url= self.base_url,
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[Ollama] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"[Ollama] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _302ai_chat(self, prompt, history):
        # 实现与302AI的交互
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.302.ai/v1",
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[302AI] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"[302AI] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _siliconflow_chat(self, prompt, history):
        # 实现与siliconflow的交互
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.siliconflow.cn/v1",
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)
            
            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[siliconflow] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"[siliconflow] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _openai_chat(self, prompt, history):
        # 实现与OpenAI的交互
        try:
            client = OpenAI(
                api_key= self.api_key,
                base_url= self.base_url,
            )

            messages = self._join_messages(prompt, history)
            messages = self._fix_messages(messages)

            if not messages:
                return

            LOGGER.info(f'  messages:\n\n\n {messages}')

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )

            LOGGER.info(f'  response:\n\n\n {completion.model_dump_json()}')

            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                return f"[OpenAI] Error:{completion.error.message}"
        except Exception as e:
            LOGGER.error(f"[OpenAI] API 调用出错: {str(e)}")
            return f"错误: {str(e)}"

    def add_to_history(self, user_message, bot_response):
        """
        将用户消息和机器人回复添加到历史记录。
        
        参数:
            user_message (str): 用户输入的消息。
            bot_response (str): 机器人回复的内容。
        """
        self.history.append({
            'user': user_message,
            'response': bot_response
        })

    def get_history(self):
        """
        获取历史记录。
        
        返回:
            history (list): 历史对话记录。
        """
        return self.history

    def _join_messages(self, prompt, history):
        if self.system_prompt:
            messages = [
                {"role": "system", "content": self.system_prompt},
                *history,
                {"role": "user", "content": prompt},
            ]
        else:
            messages = [
                *history,
                {"role": "user", "content": prompt},
            ]

        return messages

    def _fix_messages(self, messages):
        messages = [{"role": msg.get("role"), "content": str(msg.get("content",""))} for msg in messages if msg['content']]
        if messages and messages[-1]['role'] != 'user':
            messages[-1]['role'] = 'user'
        LOGGER.info(messages)
        return messages