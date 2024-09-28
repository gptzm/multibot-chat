import re

def remove_markdown(text):
    # 移除标题
    text = re.sub(r'^#+\s*', '', text)
    # 移除粗体和斜体
    text = re.sub(r'\*+', '', text)
    # 移除链接
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # 保留代码块里的代码内容，但去掉首行的```python/js 和尾部的```
    text = re.sub(r'```(?:.*)\n([\s\S]*?)\n```', r'\1', text)
    # 移除行内代码
    text = re.sub(r'`[^`\n]+`', '', text)
    # 移除列表标记
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    # 移除数字列表标记前后的多余空格
    text = re.sub(r'^\s*(\d+\.)\s*', r'\1 ', text, flags=re.MULTILINE)
    # 移除引用
    text = re.sub(r'^\s*>\s+', '', text, flags=re.MULTILINE)
    # 移除水平线
    text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # 移除多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def run(parameter, content, group_prompt, group_history):
    return remove_markdown(content)