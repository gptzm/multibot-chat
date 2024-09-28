import re
import streamlit as st

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
    
    if numbers:
        total = sum(numbers)
        average = total / len(numbers)
        median = sorted(numbers)[len(numbers) // 2] if len(numbers) % 2 != 0 else (sorted(numbers)[len(numbers) // 2 - 1] + sorted(numbers)[len(numbers) // 2]) / 2
        calculation_results.append(f"求和: {total}，平均值: {average}，中位数: {median}")

    # 提取算式并计算
    expression_pattern = r'(?:[-+]?\d*\.?\d+ *(?:(?:[+\-*/%*()]|\*\*) *[-\+]?\d*\.?\d+)+| *(?:and|or|==|not) *)+'
    expressions = re.findall(expression_pattern, content)
    for expression in expressions:
        try:
            calculation_results.append(f'计算 {expression} 结果为 {eval(expression)}')
        except Exception as e:
            calculation_results.append(f"计算 {expression} 时发生错误: {str(e)}")
    result = '\n'.join(calculation_results)
        
    return result