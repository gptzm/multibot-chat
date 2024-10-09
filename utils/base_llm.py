from openai import OpenAI
from config import BASS_LLM_BASE_URL, BASS_LLM_API_KEY, BASS_LLM_MODEL

def base_llm_completion(content, system_prompt, history=[], tools=[]):
    client = OpenAI(api_key=BASS_LLM_API_KEY, base_url=BASS_LLM_BASE_URL)
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
    return completion