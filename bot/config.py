ENGINE_CONFIG = {
  "engines": {
    "OpenAI": {
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
          "default": "https://**请更新成你的base_url信息**/v1/chat/completions",
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
        }
      ]
    },
    "XingHuo": {
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
    "DeepSeek": {
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
    "Moonshot": {
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
    "Yi": {
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
    }
  }
}
