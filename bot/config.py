ENGINE_CONFIG = {
  "engines": {
    "AzureOpenAI": {
      "fields": [
        {
          "name": "model",
          "label": "模型",
          "type": "text",
          "required": True
        },
        {
          "name": "api_endpoint",
          "label": "API 端点",
          "type": "text",
          "required": True
        },
        {
          "name": "api_key",
          "label": "API 密钥",
          "type": "password",
          "required": True
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True
        }
      ]
    },
    "ChatGLM": {
      "fields": [
        {
          "name": "model",
          "label": "模型",
          "type": "text",
          "required": True
        },
        {
          "name": "api_key",
          "label": "API 密钥",
          "type": "password",
          "required": True
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True
        }
      ]
    },
    "CoZe": {
      "fields": [
        {
          "name": "bot_id",
          "label": "Bot ID",
          "type": "text",
          "required": True
        },
        {
          "name": "api_key",
          "label": "API 密钥",
          "type": "password",
          "required": True
        }
      ]
    },
    "Qwen": {
      "fields": [
        {
          "name": "model",
          "label": "模型",
          "type": "text",
          "required": True
        },
        {
          "name": "api_key",
          "label": "API 密钥",
          "type": "password",
          "required": True
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True
        }
      ]
    },
    "Ollama": {
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True
        },
        {
          "name": "api_endpoint",
          "label": "API 端点",
          "type": "text",
          "required": True
        }
      ]
    },
    "DeepSeek": {
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True
        },
        {
          "name": "api_key",
          "label": "API 密钥",
          "type": "password",
          "required": True
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True
        }
      ]
    },
    "Moonshot": {
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True
        },
        {
          "name": "api_key",
          "label": "API 密钥",
          "type": "password",
          "required": True
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True
        }
      ]
    },
    "Yi": {
      "fields": [
        {
          "name": "model",
          "label": "Model",
          "type": "text",
          "required": True
        },
        {
          "name": "api_key",
          "label": "API 密钥",
          "type": "password",
          "required": True
        },
        {
          "name": "temperature",
          "label": "温度",
          "type": "slider",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "required": True
        }
      ]
    }
  }
}
