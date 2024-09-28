import re
import requests
from readability import Document
import requests


def get_html_text(html_content):
    options = {
        'min_text_length': 100,  # 最小文本长度
        'retry_length': 250,     # 重试时的最小长度
    }
    
    # 创建Document对象
    doc = Document(html_content, **options)

    # 获取文章标题
    title = doc.title()

    # 获取文章正文
    extracted_text = doc.summary()

    return f"# {title}\n\n{extracted_text}"

def run(content, group_prompt, group_history):
    # 从content中提取第一个URL
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, content)
    
    if not urls:
        return "[ERROR] 未找到有效的URL"
    
    result_contents = []
    
    for idx, url in enumerate(urls):
        if idx > 10:
            result_contents.append("[ERROR] 一次最多提取10个链接")
            
        if len(result_contents) > 3:
            result_contents.append("[ERROR] 一次最多解析3个页面")

        try:
            response = requests.get(url)
            content = get_html_text(response.content)
            if content:
                result_contents.append(content)
        
        except requests.RequestException as e:
            result_contents.append(f"[ERROR] 提取网页内容时发生错误: {str(e)}")
        
    return '\n\n---\n\n'.join(result_contents) or "没有找到可用的内容"