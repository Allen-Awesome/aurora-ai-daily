#!/usr/bin/env python3
"""测试修复后的内容格式化效果"""

import os
import sys
sys.path.append('src')

from summarizer import ContentSummarizer
from scheduler import NewsScheduler
import re

def test_new_format():
    """测试新的摘要格式"""
    
    # 模拟一篇测试文章
    test_article = {
        'title': 'OpenAI发布GPT-5，性能大幅提升',
        'source': 'techcrunch_ai', 
        'summary': 'OpenAI正式发布了GPT-5模型，在多个基准测试中表现优异，推理能力相比GPT-4提升了40%。该模型集成了更强的多模态能力，支持图像、音频和文本的统一处理。业界专家认为这将推动AI应用进入新阶段。',
        'url': 'https://example.com/test',
        'image': ''
    }
    
    print("🧪 测试新的摘要格式...")
    print("=" * 50)
    
    # 检查环境变量
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ 未设置 DEEPSEEK_API_KEY，使用模拟摘要")
        # 模拟符合新格式的摘要
        mock_summary = """**核心观点**：OpenAI发布GPT-5，推理能力较GPT-4提升40%，集成更强多模态处理能力。

**关键技术**：GPT-5采用了改进的Transformer架构，支持图像、音频、文本统一处理，OpenAI在模型训练和优化方面取得重大突破。

**行业影响**：此次发布将推动AI应用进入新发展阶段，可能引发新一轮技术竞赛，其他科技巨头将面临更大压力。

**重要结论**：GPT-5的性能提升标志着大模型技术迈向新里程碑，多模态能力的整合为AI商业化应用提供了更广阔前景。"""
        
        mock_result = {
            'original_title': test_article['title'],
            'summary': mock_summary,
            'keywords': ['GPT', 'OpenAI'],
            'importance_score': 0.95,
            'source': test_article['source'],
            'url': test_article['url'],
            'image': test_article['image']
        }
    else:
        print("✅ 使用真实API测试...")
        summarizer = ContentSummarizer(api_key)
        mock_result = summarizer.generate_summary(test_article)
    
    print("\n📄 生成的摘要:")
    print("-" * 30)
    print(mock_result['summary'])
    
    print("\n🎨 微信排版优化后:")
    print("-" * 30)
    
    # 测试微信排版
    scheduler = NewsScheduler()
    # 模拟preprocess_for_wechat函数
    def preprocess_for_wechat(text: str) -> str:
        """专为微信优化的排版预处理"""
        if not text:
            return ""
        s = text
        
        # 定义标准的标签词
        labels = [
            "核心观点", "关键技术", "行业影响", "重要结论",
            "核心发现", "重要数据", "技术对比"
        ]
        
        # 处理标签词格式化
        for label in labels:
            pattern = r"(?<!^)(?<!\*\*)\s*(" + re.escape(label) + r")([：:])"
            replacement = r"\n\n\n**\1**\2"
            s = re.sub(pattern, replacement, s)
        
        # 处理已经加粗的标签词，确保前后有适当换行
        s = re.sub(r'\*\*([^*]+)\*\*:', r'\n\n**\1**:\n', s)
        
        # 清理多余换行
        s = re.sub(r'\n{4,}', '\n\n\n', s)
        
        return s.strip()
    
    processed = preprocess_for_wechat(mock_result['summary'])
    print(processed)
    
    print("\n✅ 测试完成！")
    
    # 检查格式是否正确
    required_labels = ["核心观点", "关键技术", "行业影响", "重要结论"]
    found_labels = []
    for label in required_labels:
        if f"**{label}**" in processed:
            found_labels.append(label)
    
    print(f"\n📊 格式检查:")
    print(f"应包含标签: {required_labels}")
    print(f"实际包含: {found_labels}")
    print(f"格式正确率: {len(found_labels)}/{len(required_labels)} ({len(found_labels)/len(required_labels)*100:.1f}%)")

if __name__ == "__main__":
    test_new_format()
