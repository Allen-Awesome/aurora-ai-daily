import openai
import httpx
from typing import Dict, List
from logging_config import get_logger
import re
from datetime import datetime
import os

logger = get_logger(__name__)

class ContentSummarizer:
    """内容总结器"""
    
    def __init__(self, api_key: str, base_url: str = None):
        # 支持自定义base_url，默认使用DeepSeek
        if base_url is None:
            base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        
        # 提供自建 httpx.Client 以绕过某些 Runner 上 httpx 与 openai 的 proxies 兼容性问题
        http_client = httpx.Client(timeout=30.0)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client,
        )
        
    def generate_summary(self, article: Dict) -> Dict:
        """生成文章摘要"""
        try:
            # 构建提示词
            content = f"""
            标题: {article['title']}
            来源: {article['source']}
            内容: {article.get('summary', '')[:1000]}
            
            请为这篇AI行业文章生成一个200-300字的中文摘要，包含以下要素：
            1. 核心观点或发现
            2. 关键技术或公司
            3. 对行业的影响
            4. 重要数据或结论
            
            摘要要求：
            - 语言简洁明了
            - 突出重点信息
            - 适合快速阅读
            """
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的AI行业分析师，擅长总结技术文章和新闻。"},
                    {"role": "user", "content": content}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content
            
            # 提取关键信息
            keywords = self.extract_keywords(article['title'] + ' ' + summary)
            importance_score = self.calculate_importance(article, summary)
            
            return {
                'original_title': article['title'],
                'summary': summary,
                'keywords': keywords,
                'importance_score': importance_score,
                'source': article['source'],
                'url': article['url'],
                'summary_time': datetime.now().isoformat(),
                'image': article.get('image', '')
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            return {
                'original_title': article['title'],
                'summary': article.get('summary', '')[:300],
                'keywords': [],
                'importance_score': 0.5,
                'source': article['source'],
                'url': article['url'],
                'summary_time': datetime.now().isoformat(),
                'image': article.get('image', '')
            }
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # AI相关关键词列表
        ai_keywords = [
            'GPT', 'ChatGPT', 'OpenAI', 'Google', 'Microsoft', 'Meta', 'Apple',
            '人工智能', '机器学习', '深度学习', '神经网络', '大模型', 'LLM',
            'Transformer', 'BERT', '自然语言处理', 'NLP', '计算机视觉',
            '自动驾驶', '机器人', '算法', '数据科学', 'AI芯片', 'GPU',
            '投资', '融资', '并购', '上市', 'IPO', '估值', '独角兽'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in ai_keywords:
            if keyword.lower() in text_lower or keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords[:5]  # 最多返回5个关键词
    
    def calculate_importance(self, article: Dict, summary: str) -> float:
        """计算重要性评分 (0-1)"""
        score = 0.5  # 基础分数
        
        # 根据来源权威性调整
        source_weights = {
            'techcrunch_ai': 0.9,
            'mit_tech_review': 0.95,
            'arxiv_ai': 0.8,
            'venturebeat_ai': 0.8,
            'towards_data_science': 0.7,
            'github_trending': 0.6
        }
        
        source_weight = source_weights.get(article['source'], 0.5)
        score = score * 0.5 + source_weight * 0.5
        
        # 根据关键词重要性调整
        high_impact_keywords = ['GPT', 'OpenAI', 'Google', 'Microsoft', '突破', '发布', '融资']
        keyword_count = sum(1 for keyword in high_impact_keywords 
                          if keyword.lower() in summary.lower())
        
        if keyword_count > 0:
            score += min(keyword_count * 0.1, 0.3)
        
        return min(score, 1.0)
    
    def batch_summarize(self, articles: List[Dict]) -> List[Dict]:
        """批量生成摘要"""
        summaries = []
        
        for article in articles:
            summary = self.generate_summary(article)
            summaries.append(summary)
            
        # 按重要性排序
        summaries.sort(key=lambda x: x['importance_score'], reverse=True)
        
        return summaries
