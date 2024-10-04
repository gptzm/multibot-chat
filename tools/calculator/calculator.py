import re

def run(parameter, content, group_prompt, group_history):
    try:
        calculate_mode = parameter.get('calculate_mode', True)
    except Exception as e:
        return f"读取配置发生错误: {str(e)}"
    
    calculation_results = []
    
    if calculate_mode:
        # 提取算式并计算
        try:
            content = re.sub(r'(\d) +(?=\d)', r'\1', content)
            expression_pattern = r'(?:\( *)*(?:- *|not *)*\d*\.?\d+ *(?:(?:\) *)*(?:[+\-*/%*×÷]|\*\*|and|or|==) *(?:\( *)*(?:- *|not *)*\d*\.?\d+ *(?:\) *)*)+'
            expressions = re.findall(expression_pattern, content)
        except Exception as e:
            return f"解析时发生错误: {str(e)}"
    
        for expression in expressions:
            try:
                expression = expression.replace("×", " * ").replace("÷", " / ")
                result = round(eval(expression), 10)
                calculation_results.append(f"`{expression}`\n  **= {result}**")
            except Exception as e:
                calculation_results.append(f"计算 {expression} 时发生错误: {str(e)}")
    
    result = '\n\n'.join(calculation_results)

    return result or '没有识别到有效的算式'