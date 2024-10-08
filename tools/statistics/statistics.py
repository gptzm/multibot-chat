import re

def run(parameter, content, group_prompt, group_history):
    try:
        text_statistics_mode = parameter.get('text_statistics_mode', True)
        numberline_statistics_mode = parameter.get('numberline_statistics_mode', True)
    except Exception as e:
        return f"读取配置发生错误: {str(e)}"
    
    lines = content.splitlines()
    line_count = len(lines)
    word_count = sum(len(line.split()) for line in lines)
    
    statistics_results = []

    if text_statistics_mode:
        statistics_results.append(f"# 文本统计")
        statistics_results.append(f"行数: {line_count}")
        statistics_results.append(f"单词数: {word_count}")
        statistics_results.append(f"字数: {len(content)}")
    
    if numberline_statistics_mode:
        numbers = []
        for line in lines:
            stripped_line = line.replace(" ", "").replace("\n", "")
            if re.match(r'^-?\d+(\.\d+)?$', stripped_line):
                numbers.append(float(stripped_line))
        
        if numbers:
            numbers_sorted = sorted(numbers)
            total = round(sum(numbers), 10)
            average = round(total / len(numbers), 10)
            median = round(numbers_sorted[len(numbers) // 2] if len(numbers) % 2 != 0 else (numbers_sorted[len(numbers) // 2 - 1] + numbers_sorted[len(numbers) // 2]) / 2, 10)
            variance = round(sum((x - average) ** 2 for x in numbers) / len(numbers), 10)
            std_dev = round(sum((x - average) ** 2 for x in numbers) / len(numbers) ** 0.5, 10)
            min_value = round(min(numbers), 10)
            max_value = round(max(numbers), 10)
            statistics_results.append(f"# 数字行统计")
            statistics_results.append(f"行数：{len(numbers)}行")
            statistics_results.append(f"求和: {total}")
            statistics_results.append(f"均值: {average}")
            statistics_results.append(f"中位数: {median}")
            statistics_results.append(f"方差: {variance}")
            statistics_results.append(f"标准差: {std_dev}")
            statistics_results.append(f"最小值: {min_value}")
            statistics_results.append(f"最大值: {max_value}")
            statistics_results.append(f"# 数字行汇总")
            md_table = "| 序号 | 数值 |\n|------|------|\n"
            for i, num in enumerate(numbers, 1):
                md_table += f"| {i} | {num} |\n"
            statistics_results.append(md_table)
    
    result = '\n\n'.join(statistics_results)

    return result or '没有识别到有效的统计内容'