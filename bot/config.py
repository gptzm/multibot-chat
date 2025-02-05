ENGINE_CONFIG = {
  "engines": {
    "OpenAI": {
      "name": "OpenAI(需翻墙)",
      "fields": [
        {
          "name": "model",
          "label": "模型",
          "type": "text",
          "required": True,
          "default": "gpt-4o",
        },
        {
          "name": "base_url",
          "label": "Base URL",
          "type": "text",
          "required": True,
          "default": "https://**请更新成你的base_url信息**/v1",
          "is_secret": True,
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "AzureOpenAI": {
      "name": "微软OpenAI",
      "fields": [
        {
          "name": "model",
          "label": "模型",
          "type": "text",
          "required": True,
          "default": "gpt-4o",
        },
        {
          "name": "api_endpoint",
          "label": "API Endpoint",
          "type": "text",
          "required": True,
          "default": "https://**请更新成你的endpoint信息**.openai.azure.com/",
          "is_secret": True,
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "ChatGLM": {
      "name": "智谱清言",
      "fields": [
        {
          "name": "model",
          "label": "模型",
          "type": "text",
          "required": True,
          "default": "glm-4-air",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "CoZe": {
      "name": "Coze智能体",
      "fields": [
        {
          "name": "bot_id",
          "label": "Bot ID",
          "type": "text",
          "required": True,
          "default": "**从coze的链接上获取你的botid**",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        }
      ]
    },
    "Qwen": {
      "name": "通义千问",
      "fields": [
        {
          "name": "model",
          "label": "模型",
          "type": "text",
          "required": True,
          "default": "qwen-turbo",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "Ollama": {
      "name": "Ollama",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "qwen2.5",
        },
        {
          "name": "base_url",
          "label": "Base URL",
          "type": "text",
          "required": True,
          "default": "http://127.0.0.1:11434/v1",
          "is_secret": True,
        }
      ]
    },
    "XingHuo": {
      "name": "讯飞星火",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "generalv3.5",
        },
        {
          "name": "api_password",
          "label": "API Password",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "Qianfan": {
      "name": "百度文心",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "ernie-4.0-turbo-8k",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.01,
          "max": 1.00,
          "step": 0.01,
          "required": True,
        }
      ]
    },
    "DeepSeek": {
      "name": "DeepSeek",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "deepseek-chat",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "MiniMax": {
      "name": "MiniMax",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "MiniMax-Text-01",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 1.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "Moonshot": {
      "name": "KIMI",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "moonshot-v1-8k",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "Stepfun": {
      "name": "阶跃星辰",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "step-1-8k",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 1.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "Yi": {
      "name": "零一万物",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "yi-medium",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "Groq": {
      "name": "Groq(需翻墙)",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "mixtral-8x7b-32768",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "302AI": {
      "name": "302.AI",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "claude-3-5-sonnet-latest",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
    "siliconflow": {
      "name": "硅基流动",
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True,
          "default": "deepseek-ai/DeepSeek-R1",
        },
        {
          "name": "api_key",
          "label": "API Key",
          "type": "password",
          "required": True,
          "is_secret": True,
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True,
        }
      ]
    },
  }
}
