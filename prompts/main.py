# 使用OpenAI兼容接口（如果Qwen3:32B支持）
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",  # 本地部署地址
    api_key="your-api-key"  # 如果不需要认证可以留空
)


def query_qwen(user_prompt: str):
    system_prompt = f"""你是一位专业的AI提示工程专家，擅长为Claude模型设计结构化、高精度的Prompt模板。
生成要求：
1. 明确设定AI的角色（如“你是一位资深市场分析师”）
2. 清晰描述任务目标与期望输出
3. 指定输出格式（如：Markdown、JSON、报告结构等）
4. 添加约束条件（字数、风格、禁止内容、数据来源要求等）
5. 如适用，提供一个示例输入输出对
6. 语言简洁、专业、无冗余，确保Claude能精准执行

请直接输出生成的Prompt模板，不要添加解释性文字。
    """

    response = client.chat.completions.create(
        model="qwen3:32b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        top_p=0.95,
        max_tokens=1000
    )
    return response.choices[0].message.content


def analyze_keyword_type(keywords):
    """根据关键词内容自动判断任务类型"""
    keywords_lower = keywords.lower()
    if any(term in keywords_lower for term in ['代码', '编程', 'python', 'golang', 'php', 'java', '开发', '算法']):
        return "编程任务"
    elif any(term in keywords_lower for term in ['分析', '研究', '报告', '数据', '趋势', '市场']):
        return "分析任务"
    elif any(term in keywords_lower for term in ['写作', '创作', '文章', '故事', '文案', '演讲']):
        return "创作任务"
    elif any(term in keywords_lower for term in ['设计', '界面', '用户体验', 'UI', '交互']):
        return "设计任务"
    else:
        return "通用任务"


def generate_user_prompt(keywords):
    task_type = analyze_keyword_type(keywords)

    result = f"""请根据以下关键词和任务类型，生成一个可以直接用于Claude模型的完整Prompt模板：
任务类型：{task_type}
关键词：{keywords}
"""

    return result


if __name__ == "__main__":
    user_keywords = input("请输入关键词（用逗号分隔）：")

    # 生成指令
    user_prompt = generate_user_prompt(user_keywords)
    # 调用Qwen模型
    generated_prompt = query_qwen(user_prompt)

    print("生成的Claude Prompt模板：")
    print("=" * 50)
    print(generated_prompt)
    print("=" * 50)
