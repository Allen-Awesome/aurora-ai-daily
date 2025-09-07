#!/usr/bin/env python3
"""
AI新闻助手
智能问答系统，基于新闻库回答用户问题
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import hashlib

from summarizer import ContentSummarizer


class AINewsBot:
    """AI新闻助手，提供智能问答和个性化服务"""
    
    def __init__(self, data_directory: str = "daily_news", api_key: str = None):
        self.data_directory = data_directory
        
        # 如果没有提供api_key，从环境变量获取
        if api_key is None:
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        
        self.summarizer = ContentSummarizer(api_key)
        self.conversation_history = {}
        self.knowledge_cache = {}
        
        # 问题类型分类
        self.question_patterns = {
            'what': [r'什么是', r'什么叫', r'what is', r'what are'],
            'how': [r'如何', r'怎么', r'怎样', r'how to', r'how does'],
            'when': [r'什么时候', r'何时', r'when'],
            'where': [r'在哪', r'哪里', r'where'],
            'why': [r'为什么', r'为何', r'why'],
            'who': [r'谁', r'哪个公司', r'who', r'which company'],
            'trend': [r'趋势', r'发展', r'前景', r'未来', r'trend', r'future'],
            'compare': [r'对比', r'比较', r'差异', r'compare', r'difference'],
            'impact': [r'影响', r'作用', r'effect', r'impact'],
            'invest': [r'投资', r'股价', r'估值', r'investment', r'stock']
        }
        
        # 领域关键词
        self.domain_keywords = {
            'llm': ['GPT', 'LLM', '大语言模型', '生成式AI', 'ChatGPT', 'Claude'],
            'cv': ['计算机视觉', '图像识别', '自动驾驶', 'YOLO', 'ResNet'],
            'nlp': ['自然语言处理', 'NLP', '机器翻译', '文本生成'],
            'robotics': ['机器人', '自动化', '工业机器人', '服务机器人'],
            'chip': ['芯片', '半导体', 'GPU', 'TPU', 'AI芯片', 'NVIDIA'],
            'startup': ['创业', '融资', '投资', 'A轮', 'B轮', 'IPO'],
            'regulation': ['监管', '政策', '法规', '标准', '合规']
        }
    
    def answer_question(self, question: str, user_id: str = "default", 
                       max_articles: int = 10) -> Dict[str, Any]:
        """回答用户问题"""
        # 分析问题类型和领域
        question_analysis = self._analyze_question(question)
        
        # 检索相关文章
        relevant_articles = self._search_relevant_articles(
            question, 
            question_analysis['domain'],
            max_articles
        )
        
        if not relevant_articles:
            return self._generate_no_results_response(question)
        
        # 构建上下文并生成回答
        context = self._build_context(relevant_articles, question)
        answer = self._generate_ai_answer(question, context, question_analysis)
        
        # 生成相关问题建议
        related_questions = self._suggest_related_questions(question, relevant_articles)
        
        # 保存对话历史
        self._save_conversation(user_id, question, answer, relevant_articles)
        
        return {
            'answer': answer,
            'question_type': question_analysis['type'],
            'domain': question_analysis['domain'],
            'sources': self._format_sources(relevant_articles),
            'related_questions': related_questions,
            'confidence_score': self._calculate_confidence(question, relevant_articles),
            'response_time': datetime.now().isoformat(),
            'articles_used': len(relevant_articles)
        }
    
    def _analyze_question(self, question: str) -> Dict[str, Any]:
        """分析问题类型和领域"""
        question_lower = question.lower()
        
        # 识别问题类型
        question_type = 'general'
        for q_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    question_type = q_type
                    break
            if question_type != 'general':
                break
        
        # 识别问题领域
        domains_found = []
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    domains_found.append(domain)
                    break
        
        primary_domain = domains_found[0] if domains_found else 'general'
        
        return {
            'type': question_type,
            'domain': primary_domain,
            'all_domains': domains_found,
            'keywords': self._extract_question_keywords(question)
        }
    
    def _extract_question_keywords(self, question: str) -> List[str]:
        """提取问题中的关键词"""
        # 移除问句词汇
        stop_words = ['什么', '如何', '怎么', '为什么', '哪里', '什么时候', '是', '的', '了', '吗']
        
        # 简单的关键词提取（实际项目中可以使用更高级的NLP工具）
        words = re.findall(r'[\w]+', question)
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return keywords[:5]  # 返回前5个关键词
    
    def _search_relevant_articles(self, question: str, domain: str, 
                                max_articles: int) -> List[Dict[str, Any]]:
        """搜索相关文章"""
        all_articles = self._load_all_articles()
        
        if not all_articles:
            return []
        
        # 计算相关性得分
        scored_articles = []
        question_keywords = set(self._extract_question_keywords(question.lower()))
        
        for article in all_articles:
            score = self._calculate_relevance_score(article, question_keywords, domain)
            if score > 0:
                scored_articles.append((article, score))
        
        # 按相关性排序并返回top结果
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        return [article for article, score in scored_articles[:max_articles]]
    
    def _calculate_relevance_score(self, article: Dict, question_keywords: set, 
                                 domain: str) -> float:
        """计算文章相关性得分"""
        score = 0.0
        
        # 获取文章文本
        article_text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        article_keywords = set(article.get('keywords', []))
        
        # 标题匹配（权重：3.0）
        title_matches = sum(1 for keyword in question_keywords if keyword in article.get('title', '').lower())
        score += title_matches * 3.0
        
        # 摘要匹配（权重：2.0）
        summary_matches = sum(1 for keyword in question_keywords if keyword in article.get('summary', '').lower())
        score += summary_matches * 2.0
        
        # 关键词匹配（权重：1.5）
        keyword_matches = len(question_keywords.intersection(article_keywords))
        score += keyword_matches * 1.5
        
        # 领域匹配（权重：1.0）
        if domain != 'general':
            domain_keywords = self.domain_keywords.get(domain, [])
            domain_matches = sum(1 for keyword in domain_keywords if keyword.lower() in article_text)
            score += domain_matches * 1.0
        
        # 时间衰减（越新的文章权重越高）
        article_date = self._parse_article_date(article.get('date', ''))
        days_old = (datetime.now() - article_date).days
        time_factor = max(0.1, 1.0 - (days_old / 30))  # 30天后权重降到0.1
        score *= time_factor
        
        return score
    
    def _load_all_articles(self) -> List[Dict[str, Any]]:
        """加载所有文章数据"""
        if 'all_articles' in self.knowledge_cache:
            return self.knowledge_cache['all_articles']
        
        articles = []
        
        try:
            # 遍历所有日期目录
            for date_dir in os.listdir(self.data_directory):
                date_path = os.path.join(self.data_directory, date_dir)
                if os.path.isdir(date_path):
                    summaries_file = os.path.join(date_path, 'summaries.json')
                    if os.path.exists(summaries_file):
                        with open(summaries_file, 'r', encoding='utf-8') as f:
                            daily_data = json.load(f)
                            if 'summaries' in daily_data:
                                for article in daily_data['summaries']:
                                    article['date'] = date_dir
                                    articles.append(article)
        
        except Exception as e:
            print(f"加载文章数据时出错: {e}")
        
        # 缓存结果
        self.knowledge_cache['all_articles'] = articles
        return articles
    
    def _parse_article_date(self, date_str: str) -> datetime:
        """解析文章日期"""
        try:
            # 支持多种日期格式
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y%m%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return datetime.now() - timedelta(days=1)
        except Exception:
            return datetime.now() - timedelta(days=1)
    
    def _build_context(self, articles: List[Dict], question: str) -> str:
        """构建AI回答的上下文"""
        context_parts = []
        
        for i, article in enumerate(articles[:5], 1):  # 最多使用5篇文章
            context_parts.append(f"""
            文章{i}：
            标题：{article.get('title', '未知标题')}
            摘要：{article.get('summary', '无摘要')[:300]}
            关键词：{', '.join(article.get('keywords', []))}
            来源：{article.get('source', '未知来源')}
            日期：{article.get('date', '未知日期')}
            """)
        
        return '\n'.join(context_parts)
    
    def _generate_ai_answer(self, question: str, context: str, 
                          question_analysis: Dict) -> str:
        """使用AI生成回答"""
        question_type = question_analysis['type']
        domain = question_analysis['domain']
        
        # 根据问题类型调整提示词
        type_specific_instructions = {
            'what': '请详细解释相关概念、技术或现象，提供准确的定义和背景信息。',
            'how': '请说明具体的方法、步骤或机制，重点关注实施过程和技术细节。',
            'why': '请分析原因、动机和影响因素，提供深入的因果关系分析。',
            'trend': '请分析发展趋势、未来预测和市场前景，结合历史数据和当前状况。',
            'compare': '请对比不同选项的优缺点、特点和适用场景。',
            'impact': '请分析对行业、市场、技术或社会的具体影响和意义。',
            'invest': '请从投资角度分析机会、风险和市场价值。'
        }
        
        domain_context = {
            'llm': '重点关注大语言模型技术、应用场景和发展趋势',
            'cv': '重点关注计算机视觉技术、图像处理和实际应用',
            'chip': '重点关注AI芯片技术、硬件发展和产业链',
            'startup': '重点关注创业公司、投资动态和商业模式'
        }
        
        instruction = type_specific_instructions.get(question_type, '请提供准确、全面的答案。')
        domain_instruction = domain_context.get(domain, '')
        
        prompt = f"""
        请基于以下AI行业新闻资料回答用户问题：
        
        用户问题：{question}
        
        相关新闻资料：
        {context}
        
        回答要求：
        1. {instruction}
        2. {domain_instruction}
        3. 基于提供的新闻资料，引用具体信息和数据
        4. 保持客观中立，避免主观推测
        5. 如果资料不足，请明确说明
        6. 答案长度控制在200-400字
        7. 语言专业但易懂，适合AI行业从业者阅读
        
        请确保答案准确、有用、相关。
        """
        
        try:
            # 直接调用OpenAI API而不是使用ContentSummarizer
            response = self.summarizer.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的AI行业分析师，擅长回答技术问题。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            return f"抱歉，AI回答生成失败：{str(e)}。请稍后重试或重新表述问题。"
    
    def _suggest_related_questions(self, original_question: str, 
                                 articles: List[Dict]) -> List[str]:
        """建议相关问题"""
        suggestions = []
        
        # 基于文章内容生成相关问题
        if articles:
            # 提取常见主题
            all_keywords = []
            for article in articles[:3]:
                all_keywords.extend(article.get('keywords', []))
            
            # 统计关键词频率
            from collections import Counter
            keyword_freq = Counter(all_keywords)
            top_keywords = [kw for kw, count in keyword_freq.most_common(3)]
            
            # 生成问题模板
            question_templates = [
                "{kw}的最新发展如何？",
                "{kw}对行业有什么影响？",
                "{kw}的未来趋势是什么？"
            ]
            
            for keyword in top_keywords:
                for template in question_templates:
                    if keyword != original_question:  # 避免重复
                        suggestions.append(template.format(kw=keyword))
                        if len(suggestions) >= 5:
                            break
                if len(suggestions) >= 5:
                    break
        
        # 添加一些通用的相关问题
        general_questions = [
            "AI行业最近有哪些重要动态？",
            "哪些AI公司值得关注？",
            "AI技术发展趋势如何？",
            "投资AI行业有哪些机会？"
        ]
        
        # 合并并去重
        all_suggestions = suggestions + general_questions
        unique_suggestions = []
        for suggestion in all_suggestions:
            if suggestion not in unique_suggestions and suggestion != original_question:
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:5]
    
    def _calculate_confidence(self, question: str, articles: List[Dict]) -> float:
        """计算回答置信度"""
        if not articles:
            return 0.0
        
        # 基于多个因素计算置信度
        factors = {
            'article_count': min(len(articles) / 5.0, 1.0),  # 文章数量
            'relevance': self._average_relevance(question, articles),  # 相关性
            'recency': self._average_recency(articles),  # 时效性
            'source_quality': self._assess_source_quality(articles)  # 来源质量
        }
        
        # 加权平均
        weights = {'article_count': 0.2, 'relevance': 0.4, 'recency': 0.2, 'source_quality': 0.2}
        confidence = sum(factors[key] * weights[key] for key in factors)
        
        return round(confidence, 2)
    
    def _average_relevance(self, question: str, articles: List[Dict]) -> float:
        """计算平均相关性"""
        if not articles:
            return 0.0
        
        question_keywords = set(self._extract_question_keywords(question.lower()))
        total_relevance = 0.0
        
        for article in articles:
            relevance = self._calculate_relevance_score(article, question_keywords, 'general')
            total_relevance += min(relevance / 10.0, 1.0)  # 归一化到[0,1]
        
        return total_relevance / len(articles)
    
    def _average_recency(self, articles: List[Dict]) -> float:
        """计算平均时效性"""
        if not articles:
            return 0.0
        
        total_recency = 0.0
        for article in articles:
            article_date = self._parse_article_date(article.get('date', ''))
            days_old = (datetime.now() - article_date).days
            recency = max(0.1, 1.0 - (days_old / 7))  # 7天内为1.0，之后衰减
            total_recency += recency
        
        return total_recency / len(articles)
    
    def _assess_source_quality(self, articles: List[Dict]) -> float:
        """评估来源质量"""
        quality_sources = {
            'techcrunch': 0.9,
            'mit_tech_review': 1.0,
            'arxiv': 0.95,
            'github': 0.8,
            'venturebeat': 0.85
        }
        
        if not articles:
            return 0.0
        
        total_quality = 0.0
        for article in articles:
            source = article.get('source', '').lower()
            quality = quality_sources.get(source, 0.7)  # 默认质量0.7
            total_quality += quality
        
        return total_quality / len(articles)
    
    def _format_sources(self, articles: List[Dict]) -> List[Dict[str, Any]]:
        """格式化信息来源"""
        sources = []
        for article in articles[:5]:  # 最多显示5个来源
            sources.append({
                'title': article.get('title', '未知标题'),
                'url': article.get('url', ''),
                'source': article.get('source', '未知来源'),
                'date': article.get('date', '未知日期'),
                'relevance': 'high'  # 简化处理，实际可以计算具体相关性
            })
        return sources
    
    def _save_conversation(self, user_id: str, question: str, answer: str, 
                         articles: List[Dict]):
        """保存对话历史"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'answer': answer,
            'articles_used': len(articles),
            'session_id': self._generate_session_id(user_id)
        }
        
        self.conversation_history[user_id].append(conversation_entry)
        
        # 保持最近50条对话记录
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]
    
    def _generate_session_id(self, user_id: str) -> str:
        """生成会话ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H')
        return hashlib.md5(f"{user_id}_{timestamp}".encode()).hexdigest()[:8]
    
    def _generate_no_results_response(self, question: str) -> Dict[str, Any]:
        """生成无结果时的回复"""
        return {
            'answer': f"抱歉，我在现有的AI新闻数据库中没有找到与「{question}」相关的信息。建议您：\n1. 检查问题表述是否准确\n2. 尝试使用不同的关键词\n3. 关注更广泛的AI行业话题",
            'question_type': 'unknown',
            'domain': 'general',
            'sources': [],
            'related_questions': [
                "AI行业最近有哪些重要新闻？",
                "目前最热门的AI技术是什么？",
                "有哪些值得关注的AI公司？"
            ],
            'confidence_score': 0.0,
            'response_time': datetime.now().isoformat(),
            'articles_used': 0
        }
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """获取对话历史"""
        history = self.conversation_history.get(user_id, [])
        return history[-limit:] if history else []
    
    def get_daily_insights(self, user_id: str = "default") -> Dict[str, Any]:
        """获取每日洞察"""
        # 获取今天的文章
        today = datetime.now().strftime('%Y-%m-%d')
        today_articles = [
            article for article in self._load_all_articles()
            if article.get('date', '').startswith(today.replace('-', ''))
        ]
        
        if not today_articles:
            return {
                'insights': "今日暂无新的AI行业资讯。",
                'article_count': 0,
                'top_topics': [],
                'generated_at': datetime.now().isoformat()
            }
        
        # 生成洞察
        insights_prompt = f"""
        基于今日的AI行业新闻，请生成3-5个关键洞察：
        
        今日新闻摘要：
        {self._format_articles_for_insights(today_articles[:10])}
        
        请提供：
        1. 最重要的3个行业动态
        2. 值得关注的技术趋势
        3. 商业和投资机会
        4. 明天可能的重要新闻方向
        
        要求简洁明了，每个洞察50字以内。
        """
        
        try:
            # 直接调用OpenAI API而不是使用ContentSummarizer
            response = self.summarizer.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的AI行业分析师，擅长提供每日洞察。"},
                    {"role": "user", "content": insights_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            insights = response.choices[0].message.content.strip()
        except Exception as e:
            insights = f"洞察生成暂时不可用：{str(e)}"
        
        # 提取热门话题
        top_topics = self._extract_top_topics(today_articles)
        
        return {
            'insights': insights,
            'article_count': len(today_articles),
            'top_topics': top_topics,
            'generated_at': datetime.now().isoformat(),
            'summary_articles': self._format_sources(today_articles[:5])
        }
    
    def _format_articles_for_insights(self, articles: List[Dict]) -> str:
        """为洞察生成格式化文章摘要"""
        formatted = []
        for i, article in enumerate(articles, 1):
            formatted.append(f"{i}. {article.get('title', '未知标题')} - {article.get('summary', '无摘要')[:100]}")
        return '\n'.join(formatted)
    
    def _extract_top_topics(self, articles: List[Dict]) -> List[str]:
        """提取热门话题"""
        all_keywords = []
        for article in articles:
            all_keywords.extend(article.get('keywords', []))
        
        from collections import Counter
        keyword_freq = Counter(all_keywords)
        return [kw for kw, count in keyword_freq.most_common(5)]


# 使用示例
if __name__ == "__main__":
    # 测试AI新闻助手
    bot = AINewsBot()
    
    # 测试问答
    test_questions = [
        "什么是GPT-4？",
        "OpenAI最近有什么新动态？",
        "AI芯片行业的发展趋势如何？",
        "哪些公司在投资AI技术？"
    ]
    
    print("=== AI新闻助手测试 ===")
    for question in test_questions:
        print(f"\n问题：{question}")
        response = bot.answer_question(question)
        print(f"回答：{response['answer'][:200]}...")
        print(f"置信度：{response['confidence_score']}")
        print(f"使用文章数：{response['articles_used']}")
    
    # 测试每日洞察
    print("\n=== 每日洞察测试 ===")
    insights = bot.get_daily_insights()
    print(json.dumps(insights, ensure_ascii=False, indent=2))

