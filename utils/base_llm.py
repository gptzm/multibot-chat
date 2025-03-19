from openai import OpenAI
from config import BASS_LLM_BASE_URL, BASS_LLM_API_KEY, BASS_LLM_MODEL
import streamlit as st  # 新增streamlit导入

def base_llm_completion(content, system_prompt, history=[], tools=[]):
    client = OpenAI(api_key=BASS_LLM_API_KEY, base_url=BASS_LLM_BASE_URL)
    try:
        completion = client.chat.completions.create(
            model=BASS_LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *history[-4:],
                {"role": "user", "content": content},
            ],
            temperature=0.5,
            tools=tools,
        )
        
        # 新增有效性检查
        if not completion.choices or not completion.choices[0]:
            raise ValueError("API响应数据格式异常，未包含有效结果")
            
    except Exception as e:
        st.toast(
            "API调用失败，请确认已正确设置以下环境变量：\n"
            "export MULTIBOT_BASE_LLM_MODEL=\"模型名称\"\n"
            "export MULTIBOT_BASE_LLM_BASE_URL=\"模型url\"\n"
            "export MULTIBOT_BASE_LLM_API_KEY=\"模型密钥\"",
            icon="⚠️"
        )
        raise e
    return completion