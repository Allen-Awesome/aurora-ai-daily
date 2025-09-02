#!/usr/bin/env python3
"""
DeepSeek API测试脚本
用于验证API连接和基本功能
"""

import openai
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_deepseek_api():
    """测试DeepSeek API连接"""
    
    # 获取API配置
    api_key = os.getenv('DEEPSEEK_API_KEY')
    base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    
    print("🔧 DeepSeek API 测试开始...")
    print(f"📍 API地址: {base_url}")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:] if api_key else 'None'}")
    print("-" * 50)
    
    if not api_key:
        print("❌ 错误: 未找到DEEPSEEK_API_KEY环境变量")
        print("请检查.env文件是否正确配置")
        return False
    
    try:
        # 创建客户端
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 测试简单对话
        print("🤖 正在测试基本对话功能...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个AI助手，请简洁回答问题。"},
                {"role": "user", "content": "请用一句话介绍人工智能。"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        print(f"✅ API响应成功!")
        print(f"📝 回答: {answer}")
        print("-" * 50)
        
        # 测试AI新闻摘要功能
        print("📰 正在测试新闻摘要功能...")
        test_article = {
            'title': 'OpenAI发布GPT-4 Turbo新模型',
            'source': 'techcrunch_ai',
            'summary': 'OpenAI今日发布了GPT-4 Turbo模型，该模型在性能和成本效率方面都有显著提升。新模型支持更长的上下文窗口，并且API调用成本降低了50%。'
        }
        
        content = f"""
        标题: {test_article['title']}
        来源: {test_article['source']}
        内容: {test_article['summary']}
        
        请为这篇AI行业文章生成一个200字左右的中文摘要，包含以下要素：
        1. 核心观点或发现
        2. 关键技术或公司
        3. 对行业的影响
        
        摘要要求：
        - 语言简洁明了
        - 突出重点信息
        - 适合快速阅读
        """
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的AI行业分析师，擅长总结技术文章和新闻。"},
                {"role": "user", "content": content}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        print(f"✅ 摘要生成成功!")
        print(f"📄 生成的摘要:\n{summary}")
        print("-" * 50)
        
        # 显示使用统计
        print("📊 API调用统计:")
        print(f"   - 提示词tokens: {response.usage.prompt_tokens}")
        print(f"   - 完成tokens: {response.usage.completion_tokens}")
        print(f"   - 总计tokens: {response.usage.total_tokens}")
        
        print("\n🎉 DeepSeek API测试完成! 所有功能正常工作。")
        return True
        
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        print("\n🔍 可能的原因:")
        print("   1. API Key无效或已过期")
        print("   2. 网络连接问题")
        print("   3. API服务暂时不可用")
        print("   4. 账户余额不足")
        return False

if __name__ == "__main__":
    success = test_deepseek_api()
    exit(0 if success else 1)
