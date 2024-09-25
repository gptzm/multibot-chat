# *-* coding:utf-8 *-*
import requests
import json
import logging
import random
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# 定义一个通用的聊天路由组件
class ChatRouter:
    def __init__(self, bot_config, chat_config):
        """
        初始化路由器。
        
        参数:
            bot_config (dict): 机器人配置，包括engine, api_endpoint, api_key, model等。
        """
        self.engine = bot_config.get('engine')
        self.api_endpoint = bot_config.get('api_endpoint')
        self.api_key = bot_config.get('api_key')
        self.model = bot_config.get('model')
        self.system_prompt = bot_config.get('system_prompt', '')
        self.history = bot_config.get('history', [])
        self.bot_id = bot_config.get('bot_id', '')
        self.user_id = bot_config.get('user_id', random.randint(100000,999999))
        self.history_length = chat_config.get('history_length', 10)
        self.temperature = bot_config.get('temperature', 1.0)
    
    def send_message(self, prompt, input_type='text', image=None, tools=None):
        """
        发送消息到指定的大模型。
        
        参数:
            prompt (str): 用户输入的文本。
            input_type (str): 输入类型，'text' 或 'image'。
            image (bytes): 如果input_type是'image'，则提供图片的字节数据。
            tools (list): 可选的工具列表，用于增强模型能力。
        
        返回:
            response_content (str 或生成器): 模型的回复内容或流式数据。
        """
        if self.engine == 'AzureOpenAI':
            return self._azure_openai_chat(prompt)
        elif self.engine == 'ChatGLM':
            return self._chatglm_chat(prompt)
        elif self.engine == 'CoZe':
            return self._coze_chat(prompt)
        elif self.engine == 'Qwen':
            return self._qwen_chat(prompt)
        elif self.engine == 'Ollama':
            return self._ollama_chat(prompt)
        elif self.engine == 'DeepSeek':
            return self._deepseek_chat(prompt)
        elif self.engine == 'Moonshot':
            return self._moonshot_chat(prompt)
        elif self.engine == 'Yi':
            return self._yi_chat(prompt)
        else:
            return "不支持的引擎。"

    def _azure_openai_chat(self, prompt,):
        try:
            LOGGER.info("正在执行_azure_openai_chat")
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key,
            }
            data = {
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.temperature,
            }

            url = f"{self.api_endpoint}/openai/deployments/{self.model}/chat/completions?api-version=2024-02-01"
            response = requests.post(url, headers=headers, data=json.dumps(data))

            LOGGER.info('  response.json():\n', response.json())
            response_json = response.json()
            if response_json.get('choices') and len(response_json['choices']) > 0:
                return str(response_json['choices'][0]['message']['content'])
            else:
                return f"[Azure] Error: {response_json['error']['message']}"
        except Exception as e:
            return "AzureOpenAI API 调用出错: " + str(e)
    
    def _chatglm_chat(self, prompt):
        try:
            from zhipuai import ZhipuAI
            LOGGER.info("正在执行_chatglm_chat")
            client = ZhipuAI(api_key=self.api_key)
            
            payload = {
                "model": self.model or "glm-4",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.temperature,
            }
            
            json_response = client.chat.completions.create(**payload)
            
            LOGGER.info(f'  response:\n\n\n {json_response}')
            
            if json_response.choices and len(json_response.choices) > 0:
                return json_response.choices[0].message.content
            else:
                return f'[ChatGLM] Error:{json_response["error"]["message"]}'

        except Exception as e:
            LOGGER.error(f"ChatGLM API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _coze_chat(self, prompt):
        # 实现与CoZe的交互
        
        try:
            payload = {
                "bot_id": str(self.bot_id),
                "user": str(self.user_id),
                "query": prompt,
                "chat_history": self.history[-self.history_length:],
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
                return None, f"[COZE] Error: {json_response['msg']}"
            answer = None
            for message in json_response['messages']:
                if message.get('type') == 'answer':
                    answer = message.get('content')
                    break
            if not answer:
                return None, "[COZE] Error: empty answer"
            return answer
        except Exception as e:
            return "错误: " + str(e)
    
    def _qwen_chat(self, prompt):
        # 实现与Qwen的交互
        try:
            client = OpenAI(
                api_key=self.api_key,  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            if self.system_prompt:
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ]
            else:
                messages = [
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ]

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
            LOGGER.error(f"Qwen API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
    
    def _deepseek_chat(self, prompt):
        # 实现与Qwen的交互
        try:
            client = OpenAI(
                api_key=self.api_key,  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
                base_url="https://api.deepseek.com",
            )

            if self.system_prompt:
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ]
            else:
                messages = [
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ]

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
            LOGGER.error(f"DeepSeek API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _moonshot_chat(self, prompt):
        # 实现与Qwen的交互
        try:
            client = OpenAI(
                api_key=self.api_key,  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
                base_url="https://api.moonshot.cn/v1",
            )

            if self.system_prompt:
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ]
            else:
                messages = [
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ]

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
            LOGGER.error(f"Moonshot API 调用出错: {str(e)}")
            return f"错误: {str(e)}"
        
    def _yi_chat(self, prompt):
        # 实现与Qwen的交互
        try:
            client = OpenAI(
                api_key=self.api_key,  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
                base_url="https://api.lingyiwanwu.com/v1",
            )

            if self.system_prompt:
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ]
            else:
                messages = [
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ]

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
        
    def _ollama_chat(self, prompt):
        # 实现与Ollama的交互
        try:
            client = OpenAI(
                api_key= 'ollama',  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
                base_url= self.api_endpoint,
            )

            if self.system_prompt:
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ]
            else:
                messages = [
                    *self.history[-self.history_length:],
                    {"role": "user", "content": prompt},
                ]

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
            LOGGER.error(f"Ollama API 调用出错: {str(e)}")
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

    def clear_history(self):
        """
        清空历史记录。
        """
        self.history = []
        