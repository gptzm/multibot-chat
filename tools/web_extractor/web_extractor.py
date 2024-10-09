import re
import requests
from readability import Document
import requests
from config import LOGGER

def get_html_text(html_content, options):
    try:
        # 创建Document对象
        doc = Document(html_content, **options)

        # 获取文章标题
        title = doc.title()

        # 获取文章正文
        extracted_text = doc.summary()

        return f"# {title}\n\n{extracted_text}"
    except Exception as e:
        return f"[ERROR] 提取URL时发生错误: {str(e)}"

def run(parameter, content, group_prompt, group_history):
    try:
        max_url_count = parameter.get('max_url_count',1)
        
        options = {
            'min_text_length': parameter.get('min_text_length',100),  # 最小文本长度
            'retry_length': parameter.get('retry_length',250),     # 重试时的最小长度
        }
    except Exception as e:
        return f"读取配置发生错误: {str(e)}"
    
    try:
        # 从content中提取所有URL
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content)
        result_contents = []
        
    except Exception as e:
        return f"[ERROR] 提取URL时发生错误: {str(e)}"

    if not urls:
        return "[ERROR] 未找到有效的URL"
    
    for idx, url in enumerate(urls):
        if idx > max_url_count:
            break

        try:
            response = requests.get(url)
            content = get_html_text(response.content, options)
            if content:
                result_contents.append(content)
        
        except requests.RequestException as e:
            result_contents.append(f"[ERROR] 解析{url}网页内容时发生错误: {str(e)}")
        
    return result_contents or "没有找到可用的内容"