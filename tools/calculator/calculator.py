import re
import logging
import streamlit as st

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def run(content, group_prompt, group_history):
    lines = content.splitlines()
    line_count = len(lines)
    word_count = sum(len(line.split()) for line in lines)
    
    calculation_results = []
    
    # 处理多行内容
    numbers = []
    for line in lines:
        stripped_line = line.replace(" ", "").replace("\n", "")
        if stripped_line.isdigit():
            numbers.append(int(stripped_line))

    calculation_results.append(f"行数: {line_count}，字数: {word_count}")
    st.info(numbers)
    if numbers:
        total = sum(numbers)
        average = total / len(numbers)
        median = sorted(numbers)[len(numbers) // 2] if len(numbers) % 2 != 0 else (sorted(numbers)[len(numbers) // 2 - 1] + sorted(numbers)[len(numbers) // 2]) / 2
        calculation_results.append(f"\n\n发现{len(numbers)}行数字\n\n求和: {total}，均值: {average}，中位数: {median}")
    # 提取算式并计算
    try:
        expression_pattern = r'(?:\( *)*(?:- *|not *)*\d*\.?\d+ *(?:(?:\) *)*(?:[+\-*/%*×÷]|\*\*|and|or|==) *(?:\( *)*(?:- *|not *)*\d*\.?\d+ *(?:\) *)*)+'
        expressions = re.findall(expression_pattern, content)
        if expressions:
            calculation_results.append('\n\n')
    except Exception as e:
        return f"解析时发生错误: {str(e)}"
    
    for expression in expressions:
        try:
            expression = expression.replace("×"," * ").replace("÷"," / ")
            calculation_results.append(f'计算【{expression}】的结果为 {eval(expression)}')
        except Exception as e:
            calculation_results.append(f"计算 {expression} 时发生错误: {str(e)}")
    result = '\n'.join(calculation_results)

    return result or '没有识别到有效内容'