#!/usr/bin/env python3
"""
个性化仪表板系统
提供用户阅读统计、知识图谱、智能推荐等功能
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import hashlib
import math


class PersonalDashboard:
    """个性化仪表板"""
    
    def __init__(self, user_configs_dir: str = "user_configs", data_dir: str = "daily_news"):
        self.user_configs_dir = user_configs_dir
        self.data_dir = data_dir
        self.analytics = DashboardAnalytics(data_dir)
        
        # 创建用户配置目录
        os.makedirs(user_configs_dir, exist_ok=True)
    
    def generate_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """生成个性化仪表板数据"""
        user_profile = self._load_user_profile(user_id)
        
        return {
            'user_info': {
                'user_id': user_id,
                'last_updated': datetime.now().isoformat(),
                'profile_completion': self._calculate_profile_completion(user_profile)
            },
            'reading_stats': self._get_reading_statistics(user_id),
            'interest_analysis': self._analyze_user_interests(user_id),
            'knowledge_map': self._build_knowledge_map(user_id),
            'learning_progress': self._track_learning_progress(user_id),
            'smart_recommendations': self._generate_smart_recommendations(user_id),
            'industry_pulse': self._get_personalized_industry_pulse(user_id),
            'achievement_system': self._get_user_achievements(user_id),
            'social_insights': self._get_social_insights(user_id)
        }
    
    def _load_user_profile(self, user_id: str) -> Dict[str, Any]:
        """加载用户配置"""
        profile_path = os.path.join(self.user_configs_dir, f"{user_id}.json")
        
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载用户配置失败: {e}")
        
        # 返回默认配置
        return {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'interests': ['AI技术', '机器学习'],
            'reading_history': [],
            'interaction_history': [],
            'preferences': {
                'summary_level': 'business',
                'notification_frequency': 'daily',
                'preferred_sources': []
            }
        }
    
    def _get_reading_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取阅读统计"""
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        # 基础统计
        total_articles = len(reading_history)
        
        # 最近7天阅读统计
        recent_reads = self._filter_recent_activities(reading_history, days=7)
        daily_average = len(recent_reads) / 7
        
        # 阅读连续天数
        reading_streak = self._calculate_reading_streak(reading_history)
        
        # 阅读时间分布
        reading_patterns = self._analyze_reading_patterns(reading_history)
        
        # 阅读深度分析
        reading_depth = self._analyze_reading_depth(reading_history)
        
        return {
            'total_articles_read': total_articles,
            'articles_this_week': len(recent_reads),
            'daily_average': round(daily_average, 1),
            'reading_streak': reading_streak,
            'reading_patterns': reading_patterns,
            'reading_depth': reading_depth,
            'favorite_topics': self._get_favorite_topics(reading_history),
            'reading_efficiency': self._calculate_reading_efficiency(reading_history),
            'knowledge_growth_rate': self._calculate_knowledge_growth(user_id)
        }
    
    def _analyze_user_interests(self, user_id: str) -> Dict[str, Any]:
        """分析用户兴趣"""
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        # 兴趣演变分析
        interest_evolution = self._track_interest_evolution(reading_history)
        
        # 当前兴趣强度
        current_interests = self._calculate_current_interests(reading_history)
        
        # 新兴兴趣识别
        emerging_interests = self._identify_emerging_interests(reading_history)
        
        # 兴趣多样性分析
        interest_diversity = self._calculate_interest_diversity(current_interests)
        
        return {
            'current_interests': current_interests,
            'interest_evolution': interest_evolution,
            'emerging_interests': emerging_interests,
            'interest_diversity_score': interest_diversity,
            'interest_stability': self._calculate_interest_stability(interest_evolution.get('evolution_trend', [])),
            'recommended_expansions': self._suggest_interest_expansions(current_interests)
        }
    
    def _build_knowledge_map(self, user_id: str) -> Dict[str, Any]:
        """构建个人知识图谱"""
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        # 提取所有概念
        concepts = self._extract_user_concepts(reading_history)
        
        # 构建概念关系
        concept_relationships = self._build_concept_relationships(concepts)
        
        # 评估概念掌握程度
        concept_mastery = self._assess_concept_mastery(concepts, reading_history)
        
        # 识别知识空白
        knowledge_gaps = self._identify_knowledge_gaps(concepts)
        
        return {
            'total_concepts': len(concepts),
            'mastery_distribution': self._categorize_mastery_levels(concept_mastery),
            'knowledge_domains': self._group_concepts_by_domain(concepts),
            'concept_relationships': concept_relationships,
            'knowledge_gaps': knowledge_gaps,
            'learning_recommendations': self._generate_learning_recommendations(knowledge_gaps),
            'expertise_areas': self._identify_expertise_areas(concept_mastery)
        }
    
    def _track_learning_progress(self, user_id: str) -> Dict[str, Any]:
        """追踪学习进度"""
        user_profile = self._load_user_profile(user_id)
        
        # 学习目标（如果用户设置了的话）
        learning_goals = user_profile.get('learning_goals', [])
        
        # 知识点掌握进度
        concept_progress = self._calculate_concept_progress(user_id)
        
        # 学习曲线分析
        learning_curve = self._analyze_learning_curve(user_id)
        
        # 学习效率评估
        learning_efficiency = self._assess_learning_efficiency(user_id)
        
        return {
            'overall_progress': self._calculate_overall_progress(concept_progress),
            'learning_goals': self._track_goal_progress(learning_goals, user_id),
            'concept_progress': concept_progress,
            'learning_curve': learning_curve,
            'learning_efficiency': learning_efficiency,
            'milestone_achievements': self._get_learning_milestones(user_id),
            'next_learning_steps': self._suggest_next_steps(user_id)
        }
    
    def _generate_smart_recommendations(self, user_id: str) -> Dict[str, Any]:
        """生成智能推荐"""
        user_profile = self._load_user_profile(user_id)
        user_vector = self._create_user_vector(user_profile)
        
        # 文章推荐
        article_recommendations = self._recommend_articles(user_vector)
        
        # 学习内容推荐
        learning_recommendations = self._recommend_learning_content(user_vector)
        
        # 专家推荐
        expert_recommendations = self._recommend_experts_to_follow(user_vector)
        
        # 技能发展推荐
        skill_recommendations = self._recommend_skill_development(user_vector)
        
        return {
            'articles_to_read': article_recommendations,
            'learning_content': learning_recommendations,
            'experts_to_follow': expert_recommendations,
            'skills_to_develop': skill_recommendations,
            'trending_topics': self._get_personalized_trending_topics(user_vector),
            'recommendation_confidence': self._calculate_recommendation_confidence(user_vector)
        }
    
    def _get_personalized_industry_pulse(self, user_id: str) -> Dict[str, Any]:
        """获取个性化行业脉搏"""
        user_profile = self._load_user_profile(user_id)
        user_interests = user_profile.get('interests', [])
        
        # 基于用户兴趣的行业动态
        relevant_trends = self._filter_trends_by_interests(user_interests)
        
        # 个性化的市场洞察
        market_insights = self._generate_personalized_insights(user_interests)
        
        # 投资机会（如果用户关注投资）
        investment_opportunities = self._identify_investment_opportunities(user_interests)
        
        return {
            'industry_trends': relevant_trends,
            'market_insights': market_insights,
            'investment_opportunities': investment_opportunities,
            'competitive_intelligence': self._get_competitive_intelligence(user_interests),
            'technology_radar': self._create_technology_radar(user_interests),
            'industry_sentiment': self._assess_industry_sentiment(user_interests)
        }
    
    def _get_user_achievements(self, user_id: str) -> Dict[str, Any]:
        """获取用户成就系统"""
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        # 定义成就类型
        achievements = {
            'reading_milestones': self._check_reading_milestones(reading_history),
            'streak_achievements': self._check_streak_achievements(reading_history),
            'knowledge_badges': self._check_knowledge_badges(user_id),
            'exploration_awards': self._check_exploration_awards(reading_history),
            'engagement_honors': self._check_engagement_honors(user_profile)
        }
        
        # 计算总成就分数
        total_score = sum(len(category) for category in achievements.values())
        
        # 下一个可达成的成就
        next_achievements = self._suggest_next_achievements(user_profile)
        
        return {
            'total_achievements': total_score,
            'achievement_categories': achievements,
            'next_achievements': next_achievements,
            'achievement_level': self._calculate_achievement_level(total_score),
            'progress_to_next_level': self._calculate_progress_to_next_level(total_score)
        }
    
    def _get_social_insights(self, user_id: str) -> Dict[str, Any]:
        """获取社交洞察"""
        # 这里可以集成社交功能，比如：
        # - 与其他用户的兴趣相似度
        # - 社区中的活跃度排名
        # - 获得的点赞和评论数
        
        return {
            'community_rank': self._get_community_rank(user_id),
            'similar_users': self._find_similar_users(user_id),
            'discussion_participation': self._get_discussion_stats(user_id),
            'content_sharing': self._get_sharing_stats(user_id),
            'influence_score': self._calculate_influence_score(user_id)
        }
    
    # 辅助方法实现
    
    def _filter_recent_activities(self, activities: List[Dict], days: int) -> List[Dict]:
        """过滤最近的活动"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent = []
        
        for activity in activities:
            activity_date = self._parse_activity_date(activity.get('timestamp', ''))
            if activity_date >= cutoff_date:
                recent.append(activity)
        
        return recent
    
    def _parse_activity_date(self, date_str: str) -> datetime:
        """解析活动日期"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return datetime.now() - timedelta(days=999)  # 默认为很久以前
    
    def _calculate_reading_streak(self, reading_history: List[Dict]) -> int:
        """计算阅读连续天数"""
        if not reading_history:
            return 0
        
        # 按日期分组
        daily_reads = defaultdict(list)
        for read in reading_history:
            date = self._parse_activity_date(read.get('timestamp', '')).date()
            daily_reads[date].append(read)
        
        # 计算连续天数
        sorted_dates = sorted(daily_reads.keys(), reverse=True)
        streak = 0
        current_date = datetime.now().date()
        
        for date in sorted_dates:
            if date == current_date or date == current_date - timedelta(days=streak):
                streak += 1
                current_date = date
            else:
                break
        
        return streak
    
    def _analyze_reading_patterns(self, reading_history: List[Dict]) -> Dict[str, Any]:
        """分析阅读模式"""
        if not reading_history:
            return {'peak_hours': [], 'daily_distribution': {}, 'weekly_pattern': {}}
        
        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)
        weekday_counts = defaultdict(int)
        
        for read in reading_history:
            dt = self._parse_activity_date(read.get('timestamp', ''))
            hour_counts[dt.hour] += 1
            day_counts[dt.day] += 1
            weekday_counts[dt.strftime('%A')] += 1
        
        # 找出高峰时间
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'peak_hours': [f"{hour}:00" for hour, count in peak_hours],
            'hourly_distribution': dict(hour_counts),
            'weekly_pattern': dict(weekday_counts),
            'most_active_day': max(weekday_counts.items(), key=lambda x: x[1])[0] if weekday_counts else 'Monday'
        }
    
    def _analyze_reading_depth(self, reading_history: List[Dict]) -> Dict[str, Any]:
        """分析阅读深度"""
        if not reading_history:
            return {
                'avg_reading_time': 0,
                'deep_reading_ratio': 0,
                'engagement_score': 0,
                'completion_rate': 0
            }
        
        total_reading_time = 0
        deep_readings = 0
        completed_readings = 0
        engagement_scores = []
        
        for read in reading_history:
            # 阅读时长（秒）
            reading_time = read.get('reading_time', 0)
            total_reading_time += reading_time
            
            # 深度阅读判断（阅读时间超过2分钟）
            if reading_time > 120:
                deep_readings += 1
            
            # 完成度（假设有阅读进度数据）
            completion = read.get('completion_rate', 0)
            if completion > 0.8:
                completed_readings += 1
            
            # 参与度分数（基于点赞、分享、评论等）
            engagement = 0
            if read.get('liked'):
                engagement += 1
            if read.get('shared'):
                engagement += 1
            if read.get('commented'):
                engagement += 2
            engagement_scores.append(engagement)
        
        total_articles = len(reading_history)
        avg_reading_time = total_reading_time / total_articles if total_articles > 0 else 0
        deep_reading_ratio = deep_readings / total_articles if total_articles > 0 else 0
        completion_rate = completed_readings / total_articles if total_articles > 0 else 0
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        
        return {
            'avg_reading_time': round(avg_reading_time, 1),
            'deep_reading_ratio': round(deep_reading_ratio, 3),
            'engagement_score': round(avg_engagement, 2),
            'completion_rate': round(completion_rate, 3),
            'total_reading_time': total_reading_time,
            'deep_reading_count': deep_readings
        }
    
    def _create_user_vector(self, user_profile: Dict[str, Any]) -> Dict[str, float]:
        """创建用户特征向量"""
        # 基于用户的阅读历史、兴趣、互动创建特征向量
        interests = user_profile.get('interests', [])
        reading_history = user_profile.get('reading_history', [])
        
        # 兴趣权重
        interest_weights = {}
        for interest in interests:
            interest_weights[interest] = 1.0
        
        # 基于阅读历史调整权重
        for read in reading_history[-20:]:  # 最近20篇文章
            article_keywords = read.get('keywords', [])
            for keyword in article_keywords:
                interest_weights[keyword] = interest_weights.get(keyword, 0) + 0.1
        
        return interest_weights
    
    def save_user_interaction(self, user_id: str, interaction_type: str, 
                            interaction_data: Dict[str, Any]):
        """保存用户交互数据"""
        user_profile = self._load_user_profile(user_id)
        
        if 'interaction_history' not in user_profile:
            user_profile['interaction_history'] = []
        
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type,
            'data': interaction_data
        }
        
        user_profile['interaction_history'].append(interaction)
        
        # 保持最近1000条交互记录
        if len(user_profile['interaction_history']) > 1000:
            user_profile['interaction_history'] = user_profile['interaction_history'][-1000:]
        
        self._save_user_profile(user_id, user_profile)
    
    def _save_user_profile(self, user_id: str, profile: Dict[str, Any]):
        """保存用户配置"""
        profile_path = os.path.join(self.user_configs_dir, f"{user_id}.json")
        
        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户配置失败: {e}")
    
    # 占位符方法（实际项目中需要完整实现）
    
    def _calculate_profile_completion(self, profile: Dict) -> float:
        """计算配置完成度"""
        required_fields = ['interests', 'preferences']
        completed = sum(1 for field in required_fields if profile.get(field))
        return completed / len(required_fields)
    
    def _get_favorite_topics(self, reading_history: List[Dict]) -> List[str]:
        """获取最喜欢的话题"""
        topic_counts = Counter()
        for read in reading_history:
            keywords = read.get('keywords', [])
            topic_counts.update(keywords)
        return [topic for topic, count in topic_counts.most_common(5)]
    
    def _calculate_reading_efficiency(self, reading_history: List[Dict]) -> float:
        """计算阅读效率"""
        # 简化实现：基于阅读频率
        if len(reading_history) < 7:
            return 0.5
        
        recent_week = self._filter_recent_activities(reading_history, 7)
        return min(len(recent_week) / 10.0, 1.0)  # 假设每天读10篇文章为满分
    
    def _calculate_knowledge_growth(self, user_id: str) -> float:
        """计算知识增长率"""
        # 简化实现
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        if len(reading_history) < 14:
            return 0.1
        
        # 比较最近一周和上一周的阅读量
        recent_week = self._filter_recent_activities(reading_history, 7)
        previous_week = self._filter_recent_activities(reading_history, 14)
        previous_week = [r for r in previous_week if r not in recent_week]
        
        if not previous_week:
            return 0.2
        
        growth_rate = (len(recent_week) - len(previous_week)) / len(previous_week)
        return max(-1.0, min(1.0, growth_rate))  # 限制在[-1, 1]范围内
    
    def _track_interest_evolution(self, reading_history: List[Dict]) -> Dict[str, Any]:
        """追踪兴趣演变"""
        if not reading_history:
            return {'evolution_trend': [], 'interest_changes': []}
        
        # 按时间分组分析兴趣变化
        time_periods = []
        current_date = datetime.now()
        
        # 分析最近6个月的兴趣演变（每月为一个时期）
        for i in range(6):
            period_start = current_date - timedelta(days=30*(i+1))
            period_end = current_date - timedelta(days=30*i)
            
            period_reads = [
                read for read in reading_history
                if period_start <= self._parse_activity_date(read.get('timestamp', '')) < period_end
            ]
            
            # 统计该时期的兴趣关键词
            keywords_count = Counter()
            for read in period_reads:
                keywords = read.get('keywords', [])
                keywords_count.update(keywords)
            
            time_periods.append({
                'period': f"{period_start.strftime('%Y-%m')}",
                'top_interests': [keyword for keyword, count in keywords_count.most_common(5)],
                'total_articles': len(period_reads)
            })
        
        # 识别兴趣变化趋势
        interest_changes = []
        if len(time_periods) >= 2:
            latest_interests = set(time_periods[0]['top_interests'])
            previous_interests = set(time_periods[1]['top_interests'])
            
            new_interests = latest_interests - previous_interests
            lost_interests = previous_interests - latest_interests
            
            if new_interests:
                interest_changes.append({
                    'type': 'new',
                    'interests': list(new_interests),
                    'description': f"新增兴趣：{', '.join(new_interests)}"
                })
            
            if lost_interests:
                interest_changes.append({
                    'type': 'lost',
                    'interests': list(lost_interests),
                    'description': f"减少关注：{', '.join(lost_interests)}"
                })
        
        return {
            'evolution_trend': time_periods,
            'interest_changes': interest_changes,
            'stability_score': self._calculate_interest_stability(time_periods)
        }
    
    def _calculate_current_interests(self, reading_history: List[Dict]) -> Dict[str, float]:
        """计算当前兴趣强度"""
        if not reading_history:
            return {}
        
        # 分析最近30天的阅读记录
        recent_reads = self._filter_recent_activities(reading_history, 30)
        
        # 统计关键词频率
        keyword_counts = Counter()
        total_weight = 0
        
        for read in recent_reads:
            # 根据阅读时间给予不同权重（越新权重越高）
            days_ago = (datetime.now() - self._parse_activity_date(read.get('timestamp', ''))).days
            weight = max(1.0 - days_ago / 30.0, 0.1)  # 权重在0.1-1.0之间
            
            keywords = read.get('keywords', [])
            for keyword in keywords:
                keyword_counts[keyword] += weight
                total_weight += weight
        
        # 归一化为兴趣强度分数
        interest_scores = {}
        if total_weight > 0:
            for keyword, count in keyword_counts.items():
                interest_scores[keyword] = round(count / total_weight, 3)
        
        return dict(keyword_counts.most_common(10))
    
    def _identify_emerging_interests(self, reading_history: List[Dict]) -> List[Dict[str, Any]]:
        """识别新兴兴趣"""
        if len(reading_history) < 20:
            return []
        
        # 比较最近两周和之前的兴趣
        recent_reads = self._filter_recent_activities(reading_history, 14)
        earlier_reads = [r for r in reading_history if r not in recent_reads][-50:]  # 取之前的50条记录
        
        # 统计关键词
        recent_keywords = Counter()
        earlier_keywords = Counter()
        
        for read in recent_reads:
            recent_keywords.update(read.get('keywords', []))
        
        for read in earlier_reads:
            earlier_keywords.update(read.get('keywords', []))
        
        # 识别新兴兴趣（最近出现频率高但之前很少出现的）
        emerging_interests = []
        for keyword, recent_count in recent_keywords.most_common(20):
            earlier_count = earlier_keywords.get(keyword, 0)
            
            # 计算增长率
            if earlier_count == 0:
                growth_rate = float('inf')  # 全新的兴趣
            else:
                growth_rate = recent_count / earlier_count
            
            # 如果增长率大于2且最近出现次数大于等于3，认为是新兴兴趣
            if growth_rate >= 2.0 and recent_count >= 3:
                emerging_interests.append({
                    'keyword': keyword,
                    'growth_rate': growth_rate if growth_rate != float('inf') else 999,
                    'recent_count': recent_count,
                    'earlier_count': earlier_count,
                    'status': 'new' if earlier_count == 0 else 'growing'
                })
        
        return sorted(emerging_interests, key=lambda x: x['growth_rate'], reverse=True)[:5]
    
    def _calculate_interest_diversity(self, current_interests: Dict[str, float]) -> Dict[str, Any]:
        """计算兴趣多样性"""
        if not current_interests:
            return {
                'diversity_score': 0,
                'category_distribution': {},
                'concentration_index': 0
            }
        
        # 计算兴趣分布的熵（多样性指标）
        total_weight = sum(current_interests.values())
        probabilities = [weight / total_weight for weight in current_interests.values()]
        
        # 计算香农熵
        entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
        max_entropy = math.log2(len(current_interests))
        diversity_score = entropy / max_entropy if max_entropy > 0 else 0
        
        # 计算集中度指数（赫芬达尔指数）
        concentration_index = sum(p ** 2 for p in probabilities)
        
        # 简单的分类映射（实际项目中可以用更复杂的分类方法）
        category_mapping = {
            'GPT': 'LLM',
            'ChatGPT': 'LLM',
            'LLM': 'LLM',
            '大语言模型': 'LLM',
            '机器学习': 'ML',
            '深度学习': 'ML',
            '计算机视觉': 'CV',
            '自动驾驶': 'CV',
            '自然语言处理': 'NLP',
            'NLP': 'NLP'
        }
        
        category_distribution = Counter()
        for keyword, weight in current_interests.items():
            category = category_mapping.get(keyword, '其他')
            category_distribution[category] += weight
        
        return {
            'diversity_score': round(diversity_score, 3),
            'category_distribution': dict(category_distribution),
            'concentration_index': round(concentration_index, 3),
            'total_interests': len(current_interests)
        }
    
    def _calculate_interest_stability(self, time_periods: List[Dict]) -> float:
        """计算兴趣稳定性"""
        if len(time_periods) < 2:
            return 1.0
        
        # 计算相邻时期兴趣的重叠度
        overlaps = []
        for i in range(len(time_periods) - 1):
            current_interests = set(time_periods[i]['top_interests'])
            next_interests = set(time_periods[i + 1]['top_interests'])
            
            if current_interests or next_interests:
                overlap = len(current_interests & next_interests) / len(current_interests | next_interests)
                overlaps.append(overlap)
        
        return round(sum(overlaps) / len(overlaps), 3) if overlaps else 1.0
    
    def _suggest_interest_expansions(self, current_interests: Dict[str, float]) -> List[str]:
        """建议兴趣扩展方向"""
        if not current_interests:
            return ['机器学习', '深度学习', '自然语言处理', '计算机视觉', '强化学习']
        
        # 基于当前兴趣建议相关领域
        suggestions = []
        interest_mapping = {
            'GPT': ['自然语言处理', '生成式AI', '对话系统'],
            'LLM': ['Transformer', '预训练模型', '模型压缩'],
            '大语言模型': ['多模态AI', '知识图谱', '推理能力'],
            '机器学习': ['深度学习', '强化学习', '联邦学习'],
            '计算机视觉': ['图像生成', '目标检测', '图像分割'],
            '自动驾驶': ['传感器融合', '路径规划', '决策算法']
        }
        
        for interest in current_interests.keys():
            if interest in interest_mapping:
                suggestions.extend(interest_mapping[interest])
        
        # 去重并限制数量
        unique_suggestions = list(set(suggestions))
        return unique_suggestions[:5] if unique_suggestions else ['AI伦理', '边缘计算', '量子计算', '脑机接口', '数字孪生']
    
    def _extract_user_concepts(self, reading_history: List[Dict]) -> List[Dict[str, Any]]:
        """从阅读历史中提取用户概念"""
        if not reading_history:
            return []
        
        concepts = []
        concept_counts = Counter()
        
        for read in reading_history:
            # 从关键词中提取概念
            keywords = read.get('keywords', [])
            for keyword in keywords:
                concept_counts[keyword] += 1
        
        # 构建概念对象
        for concept, count in concept_counts.most_common(20):
            concepts.append({
                'name': concept,
                'frequency': count,
                'category': self._categorize_concept(concept),
                'first_encountered': self._find_first_encounter(concept, reading_history),
                'last_encountered': self._find_last_encounter(concept, reading_history)
            })
        
        return concepts
    
    def _categorize_concept(self, concept: str) -> str:
        """对概念进行分类"""
        categories = {
            'LLM': ['GPT', 'ChatGPT', 'LLM', '大语言模型', 'Transformer', 'BERT'],
            'CV': ['计算机视觉', '图像识别', '目标检测', 'CNN', 'YOLO'],
            'ML': ['机器学习', '深度学习', '神经网络', '算法', '训练'],
            'Company': ['OpenAI', 'Google', 'Microsoft', 'Meta', '百度', '阿里巴巴'],
            'Application': ['自动驾驶', '医疗AI', '金融AI', '推荐系统'],
            'Technology': ['量子计算', '边缘计算', '云计算', '区块链']
        }
        
        for category, keywords in categories.items():
            if any(keyword.lower() in concept.lower() or concept.lower() in keyword.lower() for keyword in keywords):
                return category
        
        return 'Other'
    
    def _find_first_encounter(self, concept: str, reading_history: List[Dict]) -> str:
        """找到第一次遇到概念的时间"""
        for read in reversed(reading_history):  # 从最早的开始查找
            if concept in read.get('keywords', []):
                return read.get('timestamp', '')
        return ''
    
    def _find_last_encounter(self, concept: str, reading_history: List[Dict]) -> str:
        """找到最后一次遇到概念的时间"""
        for read in reading_history:  # 从最新的开始查找
            if concept in read.get('keywords', []):
                return read.get('timestamp', '')
        return ''
    
    def _build_concept_relationships(self, concepts: List[Dict]) -> Dict[str, Any]:
        """构建概念关系图"""
        if not concepts:
            return {'nodes': [], 'edges': [], 'clusters': []}
        
        # 简化的关系构建
        nodes = []
        edges = []
        clusters = defaultdict(list)
        
        for concept in concepts:
            nodes.append({
                'id': concept['name'],
                'label': concept['name'],
                'category': concept['category'],
                'size': min(concept['frequency'] * 2, 20)  # 限制节点大小
            })
            
            # 按类别分组
            clusters[concept['category']].append(concept['name'])
        
        # 创建同类别概念之间的边
        for category, concept_names in clusters.items():
            for i, concept1 in enumerate(concept_names):
                for concept2 in concept_names[i+1:]:
                    edges.append({
                        'source': concept1,
                        'target': concept2,
                        'weight': 1,
                        'type': 'same_category'
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'clusters': dict(clusters),
            'total_concepts': len(concepts),
            'categories': list(clusters.keys())
        }
    
    def _assess_concept_mastery(self, concepts: List[Dict], reading_history: List[Dict]) -> Dict[str, Any]:
        """评估概念掌握程度"""
        if not concepts:
            return {'mastery_levels': {}, 'average_mastery': 0, 'strong_concepts': [], 'weak_concepts': []}
        
        mastery_levels = {}
        
        for concept in concepts:
            concept_name = concept['name']
            frequency = concept['frequency']
            
            # 简单的掌握度计算
            # 基于频率、时间跨度等因素
            if frequency >= 10:
                mastery = 'Expert'
            elif frequency >= 5:
                mastery = 'Advanced'
            elif frequency >= 3:
                mastery = 'Intermediate'
            else:
                mastery = 'Beginner'
            
            mastery_levels[concept_name] = {
                'level': mastery,
                'score': min(frequency / 10.0, 1.0),  # 归一化到0-1
                'frequency': frequency
            }
        
        # 统计
        scores = [info['score'] for info in mastery_levels.values()]
        average_mastery = sum(scores) / len(scores) if scores else 0
        
        strong_concepts = [name for name, info in mastery_levels.items() if info['score'] >= 0.7]
        weak_concepts = [name for name, info in mastery_levels.items() if info['score'] < 0.3]
        
        return {
            'mastery_levels': mastery_levels,
            'average_mastery': round(average_mastery, 3),
            'strong_concepts': strong_concepts[:5],
            'weak_concepts': weak_concepts[:5]
        }
    
    def _identify_knowledge_gaps(self, concepts: List[Dict]) -> List[Dict[str, Any]]:
        """识别知识空白"""
        if not concepts:
            return []
        
        gaps = []
        
        # 基于概念类别识别空白
        category_counts = Counter()
        for concept in concepts:
            category_counts[concept['category']] += 1
        
        # 预期的AI领域知识类别
        expected_categories = {
            'LLM': '大语言模型',
            'CV': '计算机视觉', 
            'ML': '机器学习',
            'Company': 'AI公司',
            'Application': 'AI应用',
            'Technology': '前沿技术'
        }
        
        for category, description in expected_categories.items():
            count = category_counts.get(category, 0)
            if count < 2:  # 如果某个类别的概念少于2个，认为是知识空白
                gaps.append({
                    'category': category,
                    'description': description,
                    'current_count': count,
                    'recommended_count': 5,
                    'priority': 'high' if count == 0 else 'medium'
                })
        
        return gaps
    
    def _categorize_mastery_levels(self, concept_mastery: Dict) -> Dict[str, int]:
        """按掌握程度分类"""
        levels = {'Expert': 0, 'Advanced': 0, 'Intermediate': 0, 'Beginner': 0}
        
        for mastery_info in concept_mastery.get('mastery_levels', {}).values():
            level = mastery_info.get('level', 'Beginner')
            levels[level] += 1
        
        return levels
    
    def _group_concepts_by_domain(self, concepts: List[Dict]) -> Dict[str, List[str]]:
        """按领域分组概念"""
        domains = defaultdict(list)
        
        for concept in concepts:
            category = concept['category']
            domains[category].append(concept['name'])
        
        return dict(domains)
    
    def _generate_learning_recommendations(self, knowledge_gaps: List[Dict]) -> List[Dict[str, Any]]:
        """生成学习建议"""
        recommendations = []
        
        for gap in knowledge_gaps:
            category = gap['category']
            
            # 基于类别推荐学习内容
            category_recommendations = {
                'LLM': ['学习Transformer原理', '了解GPT系列发展', '掌握提示工程技巧'],
                'CV': ['学习CNN基础', '了解目标检测算法', '掌握图像处理技术'],
                'ML': ['学习机器学习基础', '了解深度学习框架', '掌握模型评估方法'],
                'Company': ['关注AI领域头部公司', '了解投资动态', '跟踪技术发展'],
                'Application': ['了解AI在各行业应用', '学习解决方案案例', '掌握部署实践'],
                'Technology': ['关注前沿技术趋势', '学习新兴技术概念', '了解技术发展路线']
            }
            
            for suggestion in category_recommendations.get(category, ['扩大相关领域阅读']):
                recommendations.append({
                    'category': gap['category'],
                    'suggestion': suggestion,
                    'priority': gap['priority'],
                    'description': f"针对{gap['description']}领域的学习建议"
                })
        
        return recommendations[:10]  # 限制推荐数量
    
    def _identify_expertise_areas(self, concept_mastery: Dict) -> List[Dict[str, Any]]:
        """识别用户专业领域"""
        if not concept_mastery or not concept_mastery.get('mastery_levels'):
            return []
        
        expertise_areas = []
        mastery_levels = concept_mastery['mastery_levels']
        
        # 按掌握程度分类概念
        expert_concepts = [name for name, info in mastery_levels.items() if info['level'] == 'Expert']
        advanced_concepts = [name for name, info in mastery_levels.items() if info['level'] == 'Advanced']
        
        # 基于概念数量和掌握程度判断专业领域
        all_strong_concepts = expert_concepts + advanced_concepts
        
        if not all_strong_concepts:
            return [{
                'area': '入门学习者',
                'level': 'Beginner',
                'concepts': [],
                'strength': 0.1,
                'description': '正在AI领域起步学习'
            }]
        
        # 按类别分组强势概念
        area_concepts = defaultdict(list)
        for concept in all_strong_concepts:
            category = self._categorize_concept(concept)
            area_concepts[category].append(concept)
        
        # 生成专业领域
        for category, concepts in area_concepts.items():
            if len(concepts) >= 2:  # 至少有2个强势概念才算专业领域
                area_mapping = {
                    'LLM': '大语言模型专家',
                    'CV': '计算机视觉专家', 
                    'ML': '机器学习专家',
                    'Company': 'AI行业分析师',
                    'Application': 'AI应用专家',
                    'Technology': 'AI技术专家'
                }
                
                area_name = area_mapping.get(category, f'{category}专家')
                
                # 计算专业强度
                expert_count = sum(1 for c in concepts if c in expert_concepts)
                advanced_count = sum(1 for c in concepts if c in advanced_concepts)
                strength = (expert_count * 1.0 + advanced_count * 0.7) / len(concepts)
                
                # 确定专业级别
                if strength >= 0.8:
                    level = 'Expert'
                elif strength >= 0.6:
                    level = 'Advanced'
                elif strength >= 0.4:
                    level = 'Intermediate'
                else:
                    level = 'Developing'
                
                expertise_areas.append({
                    'area': area_name,
                    'level': level,
                    'concepts': concepts,
                    'strength': round(strength, 3),
                    'description': f'在{area_name}领域有{len(concepts)}个强势概念'
                })
        
        # 按专业强度排序
        expertise_areas.sort(key=lambda x: x['strength'], reverse=True)
        
        return expertise_areas[:5]  # 返回最多5个专业领域
    
    def _calculate_concept_progress(self, user_id: str) -> Dict[str, Any]:
        """计算用户概念掌握进度"""
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        if not reading_history:
            return {
                'total_concepts_encountered': 0,
                'concepts_by_level': {'Beginner': 0, 'Intermediate': 0, 'Advanced': 0, 'Expert': 0},
                'learning_velocity': 0,
                'progress_trend': 'stable',
                'recent_progress': []
            }
        
        # 提取概念和计算掌握程度
        concepts = self._extract_user_concepts(reading_history)
        concept_mastery = self._assess_concept_mastery(concepts, reading_history)
        
        # 按掌握级别分类
        mastery_levels = concept_mastery.get('mastery_levels', {})
        concepts_by_level = {'Beginner': 0, 'Intermediate': 0, 'Advanced': 0, 'Expert': 0}
        
        for concept_info in mastery_levels.values():
            level = concept_info.get('level', 'Beginner')
            concepts_by_level[level] += 1
        
        # 计算学习速度（最近7天新概念数）
        recent_concepts = self._get_recent_concepts(reading_history, 7)
        learning_velocity = len(recent_concepts)
        
        # 分析进度趋势
        progress_trend = self._analyze_progress_trend(reading_history)
        
        # 最近学习进度
        recent_progress = self._get_recent_learning_progress(reading_history, 7)
        
        return {
            'total_concepts_encountered': len(concepts),
            'concepts_by_level': concepts_by_level,
            'learning_velocity': learning_velocity,
            'progress_trend': progress_trend,
            'recent_progress': recent_progress,
            'mastery_distribution': {
                'expert_ratio': concepts_by_level['Expert'] / max(len(concepts), 1),
                'advanced_ratio': concepts_by_level['Advanced'] / max(len(concepts), 1),
                'beginner_ratio': concepts_by_level['Beginner'] / max(len(concepts), 1)
            }
        }
    
    def _get_recent_concepts(self, reading_history: List[Dict], days: int) -> List[str]:
        """获取最近几天接触的新概念"""
        recent_reads = self._filter_recent_activities(reading_history, days)
        
        all_concepts = set()
        for read in recent_reads:
            keywords = read.get('keywords', [])
            all_concepts.update(keywords)
        
        return list(all_concepts)
    
    def _analyze_progress_trend(self, reading_history: List[Dict]) -> str:
        """分析学习进度趋势"""
        if len(reading_history) < 14:
            return 'stable'
        
        # 比较最近一周和前一周的阅读量
        recent_week = self._filter_recent_activities(reading_history, 7)
        previous_week = self._filter_recent_activities(reading_history, 14)
        previous_week = [r for r in previous_week if r not in recent_week]
        
        recent_count = len(recent_week)
        previous_count = len(previous_week)
        
        if recent_count > previous_count * 1.2:
            return 'accelerating'
        elif recent_count < previous_count * 0.8:
            return 'slowing'
        else:
            return 'stable'
    
    def _get_recent_learning_progress(self, reading_history: List[Dict], days: int) -> List[Dict[str, Any]]:
        """获取最近的学习进度记录"""
        recent_reads = self._filter_recent_activities(reading_history, days)
        
        progress_records = []
        for read in recent_reads[:5]:  # 最多5条记录
            progress_records.append({
                'date': read.get('timestamp', ''),
                'concepts_learned': len(read.get('keywords', [])),
                'reading_time': read.get('reading_time', 0),
                'completion_rate': read.get('completion_rate', 0),
                'engagement': 1 if read.get('liked') else 0
            })
        
        return progress_records
    
    def _analyze_learning_curve(self, user_id: str) -> Dict[str, Any]:
        """分析用户学习曲线"""
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        if not reading_history:
            return {
                'curve_type': 'starting',
                'learning_phases': [],
                'current_phase': 'initialization',
                'growth_rate': 0,
                'consistency_score': 0,
                'recommendations': ['开始定期阅读AI相关内容', '建立学习计划']
            }
        
        # 按时间段分析学习活动
        time_periods = self._divide_into_time_periods(reading_history)
        
        # 计算每个时期的学习指标
        learning_phases = []
        for period in time_periods:
            phase_data = self._calculate_phase_metrics(period)
            learning_phases.append(phase_data)
        
        # 分析整体学习曲线类型
        curve_type = self._determine_curve_type(learning_phases)
        
        # 计算成长率
        growth_rate = self._calculate_growth_rate(learning_phases)
        
        # 评估学习一致性
        consistency_score = self._calculate_consistency_score(learning_phases)
        
        # 确定当前学习阶段
        current_phase = self._identify_current_phase(learning_phases[-1] if learning_phases else {})
        
        # 生成学习建议
        recommendations = self._generate_learning_recommendations_curve(curve_type, current_phase, consistency_score)
        
        return {
            'curve_type': curve_type,
            'learning_phases': learning_phases,
            'current_phase': current_phase,
            'growth_rate': round(growth_rate, 3),
            'consistency_score': round(consistency_score, 3),
            'recommendations': recommendations
        }
    
    def _divide_into_time_periods(self, reading_history: List[Dict]) -> List[List[Dict]]:
        """将阅读历史按时间段分组"""
        if not reading_history:
            return []
        
        # 按周分组
        periods = []
        current_week = []
        current_week_start = None
        
        for read in sorted(reading_history, key=lambda x: x.get('timestamp', '')):
            read_date = self._parse_activity_date(read.get('timestamp', ''))
            week_start = read_date - timedelta(days=read_date.weekday())
            
            if current_week_start is None:
                current_week_start = week_start
            
            if week_start == current_week_start:
                current_week.append(read)
            else:
                if current_week:
                    periods.append(current_week)
                current_week = [read]
                current_week_start = week_start
        
        if current_week:
            periods.append(current_week)
        
        return periods[-8:]  # 最近8周
    
    def _calculate_phase_metrics(self, period_reads: List[Dict]) -> Dict[str, Any]:
        """计算时期的学习指标"""
        if not period_reads:
            return {
                'articles_read': 0,
                'total_reading_time': 0,
                'concepts_learned': 0,
                'avg_completion_rate': 0,
                'engagement_level': 0
            }
        
        total_reading_time = sum(read.get('reading_time', 0) for read in period_reads)
        concepts = set()
        total_completion = 0
        engagement_actions = 0
        
        for read in period_reads:
            concepts.update(read.get('keywords', []))
            total_completion += read.get('completion_rate', 0)
            if read.get('liked') or read.get('shared') or read.get('commented'):
                engagement_actions += 1
        
        return {
            'articles_read': len(period_reads),
            'total_reading_time': total_reading_time,
            'concepts_learned': len(concepts),
            'avg_completion_rate': total_completion / len(period_reads) if period_reads else 0,
            'engagement_level': engagement_actions / len(period_reads) if period_reads else 0,
            'period_start': period_reads[0].get('timestamp', '') if period_reads else ''
        }
    
    def _determine_curve_type(self, learning_phases: List[Dict]) -> str:
        """确定学习曲线类型"""
        if len(learning_phases) < 3:
            return 'starting'
        
        # 分析文章阅读数量趋势
        article_counts = [phase['articles_read'] for phase in learning_phases]
        
        # 计算趋势
        if len(article_counts) < 3:
            return 'stable'
        
        # 简单的趋势分析
        recent_avg = sum(article_counts[-3:]) / 3
        early_avg = sum(article_counts[:3]) / 3
        
        if recent_avg > early_avg * 1.5:
            return 'exponential'
        elif recent_avg > early_avg * 1.2:
            return 'linear'
        elif recent_avg < early_avg * 0.8:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_growth_rate(self, learning_phases: List[Dict]) -> float:
        """计算学习成长率"""
        if len(learning_phases) < 2:
            return 0
        
        first_phase = learning_phases[0]
        last_phase = learning_phases[-1]
        
        first_score = (first_phase['articles_read'] + first_phase['concepts_learned']) / 2
        last_score = (last_phase['articles_read'] + last_phase['concepts_learned']) / 2
        
        if first_score == 0:
            return 1.0 if last_score > 0 else 0
        
        return (last_score - first_score) / first_score
    
    def _calculate_consistency_score(self, learning_phases: List[Dict]) -> float:
        """计算学习一致性分数"""
        if len(learning_phases) < 2:
            return 1.0
        
        article_counts = [phase['articles_read'] for phase in learning_phases]
        
        # 计算变异系数
        mean_count = sum(article_counts) / len(article_counts)
        if mean_count == 0:
            return 1.0
        
        variance = sum((count - mean_count) ** 2 for count in article_counts) / len(article_counts)
        std_dev = variance ** 0.5
        coefficient_of_variation = std_dev / mean_count
        
        # 转换为一致性分数 (0-1)
        consistency = max(0, 1 - coefficient_of_variation)
        return consistency
    
    def _identify_current_phase(self, latest_phase: Dict) -> str:
        """识别当前学习阶段"""
        if not latest_phase:
            return 'initialization'
        
        articles_read = latest_phase.get('articles_read', 0)
        concepts_learned = latest_phase.get('concepts_learned', 0)
        engagement = latest_phase.get('engagement_level', 0)
        
        if articles_read >= 10 and concepts_learned >= 15 and engagement >= 0.3:
            return 'advanced'
        elif articles_read >= 5 and concepts_learned >= 8 and engagement >= 0.2:
            return 'intermediate'
        elif articles_read >= 2 and concepts_learned >= 3:
            return 'developing'
        else:
            return 'beginner'
    
    def _generate_learning_recommendations_curve(self, curve_type: str, current_phase: str, consistency: float) -> List[str]:
        """基于学习曲线生成建议"""
        recommendations = []
        
        # 基于曲线类型的建议
        if curve_type == 'exponential':
            recommendations.append('学习进展很好，保持当前节奏')
        elif curve_type == 'linear':
            recommendations.append('稳步进步中，可以适当增加学习强度')
        elif curve_type == 'declining':
            recommendations.append('学习活跃度下降，建议重新制定学习计划')
        elif curve_type == 'stable':
            recommendations.append('学习较为稳定，可以尝试挑战更深层次的内容')
        else:
            recommendations.append('刚开始学习，建议建立固定的阅读习惯')
        
        # 基于当前阶段的建议
        phase_recommendations = {
            'beginner': '建议每天阅读1-2篇AI基础文章',
            'developing': '可以开始关注特定AI领域的深度内容',
            'intermediate': '建议加强实践和案例分析',
            'advanced': '可以开始关注前沿研究和技术趋势'
        }
        
        if current_phase in phase_recommendations:
            recommendations.append(phase_recommendations[current_phase])
        
        # 基于一致性的建议
        if consistency < 0.5:
            recommendations.append('建议建立更规律的学习习惯')
        elif consistency > 0.8:
            recommendations.append('学习习惯很好，可以考虑拓展学习领域')
        
        return recommendations[:3]  # 最多3条建议
    
    def _assess_learning_efficiency(self, user_id: str) -> Dict[str, Any]:
        """评估学习效率"""
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        if not reading_history:
            return {
                'efficiency_score': 0,
                'time_utilization': 0,
                'concept_absorption_rate': 0,
                'retention_estimate': 0,
                'improvement_areas': ['建立学习习惯', '增加阅读量'],
                'efficiency_trend': 'stable'
            }
        
        # 计算效率指标
        total_reading_time = sum(read.get('reading_time', 0) for read in reading_history)
        total_concepts = len(set(keyword for read in reading_history for keyword in read.get('keywords', [])))
        total_articles = len(reading_history)
        
        # 概念吸收率 (每分钟学到的概念数)
        if total_reading_time > 0:
            concept_absorption_rate = (total_concepts * 60) / total_reading_time  # 每小时概念数
        else:
            concept_absorption_rate = 0
        
        # 时间利用率 (基于完成率)
        completion_rates = [read.get('completion_rate', 0) for read in reading_history]
        time_utilization = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        
        # 保留率估算 (基于重复概念和参与度)
        engagement_actions = sum(1 for read in reading_history 
                               if read.get('liked') or read.get('shared') or read.get('commented'))
        retention_estimate = min(1.0, (engagement_actions / total_articles) + (time_utilization * 0.5))
        
        # 综合效率分数
        efficiency_score = (concept_absorption_rate * 0.4 + 
                          time_utilization * 0.3 + 
                          retention_estimate * 0.3)
        
        # 效率趋势分析
        efficiency_trend = self._analyze_efficiency_trend(reading_history)
        
        # 改进建议
        improvement_areas = self._identify_efficiency_improvements(
            concept_absorption_rate, time_utilization, retention_estimate
        )
        
        return {
            'efficiency_score': round(min(efficiency_score, 1.0), 3),
            'time_utilization': round(time_utilization, 3),
            'concept_absorption_rate': round(concept_absorption_rate, 2),
            'retention_estimate': round(retention_estimate, 3),
            'improvement_areas': improvement_areas,
            'efficiency_trend': efficiency_trend,
            'metrics_breakdown': {
                'total_reading_time': total_reading_time,
                'total_concepts_learned': total_concepts,
                'total_articles_read': total_articles,
                'engagement_actions': engagement_actions
            }
        }
    
    def _analyze_efficiency_trend(self, reading_history: List[Dict]) -> str:
        """分析效率趋势"""
        if len(reading_history) < 10:
            return 'insufficient_data'
        
        # 比较前半部分和后半部分的效率
        mid_point = len(reading_history) // 2
        early_reads = reading_history[:mid_point]
        recent_reads = reading_history[mid_point:]
        
        # 计算早期效率
        early_concepts = len(set(keyword for read in early_reads for keyword in read.get('keywords', [])))
        early_time = sum(read.get('reading_time', 0) for read in early_reads)
        early_efficiency = (early_concepts / early_time) if early_time > 0 else 0
        
        # 计算最近效率
        recent_concepts = len(set(keyword for read in recent_reads for keyword in read.get('keywords', [])))
        recent_time = sum(read.get('reading_time', 0) for read in recent_reads)
        recent_efficiency = (recent_concepts / recent_time) if recent_time > 0 else 0
        
        if recent_efficiency > early_efficiency * 1.2:
            return 'improving'
        elif recent_efficiency < early_efficiency * 0.8:
            return 'declining'
        else:
            return 'stable'
    
    def _identify_efficiency_improvements(self, absorption_rate: float, 
                                        time_utilization: float, 
                                        retention: float) -> List[str]:
        """识别效率改进点"""
        improvements = []
        
        if absorption_rate < 1.0:
            improvements.append('提高概念学习速度 - 尝试主动总结和记录关键点')
        
        if time_utilization < 0.7:
            improvements.append('提高阅读完成率 - 选择更合适难度的文章')
        
        if retention < 0.5:
            improvements.append('增强知识保留 - 多参与讨论和实践应用')
        
        if len(improvements) == 0:
            improvements.append('学习效率良好，可以尝试挑战更复杂的内容')
        
        return improvements[:3]
    
    # ========== 学习进度相关方法 ==========
    
    def _calculate_overall_progress(self, concept_progress: Dict) -> Dict[str, Any]:
        """计算整体学习进度"""
        if not concept_progress:
            return {'progress_percentage': 0, 'level': 'beginner', 'next_milestone': 100}
        
        total_concepts = concept_progress.get('total_concepts_encountered', 0)
        learning_velocity = concept_progress.get('learning_velocity', 0)
        
        # 基于概念数量和学习速度计算进度百分比
        progress_percentage = min(100, (total_concepts * 10 + learning_velocity * 20))
        
        # 确定学习级别
        if progress_percentage >= 80:
            level = 'expert'
        elif progress_percentage >= 60:
            level = 'advanced'
        elif progress_percentage >= 30:
            level = 'intermediate'
        else:
            level = 'beginner'
        
        return {
            'progress_percentage': progress_percentage,
            'level': level,
            'next_milestone': ((progress_percentage // 25) + 1) * 25,
            'concepts_to_next_level': max(0, 50 - total_concepts)
        }
    
    def _track_goal_progress(self, learning_goals: List[Dict], user_id: str) -> List[Dict[str, Any]]:
        """追踪学习目标进度"""
        # 简化实现 - 实际项目中会有更复杂的目标管理
        default_goals = [
            {'goal': '每周阅读5篇AI文章', 'target': 5, 'current': 3, 'progress': 0.6},
            {'goal': '掌握10个AI概念', 'target': 10, 'current': 7, 'progress': 0.7},
            {'goal': '完成度达到80%', 'target': 0.8, 'current': 0.75, 'progress': 0.94}
        ]
        
        return learning_goals if learning_goals else default_goals
    
    def _get_learning_milestones(self, user_id: str) -> List[Dict[str, Any]]:
        """获取学习里程碑"""
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        milestones = []
        
        # 阅读量里程碑
        article_count = len(reading_history)
        if article_count >= 100:
            milestones.append({'type': 'reading', 'achievement': '百篇阅读达人', 'unlocked': True})
        elif article_count >= 50:
            milestones.append({'type': 'reading', 'achievement': '五十篇里程碑', 'unlocked': True})
        elif article_count >= 10:
            milestones.append({'type': 'reading', 'achievement': '十篇起步', 'unlocked': True})
        
        # 连续阅读里程碑
        streak = self._calculate_reading_streak(reading_history)
        if streak >= 30:
            milestones.append({'type': 'streak', 'achievement': '月度坚持者', 'unlocked': True})
        elif streak >= 7:
            milestones.append({'type': 'streak', 'achievement': '周度坚持者', 'unlocked': True})
        
        return milestones
    
    def _suggest_next_steps(self, user_id: str) -> List[str]:
        """建议下一步学习方向"""
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        suggestions = []
        
        if len(reading_history) < 5:
            suggestions.append('建立定期阅读习惯，每天阅读1-2篇AI文章')
        elif len(reading_history) < 20:
            suggestions.append('扩展阅读领域，尝试不同类型的AI内容')
        else:
            suggestions.append('深入专业领域，关注前沿技术发展')
        
        suggestions.extend([
            '参与AI相关讨论和交流',
            '尝试实践项目应用所学知识',
            '关注行业专家和意见领袖'
        ])
        
        return suggestions[:3]
    
    # ========== 智能推荐相关方法 ==========
    
    def _recommend_articles(self, user_vector: Dict[str, float]) -> List[Dict[str, Any]]:
        """推荐文章"""
        # 基于用户兴趣向量推荐文章
        recommendations = [
            {'title': 'GPT-4最新应用案例分析', 'relevance': 0.95, 'source': '机器之心'},
            {'title': '计算机视觉在自动驾驶中的突破', 'relevance': 0.88, 'source': 'AI科技评论'},
            {'title': '大模型训练成本优化策略', 'relevance': 0.82, 'source': '新智元'}
        ]
        
        # 根据用户兴趣排序
        top_interests = sorted(user_vector.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return recommendations[:5]
    
    def _recommend_learning_content(self, user_vector: Dict[str, float]) -> List[Dict[str, Any]]:
        """推荐学习内容"""
        content_recommendations = [
            {'type': 'course', 'title': 'PyTorch深度学习实战', 'provider': 'Coursera', 'difficulty': 'intermediate'},
            {'type': 'tutorial', 'title': 'Transformer架构详解', 'provider': 'YouTube', 'difficulty': 'advanced'},
            {'type': 'paper', 'title': 'Attention Is All You Need', 'venue': 'NIPS 2017', 'difficulty': 'expert'}
        ]
        
        return content_recommendations[:3]
    
    def _recommend_experts_to_follow(self, user_vector: Dict[str, float]) -> List[Dict[str, Any]]:
        """推荐专家关注"""
        experts = [
            {'name': 'Andrew Ng', 'field': 'Machine Learning', 'platform': 'Twitter', 'followers': '2.8M'},
            {'name': 'Yann LeCun', 'field': 'Deep Learning', 'platform': 'LinkedIn', 'followers': '1.2M'},
            {'name': 'Fei-Fei Li', 'field': 'Computer Vision', 'platform': 'Twitter', 'followers': '800K'}
        ]
        
        return experts[:3]
    
    def _recommend_skill_development(self, user_vector: Dict[str, float]) -> List[str]:
        """推荐技能发展方向"""
        skills = [
            'Python机器学习编程',
            'Transformer模型应用',
            '数据可视化技能',
            'AI产品设计思维',
            '技术文档写作'
        ]
        
        return skills[:3]
    
    def _get_personalized_trending_topics(self, user_vector: Dict[str, float]) -> List[str]:
        """获取个性化热门话题"""
        trending_topics = [
            'GPT-4应用创新',
            '多模态AI发展',
            'AI安全与伦理',
            '边缘AI计算',
            '量子机器学习'
        ]
        
        return trending_topics[:5]
    
    def _calculate_recommendation_confidence(self, user_vector: Dict[str, float]) -> float:
        """计算推荐置信度"""
        if not user_vector:
            return 0.1
        
        # 基于用户数据丰富度计算置信度
        total_weight = sum(user_vector.values())
        confidence = min(1.0, total_weight / 10.0)  # 假设权重总和10为高置信度
        
        return round(confidence, 2)
    
    # ========== 行业脉动相关方法 ==========
    
    def _filter_trends_by_interests(self, user_interests: List[str]) -> List[Dict[str, Any]]:
        """根据兴趣过滤趋势"""
        all_trends = [
            {'topic': 'GPT-4 Turbo发布', 'relevance': 0.95, 'impact': 'high'},
            {'topic': '多模态AI突破', 'relevance': 0.88, 'impact': 'medium'},
            {'topic': 'AI芯片新进展', 'relevance': 0.75, 'impact': 'high'}
        ]
        
        return all_trends[:3]
    
    def _generate_personalized_insights(self, user_interests: List[str]) -> List[str]:
        """生成个性化洞察"""
        insights = [
            '大语言模型成本持续下降，企业应用门槛降低',
            '多模态AI将成为下一个竞争焦点',
            'AI安全问题日益重要，需要加强关注'
        ]
        
        return insights[:3]
    
    def _identify_investment_opportunities(self, user_interests: List[str]) -> List[Dict[str, Any]]:
        """识别投资机会"""
        opportunities = [
            {'sector': 'AI芯片', 'potential': 'high', 'timeframe': 'short-term'},
            {'sector': '自动驾驶', 'potential': 'medium', 'timeframe': 'long-term'},
            {'sector': 'AI医疗', 'potential': 'high', 'timeframe': 'medium-term'}
        ]
        
        return opportunities[:3]
    
    def _get_competitive_intelligence(self, user_interests: List[str]) -> Dict[str, Any]:
        """获取竞争情报"""
        return {
            'market_leaders': ['OpenAI', 'Google', 'Microsoft'],
            'emerging_players': ['Anthropic', 'Cohere', 'Stability AI'],
            'investment_trends': ['大模型基础设施', 'AI应用层创新', '垂直领域AI']
        }
    
    def _create_technology_radar(self, user_interests: List[str]) -> Dict[str, List[str]]:
        """创建技术雷达"""
        return {
            'adopt': ['Transformer架构', 'Pre-trained模型'],
            'trial': ['多模态融合', 'AI Agent框架'],
            'assess': ['量子机器学习', '神经符号AI'],
            'hold': ['传统机器学习', '规则引擎']
        }
    
    def _assess_industry_sentiment(self, user_interests: List[str]) -> Dict[str, Any]:
        """评估行业情绪"""
        return {
            'overall_sentiment': 'optimistic',
            'confidence_level': 0.85,
            'key_concerns': ['AI安全', '监管政策', '技术泡沫'],
            'growth_drivers': ['成本下降', '应用创新', '基础设施完善']
        }
    
    # ========== 成就系统相关方法 ==========
    
    def _check_reading_milestones(self, reading_history: List[Dict]) -> List[Dict[str, Any]]:
        """检查阅读里程碑"""
        milestones = []
        count = len(reading_history)
        
        milestones_config = [
            (1, '第一篇', 'bronze'),
            (10, '十篇达成', 'silver'), 
            (50, '五十篇里程碑', 'gold'),
            (100, '百篇阅读达人', 'platinum')
        ]
        
        for threshold, name, level in milestones_config:
            if count >= threshold:
                milestones.append({
                    'name': name,
                    'level': level,
                    'achieved': True,
                    'achievement_date': reading_history[threshold-1].get('timestamp', '') if len(reading_history) >= threshold else ''
                })
        
        return milestones
    
    def _check_streak_achievements(self, reading_history: List[Dict]) -> List[Dict[str, Any]]:
        """检查连续阅读成就"""
        streak = self._calculate_reading_streak(reading_history)
        achievements = []
        
        streak_config = [
            (3, '三天坚持', 'bronze'),
            (7, '一周坚持', 'silver'),
            (30, '一月坚持', 'gold'),
            (100, '百天坚持', 'diamond')
        ]
        
        for threshold, name, level in streak_config:
            if streak >= threshold:
                achievements.append({
                    'name': name,
                    'level': level,
                    'achieved': True,
                    'current_streak': streak
                })
        
        return achievements
    
    def _check_knowledge_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """检查知识徽章"""
        user_profile = self._load_user_profile(user_id)
        reading_history = user_profile.get('reading_history', [])
        
        # 统计不同领域的阅读量
        domain_counts = Counter()
        for read in reading_history:
            keywords = read.get('keywords', [])
            for keyword in keywords:
                domain = self._categorize_concept(keyword)
                domain_counts[domain] += 1
        
        badges = []
        for domain, count in domain_counts.most_common():
            if count >= 10:
                badges.append({
                    'domain': domain,
                    'level': 'expert' if count >= 20 else 'advanced',
                    'count': count
                })
        
        return badges[:5]
    
    def _check_exploration_awards(self, reading_history: List[Dict]) -> List[Dict[str, Any]]:
        """检查探索奖励"""
        # 统计阅读的不同来源
        sources = set()
        for read in reading_history:
            source = read.get('source', 'unknown')
            sources.add(source)
        
        awards = []
        if len(sources) >= 10:
            awards.append({'name': '信息探索者', 'description': f'阅读了{len(sources)}个不同来源'})
        elif len(sources) >= 5:
            awards.append({'name': '多源阅读', 'description': f'阅读了{len(sources)}个不同来源'})
        
        return awards
    
    def _check_engagement_honors(self, user_profile: Dict) -> List[Dict[str, Any]]:
        """检查参与度荣誉"""
        reading_history = user_profile.get('reading_history', [])
        
        engagement_count = sum(1 for read in reading_history 
                             if read.get('liked') or read.get('shared') or read.get('commented'))
        
        honors = []
        if engagement_count >= 50:
            honors.append({'name': '活跃参与者', 'level': 'gold'})
        elif engagement_count >= 20:
            honors.append({'name': '积极互动', 'level': 'silver'})
        elif engagement_count >= 5:
            honors.append({'name': '参与互动', 'level': 'bronze'})
        
        return honors
    
    def _suggest_next_achievements(self, user_profile: Dict) -> List[str]:
        """建议下一个成就目标"""
        reading_history = user_profile.get('reading_history', [])
        count = len(reading_history)
        
        suggestions = []
        
        # 基于当前进度建议下一个目标
        if count < 10:
            suggestions.append(f'再阅读{10-count}篇文章达到十篇里程碑')
        elif count < 50:
            suggestions.append(f'再阅读{50-count}篇文章达到五十篇里程碑')
        elif count < 100:
            suggestions.append(f'再阅读{100-count}篇文章成为百篇阅读达人')
        
        # 连续阅读建议
        streak = self._calculate_reading_streak(reading_history)
        if streak < 7:
            suggestions.append(f'连续阅读{7-streak}天达到一周坚持')
        elif streak < 30:
            suggestions.append(f'连续阅读{30-streak}天达到一月坚持')
        
        return suggestions[:3]
    
    def _calculate_achievement_level(self, total_score: int) -> str:
        """计算成就等级"""
        if total_score >= 1000:
            return 'Master'
        elif total_score >= 500:
            return 'Expert'
        elif total_score >= 200:
            return 'Advanced'
        elif total_score >= 50:
            return 'Intermediate'
        else:
            return 'Beginner'
    
    def _calculate_progress_to_next_level(self, total_score: int) -> Dict[str, Any]:
        """计算到下一等级的进度"""
        levels = [50, 200, 500, 1000]
        current_level = 0
        
        for i, threshold in enumerate(levels):
            if total_score >= threshold:
                current_level = i + 1
            else:
                break
        
        if current_level >= len(levels):
            return {'progress': 1.0, 'points_needed': 0, 'next_level': 'Master'}
        
        next_threshold = levels[current_level]
        previous_threshold = levels[current_level - 1] if current_level > 0 else 0
        
        progress = (total_score - previous_threshold) / (next_threshold - previous_threshold)
        points_needed = next_threshold - total_score
        
        level_names = ['Intermediate', 'Advanced', 'Expert', 'Master']
        next_level = level_names[current_level] if current_level < len(level_names) else 'Master'
        
        return {
            'progress': round(progress, 2),
            'points_needed': points_needed,
            'next_level': next_level
        }
    
    # ========== 社交洞察相关方法 ==========
    
    def _get_community_rank(self, user_id: str) -> Dict[str, Any]:
        """获取社区排名"""
        # 简化实现
        return {
            'rank': 156,
            'total_users': 10000,
            'percentile': 98.4,
            'category': 'reading_volume'
        }
    
    def _find_similar_users(self, user_id: str) -> List[Dict[str, Any]]:
        """寻找相似用户"""
        # 简化实现
        similar_users = [
            {'user_id': 'user_001', 'similarity': 0.92, 'common_interests': ['GPT', 'ML', 'CV']},
            {'user_id': 'user_002', 'similarity': 0.88, 'common_interests': ['AI', 'DL', 'NLP']},
            {'user_id': 'user_003', 'similarity': 0.85, 'common_interests': ['AI', 'GPT', 'Robotics']}
        ]
        
        return similar_users[:3]
    
    def _get_discussion_stats(self, user_id: str) -> Dict[str, Any]:
        """获取讨论统计"""
        return {
            'comments_made': 45,
            'discussions_started': 12,
            'upvotes_received': 128,
            'response_rate': 0.75
        }
    
    def _get_sharing_stats(self, user_id: str) -> Dict[str, Any]:
        """获取分享统计"""
        return {
            'articles_shared': 23,
            'shares_received': 67,
            'sharing_frequency': 0.15,
            'most_shared_topic': 'GPT应用'
        }
    
    def _calculate_influence_score(self, user_id: str) -> float:
        """计算影响力分数"""
        # 基于多个因素计算影响力
        discussion_stats = self._get_discussion_stats(user_id)
        sharing_stats = self._get_sharing_stats(user_id)
        
        influence = (
            discussion_stats['upvotes_received'] * 0.4 +
            sharing_stats['shares_received'] * 0.3 +
            discussion_stats['discussions_started'] * 0.2 +
            sharing_stats['articles_shared'] * 0.1
        ) / 100.0
        
        return round(min(influence, 1.0), 3)


class DashboardAnalytics:
    """仪表板分析工具"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
    
    def get_user_read_articles(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户已读文章"""
        # 这里需要实现从用户配置中获取已读文章列表
        # 然后从数据库中获取完整的文章信息
        return []
    
    def count_daily_reads(self, user_id: str) -> int:
        """统计今日阅读量"""
        # 简化实现
        return 5
    
    def calculate_reading_streak(self, user_id: str) -> int:
        """计算阅读连续天数"""
        # 简化实现
        return 7


# 使用示例
if __name__ == "__main__":
    # 测试个性化仪表板
    dashboard = PersonalDashboard()
    
    # 生成测试用户的仪表板数据
    test_user_id = "test_user_001"
    dashboard_data = dashboard.generate_dashboard_data(test_user_id)
    
    print("=== 个性化仪表板测试 ===")
    print(json.dumps(dashboard_data, ensure_ascii=False, indent=2))
    
    # 测试用户交互保存
    dashboard.save_user_interaction(
        test_user_id,
        "article_read",
        {
            "article_id": "test_article_001",
            "title": "AI技术最新进展",
            "reading_time": 120,
            "completion_rate": 0.8
        }
    )

