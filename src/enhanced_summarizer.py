#!/usr/bin/env python3
"""
增强版摘要生成器
支持多层次摘要、情感分析、趋势预测
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import Counter, defaultdict

from summarizer import ContentSummarizer


class EnhancedSummarizer(ContentSummarizer):
    """增强版摘要生成器，支持多层次摘要和智能分析"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        # 如果没有提供api_key，从环境变量获取
        if api_key is None:
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        
        super().__init__(api_key, base_url)
        self.summary_templates = {
            'executive': {
                'prompt': '请用一句话(20字内)总结这篇AI新闻的核心要点：',
                'max_length': 50
            },
            'business': {
                'prompt': '请从商业角度分析这篇AI新闻，用50字总结商业影响和投资机会：',
                'max_length': 80
            },
            'technical': {
                'prompt': '请从技术角度详细分析这篇AI新闻，用150字说明技术细节、创新点和技术影响：',
                'max_length': 200
            },
            'detailed': {
                'prompt': '请提供这篇AI新闻的完整分析，包括背景、技术细节、商业影响和未来预测：',
                'max_length': 400
            }
        }
        
        # 情感分析关键词库
        self.sentiment_keywords = {
            'positive': {
                'breakthrough': ['突破', '创新', '革命性', '颠覆性', '领先'],
                'success': ['成功', '胜利', '达成', '实现', '完成'],
                'growth': ['增长', '提升', '改善', '优化', '进步'],
                'opportunity': ['机会', '前景', '潜力', '空间', '价值']
            },
            'negative': {
                'risk': ['风险', '威胁', '危险', '挑战', '困难'],
                'decline': ['下降', '减少', '衰退', '恶化', '退步'],
                'failure': ['失败', '错误', '问题', '缺陷', '漏洞'],
                'concern': ['担忧', '质疑', '争议', '批评', '反对']
            },
            'neutral': {
                'announce': ['发布', '宣布', '推出', '展示', '介绍'],
                'report': ['报告', '显示', '表明', '指出', '说明'],
                'analyze': ['分析', '研究', '探讨', '考虑', '评估']
            }
        }
    
    def generate_multi_level_summary(self, title: str, content: str, url: str = "") -> Dict[str, Any]:
        """生成多层次摘要"""
        summaries = {}
        
        for level, template in self.summary_templates.items():
            try:
                # 构建特定层次的提示词
                prompt = self._build_level_prompt(template, title, content, level)
                
                # 生成摘要
                summary_text = self._generate_custom_summary(prompt)
                
                # 限制长度
                if len(summary_text) > template['max_length']:
                    summary_text = summary_text[:template['max_length']] + "..."
                
                summaries[level] = {
                    'content': summary_text,
                    'length': len(summary_text),
                    'keywords': self.extract_keywords(summary_text),
                    'generated_at': datetime.now().isoformat(),
                    'prompt_used': template['prompt']
                }
                
            except Exception as e:
                summaries[level] = {
                    'error': str(e),
                    'fallback_content': self._create_fallback_summary(title, content, level)
                }
        
        # 添加情感分析
        sentiment_analysis = self.analyze_sentiment(title, content)
        
        # 添加关键实体提取
        entities = self.extract_entities(title + " " + content)
        
        return {
            'summaries': summaries,
            'sentiment_analysis': sentiment_analysis,
            'entities': entities,
            'article_metadata': {
                'title': title,
                'url': url,
                'processed_at': datetime.now().isoformat(),
                'content_length': len(content)
            }
        }
    
    def _build_level_prompt(self, template: Dict, title: str, content: str, level: str) -> str:
        """构建特定层次的提示词"""
        # 限制内容长度以节省API成本
        content_preview = content[:1500] if len(content) > 1500 else content
        
        level_requirements = {
            'executive': '要求：简洁明了，突出核心价值，适合高管阅读',
            'business': '要求：重点分析商业影响、市场机会、投资价值',
            'technical': '要求：详细解释技术原理、创新点、技术优势',
            'detailed': '要求：全面分析，包括背景、现状、影响、预测'
        }
        
        prompt = f"""
        {template['prompt']}
        
        文章标题：{title}
        文章内容：{content_preview}
        
        {level_requirements.get(level, '')}
        
        请确保：
        1. 信息准确，基于文章内容
        2. 语言专业但易懂
        3. 突出AI行业相关性
        4. 字数控制在{template['max_length']}字以内
        """
        
        return prompt
    
    def _generate_custom_summary(self, prompt: str) -> str:
        """使用自定义提示词生成摘要"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的AI行业分析师，擅长总结技术文章和新闻。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"摘要生成失败: {str(e)}"
    
    def analyze_sentiment(self, title: str, content: str) -> Dict[str, Any]:
        """分析文章情感倾向"""
        text = f"{title} {content}"
        sentiment_scores = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        found_keywords = {
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        # 基于关键词的情感分析
        for sentiment, categories in self.sentiment_keywords.items():
            for category, keywords in categories.items():
                for keyword in keywords:
                    count = text.count(keyword)
                    if count > 0:
                        sentiment_scores[sentiment] += count
                        found_keywords[sentiment].extend([keyword] * count)
        
        # 计算总体情感得分
        total_keywords = sum(sentiment_scores.values())
        if total_keywords == 0:
            sentiment_ratios = {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
        else:
            sentiment_ratios = {
                sentiment: score / total_keywords 
                for sentiment, score in sentiment_scores.items()
            }
        
        # 确定主要情感倾向
        primary_sentiment = max(sentiment_ratios, key=sentiment_ratios.get)
        confidence = sentiment_ratios[primary_sentiment]
        
        # AI深度情感分析（可选）
        ai_sentiment = self._ai_sentiment_analysis(title, content[:800])
        
        return {
            'primary_sentiment': primary_sentiment,
            'confidence': confidence,
            'sentiment_ratios': sentiment_ratios,
            'keyword_analysis': found_keywords,
            'ai_analysis': ai_sentiment,
            'market_impact': self._assess_market_impact(primary_sentiment, confidence),
            'investor_sentiment': self._assess_investor_sentiment(found_keywords)
        }
    
    def _ai_sentiment_analysis(self, title: str, content: str) -> Dict[str, Any]:
        """使用AI进行深度情感分析"""
        try:
            prompt = f"""
            请分析以下AI行业新闻的市场情绪和投资者情感：
            
            标题：{title}
            内容：{content}
            
            请从以下维度分析并返回JSON格式：
            {{
                "market_sentiment": "积极/消极/中性",
                "investor_confidence": "高/中/低",
                "technology_outlook": "乐观/谨慎/悲观",
                "business_impact": "正面/负面/中性",
                "key_emotions": ["情感1", "情感2", "情感3"],
                "analysis_summary": "50字以内的分析总结"
            }}
            """
            
            response = self._generate_custom_summary(prompt)
            
            # 尝试解析JSON响应
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # 如果不是JSON格式，返回文本分析
                return {
                    'analysis_text': response,
                    'parsing_error': 'Response not in JSON format'
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'fallback': 'AI情感分析暂时不可用'
            }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """提取关键实体"""
        entities = {
            'companies': [],
            'technologies': [],
            'people': [],
            'locations': [],
            'products': []
        }
        
        # 公司名称模式
        company_patterns = [
            r'(OpenAI|Google|Microsoft|Apple|Amazon|Meta|Tesla|NVIDIA|Intel|AMD)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Inc\.?|\s+Corp\.?|\s+Ltd\.?|\s+LLC)?)',
            r'(字节跳动|阿里巴巴|腾讯|百度|华为|小米|美团|滴滴|蚂蚁金服)'
        ]
        
        # 技术关键词
        tech_keywords = [
            'GPT', 'ChatGPT', 'LLM', '大语言模型', '机器学习', '深度学习',
            '神经网络', '人工智能', 'AI', '自然语言处理', 'NLP', '计算机视觉',
            '强化学习', '迁移学习', '联邦学习', '边缘计算', '量子计算'
        ]
        
        # 产品名称
        product_keywords = [
            'iPhone', 'iPad', 'Tesla', 'ChatGPT', 'Gemini', 'Claude',
            'GPT-4', 'DALL-E', 'Midjourney', 'Stable Diffusion'
        ]
        
        # 提取公司
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['companies'].extend(matches)
        
        # 提取技术
        for tech in tech_keywords:
            if tech.lower() in text.lower():
                entities['technologies'].append(tech)
        
        # 提取产品
        for product in product_keywords:
            if product.lower() in text.lower():
                entities['products'].append(product)
        
        # 去重并排序
        for category in entities:
            entities[category] = sorted(list(set(entities[category])))
        
        return entities
    
    def _assess_market_impact(self, sentiment: str, confidence: float) -> str:
        """评估市场影响"""
        if confidence < 0.4:
            return "影响不明确"
        
        impact_map = {
            'positive': "正面影响" if confidence > 0.6 else "轻微正面影响",
            'negative': "负面影响" if confidence > 0.6 else "轻微负面影响",
            'neutral': "中性影响"
        }
        
        return impact_map.get(sentiment, "未知影响")
    
    def _assess_investor_sentiment(self, keywords: Dict[str, List]) -> str:
        """评估投资者情绪"""
        positive_count = len(keywords.get('positive', []))
        negative_count = len(keywords.get('negative', []))
        
        if positive_count > negative_count * 2:
            return "乐观"
        elif negative_count > positive_count * 2:
            return "悲观"
        else:
            return "谨慎"
    
    def _create_fallback_summary(self, title: str, content: str, level: str) -> str:
        """创建备用摘要"""
        fallback_templates = {
            'executive': f"AI行业新闻：{title[:30]}...",
            'business': f"这是一条关于{title}的AI行业新闻，涉及相关商业发展。",
            'technical': f"技术新闻：{title}。详细内容需要进一步分析。",
            'detailed': f"详细报告：{title}。完整分析正在处理中。"
        }
        return fallback_templates.get(level, title)
    
    def get_adaptive_summary(self, multi_level_result: Dict, user_preference: str = 'business') -> Dict[str, Any]:
        """根据用户偏好返回适合的摘要"""
        summaries = multi_level_result.get('summaries', {})
        
        # 如果用户偏好的层次不存在，按优先级降级
        preference_fallback = ['business', 'technical', 'detailed', 'executive']
        
        if user_preference in summaries:
            selected_summary = summaries[user_preference]
        else:
            for fallback in preference_fallback:
                if fallback in summaries:
                    selected_summary = summaries[fallback]
                    break
            else:
                selected_summary = {'content': '摘要生成失败', 'error': True}
        
        return {
            'summary': selected_summary,
            'preference_used': user_preference,
            'sentiment': multi_level_result.get('sentiment_analysis', {}),
            'entities': multi_level_result.get('entities', {}),
            'metadata': multi_level_result.get('article_metadata', {})
        }


class TrendAnalyzer:
    """趋势分析器"""
    
    def __init__(self):
        self.trend_keywords = {
            'ai_models': ['GPT', 'LLM', '大语言模型', '生成式AI', 'Transformer'],
            'companies': ['OpenAI', 'Google', 'Microsoft', 'Anthropic', '字节跳动'],
            'applications': ['自动驾驶', '医疗AI', '金融AI', '教育AI', '创作AI'],
            'technologies': ['机器学习', '深度学习', '强化学习', '计算机视觉', 'NLP']
        }
    
    def analyze_trending_topics(self, articles: List[Dict], days: int = 7) -> Dict[str, Any]:
        """分析趋势话题"""
        # 过滤最近几天的文章
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_articles = [
            article for article in articles 
            if self._parse_date(article.get('date', '')) >= cutoff_date
        ]
        
        # 统计关键词频率
        keyword_frequency = defaultdict(int)
        category_trends = defaultdict(list)
        
        for article in recent_articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            
            for category, keywords in self.trend_keywords.items():
                for keyword in keywords:
                    count = text.lower().count(keyword.lower())
                    if count > 0:
                        keyword_frequency[keyword] += count
                        category_trends[category].append({
                            'keyword': keyword,
                            'article_title': article.get('title', ''),
                            'date': article.get('date', ''),
                            'count': count
                        })
        
        # 识别热门趋势
        hot_keywords = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'trending_keywords': hot_keywords,
            'category_trends': dict(category_trends),
            'analysis_period': f"{days} days",
            'articles_analyzed': len(recent_articles),
            'trend_summary': self._generate_trend_summary(hot_keywords, category_trends)
        }
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        try:
            # 支持多种日期格式
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                try:
                    return datetime.strptime(date_str[:len(fmt)], fmt)
                except ValueError:
                    continue
            return datetime.now() - timedelta(days=1)  # 默认为昨天
        except Exception:
            return datetime.now() - timedelta(days=1)
    
    def _generate_trend_summary(self, hot_keywords: List, category_trends: Dict) -> str:
        """生成趋势总结"""
        if not hot_keywords:
            return "本期未发现明显趋势"
        
        top_keyword = hot_keywords[0][0]
        keyword_count = hot_keywords[0][1]
        
        summary = f"本期最热门话题是'{top_keyword}'，被提及{keyword_count}次。"
        
        # 分析类别趋势
        top_categories = sorted(category_trends.items(), key=lambda x: len(x[1]), reverse=True)[:3]
        if top_categories:
            category_names = [cat[0] for cat in top_categories]
            summary += f" 主要关注领域包括：{', '.join(category_names)}。"
        
        return summary


# 使用示例和测试
if __name__ == "__main__":
    # 测试增强版摘要生成器
    enhanced_summarizer = EnhancedSummarizer()
    
    # 测试数据
    test_title = "OpenAI发布GPT-4 Turbo，性能提升显著降低成本"
    test_content = """
    OpenAI今日宣布推出GPT-4 Turbo，这是其最新的大语言模型版本。
    新模型在保持高质量输出的同时，显著降低了使用成本，并支持更长的上下文窗口。
    GPT-4 Turbo支持128,000个token的上下文长度，相比之前版本有了重大突破。
    这一升级将使开发者能够构建更复杂的AI应用，同时降低运营成本。
    业界专家认为，这将加速AI技术在企业级应用中的普及。
    """
    
    # 生成多层次摘要
    result = enhanced_summarizer.generate_multi_level_summary(test_title, test_content)
    
    print("=== 多层次摘要测试结果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试趋势分析
    trend_analyzer = TrendAnalyzer()
    test_articles = [
        {
            'title': 'OpenAI发布新模型',
            'summary': 'GPT-4技术突破',
            'date': '2025-09-06'
        },
        {
            'title': 'Google AI进展',
            'summary': 'Gemini模型更新',
            'date': '2025-09-05'
        }
    ]
    
    trends = trend_analyzer.analyze_trending_topics(test_articles)
    print("\n=== 趋势分析测试结果 ===")
    print(json.dumps(trends, ensure_ascii=False, indent=2))

