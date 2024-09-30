import re

def run(parameter, content, group_prompt, group_history):
    try:
        text_statistics_mode = parameter.get('text_statistics_mode', True)
        numberline_statistics_mode = parameter.get('numberline_statistics_mode', True)
        calculate_mode = parameter.get('calculate_mode', True)
    except Exception as e:
        return f"读取配置发生错误: {str(e)}"
    
    lines = content.splitlines()
    line_count = len(lines)
    word_count = sum(len(line.split()) for line in lines)
    
    calculation_results = []

    # 处理多行内容
    numbers = []
    for line in lines:
        stripped_line = line.replace(" ", "").replace("\n", "")
        if re.match(r'^-?\d+(\.\d+)?$', stripped_line):
            numbers.append(float(stripped_line))
    if text_statistics_mode:
        calculation_results.append(f"行数: {line_count}，单词数: {word_count}，字数: {len(content)}")
    
    if numberline_statistics_mode and numbers:
        total = round(sum(numbers), 10)
        average = round(total / len(numbers), 10)
        median = round(sorted(numbers)[len(numbers) // 2] if len(numbers) % 2 != 0 else (sorted(numbers)[len(numbers) // 2 - 1] + sorted(numbers)[len(numbers) // 2]) / 2, 10)
        calculation_results.append(f"发现{len(numbers)}行数字")
        calculation_results.append(f"求和: {total}，均值: {average}，中位数: {median}")
    
    if calculate_mode:
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
                calculation_results.append(f'计算【{expression}】的结果为 {round(eval(expression),10)}')
            except Exception as e:
                calculation_results.append(f"计算 {expression} 时发生错误: {str(e)}")
    
    result = '\n\n'.join(calculation_results)

    return result or '没有识别到有效内容'