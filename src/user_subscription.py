import json
import os
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
from logging_config import get_logger
import hashlib

logger = get_logger(__name__)

class UserSubscription:
    """用户订阅管理系统"""
    
    def __init__(self, config_path: str = "user_configs"):
        self.config_path = config_path
        os.makedirs(config_path, exist_ok=True)
        
    def create_user(self, user_id: str, user_config: Dict) -> bool:
        """创建新用户配置"""
        try:
            config_file = os.path.join(self.config_path, f"{user_id}.json")
            
            # 默认配置
            default_config = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "active": True,
                
                # 兴趣标签配置
                "interest_tags": {
                    "ai_models": True,          # AI模型
                    "machine_learning": True,   # 机器学习
                    "deep_learning": True,      # 深度学习
                    "computer_vision": False,   # 计算机视觉
                    "nlp": True,               # 自然语言处理
                    "robotics": False,         # 机器人
                    "autonomous_driving": False, # 自动驾驶
                    "ai_chips": False,         # AI芯片
                    "ai_startups": True,       # AI创业公司
                    "ai_investment": True,     # AI投资
                    "ai_ethics": False,        # AI伦理
                    "ai_regulation": False,    # AI监管
                },
                
                # 关键词过滤
                "keyword_filters": {
                    "include_keywords": [],    # 必须包含的关键词
                    "exclude_keywords": [],    # 排除的关键词
                    "priority_keywords": [],   # 优先关键词（提升重要性）
                },
                
                # 来源偏好
                "source_preferences": {
                    "preferred_sources": [],   # 偏好的数据源
                    "blocked_sources": [],     # 屏蔽的数据源
                    "source_weights": {},      # 来源权重调整
                },
                
                # 推送设置
                "notification_settings": {
                    "enabled": True,
                    "min_importance_score": 0.7,  # 最低重要性阈值
                    "max_daily_items": 20,         # 每日最大推送数量
                    "preferred_times": ["08:00", "20:00"],  # 偏好推送时间
                    "template_preference": "detailed",       # 卡片模板偏好
                    "include_images": True,                  # 是否包含图片
                },
                
                # 阅读历史
                "reading_history": {
                    "read_articles": [],       # 已读文章URL
                    "liked_articles": [],      # 点赞文章
                    "shared_articles": [],     # 分享文章
                    "reading_time_preference": "fast",  # fast/detailed
                },
                
                # 个性化学习
                "learning_data": {
                    "click_keywords": {},      # 点击的关键词统计
                    "read_sources": {},        # 阅读来源统计
                    "engagement_score": 0.5,   # 参与度评分
                    "last_active": datetime.now().isoformat(),
                }
            }
            
            # 合并用户提供的配置
            merged_config = {**default_config, **user_config}
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(merged_config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Created user config: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return False
    
    def get_user_config(self, user_id: str) -> Optional[Dict]:
        """获取用户配置"""
        try:
            config_file = os.path.join(self.config_path, f"{user_id}.json")
            if not os.path.exists(config_file):
                return None
                
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            return config
            
        except Exception as e:
            logger.error(f"Error loading user config {user_id}: {e}")
            return None
    
    def update_user_config(self, user_id: str, updates: Dict) -> bool:
        """更新用户配置"""
        try:
            config = self.get_user_config(user_id)
            if not config:
                return False
            
            # 递归更新配置
            def deep_update(base_dict, update_dict):
                for key, value in update_dict.items():
                    if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                        deep_update(base_dict[key], value)
                    else:
                        base_dict[key] = value
            
            deep_update(config, updates)
            config["updated_at"] = datetime.now().isoformat()
            
            config_file = os.path.join(self.config_path, f"{user_id}.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Updated user config: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user config {user_id}: {e}")
            return False
    
    def filter_articles_for_user(self, user_id: str, articles: List[Dict]) -> List[Dict]:
        """根据用户偏好过滤文章"""
        config = self.get_user_config(user_id)
        if not config:
            return articles
        
        try:
            filtered_articles = []
            
            for article in articles:
                if self._should_include_article(article, config):
                    # 调整重要性评分
                    article = self._adjust_importance_score(article, config)
                    filtered_articles.append(article)
            
            # 按重要性排序
            filtered_articles.sort(key=lambda x: x.get('importance_score', 0), reverse=True)
            
            # 限制数量
            max_items = config['notification_settings']['max_daily_items']
            return filtered_articles[:max_items]
            
        except Exception as e:
            logger.error(f"Error filtering articles for user {user_id}: {e}")
            return articles
    
    def _should_include_article(self, article: Dict, config: Dict) -> bool:
        """判断是否应该包含某篇文章"""
        # 检查来源偏好
        source = article.get('source', '')
        if source in config['source_preferences']['blocked_sources']:
            return False
        
        # 检查最低重要性阈值
        importance = article.get('importance_score', 0)
        min_importance = config['notification_settings']['min_importance_score']
        if importance < min_importance:
            return False
        
        # 检查是否已读
        url = article.get('url', '')
        if url in config['reading_history']['read_articles']:
            return False
        
        # 检查兴趣标签
        if not self._matches_interest_tags(article, config['interest_tags']):
            return False
        
        # 检查关键词过滤
        if not self._matches_keyword_filters(article, config['keyword_filters']):
            return False
        
        return True
    
    def _matches_interest_tags(self, article: Dict, interest_tags: Dict) -> bool:
        """检查文章是否匹配用户兴趣标签"""
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        content = f"{title} {summary}"
        
        # 标签映射到关键词
        tag_keywords = {
            'ai_models': ['gpt', 'chatgpt', 'claude', 'llama', 'bert', '大模型', '语言模型'],
            'machine_learning': ['machine learning', '机器学习', 'ml', 'algorithm', '算法'],
            'deep_learning': ['deep learning', '深度学习', 'neural network', '神经网络'],
            'computer_vision': ['computer vision', '计算机视觉', 'image recognition', '图像识别'],
            'nlp': ['nlp', 'natural language', '自然语言', 'text processing'],
            'robotics': ['robot', '机器人', 'robotics', 'automation'],
            'autonomous_driving': ['autonomous', 'self-driving', '自动驾驶', 'tesla'],
            'ai_chips': ['chip', '芯片', 'gpu', 'nvidia', 'processor'],
            'ai_startups': ['startup', '创业', 'funding', '融资', 'venture'],
            'ai_investment': ['investment', '投资', 'funding', '融资', 'ipo'],
            'ai_ethics': ['ethics', '伦理', 'bias', 'fairness'],
            'ai_regulation': ['regulation', '监管', 'policy', '政策', 'law'],
        }
        
        matched_tags = []
        for tag, enabled in interest_tags.items():
            if enabled and tag in tag_keywords:
                keywords = tag_keywords[tag]
                if any(keyword in content for keyword in keywords):
                    matched_tags.append(tag)
        
        # 至少匹配一个启用的标签
        return len(matched_tags) > 0
    
    def _matches_keyword_filters(self, article: Dict, filters: Dict) -> bool:
        """检查文章是否匹配关键词过滤器"""
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        content = f"{title} {summary}"
        
        # 必须包含的关键词
        include_keywords = filters.get('include_keywords', [])
        if include_keywords:
            if not any(keyword.lower() in content for keyword in include_keywords):
                return False
        
        # 排除的关键词
        exclude_keywords = filters.get('exclude_keywords', [])
        if exclude_keywords:
            if any(keyword.lower() in content for keyword in exclude_keywords):
                return False
        
        return True
    
    def _adjust_importance_score(self, article: Dict, config: Dict) -> Dict:
        """根据用户偏好调整重要性评分"""
        original_score = article.get('importance_score', 0.5)
        adjusted_score = original_score
        
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        content = f"{title} {summary}"
        
        # 优先关键词加分
        priority_keywords = config['keyword_filters'].get('priority_keywords', [])
        for keyword in priority_keywords:
            if keyword.lower() in content:
                adjusted_score += 0.1
        
        # 偏好来源加分
        source = article.get('source', '')
        preferred_sources = config['source_preferences'].get('preferred_sources', [])
        if source in preferred_sources:
            adjusted_score += 0.15
        
        # 来源权重调整
        source_weights = config['source_preferences'].get('source_weights', {})
        if source in source_weights:
            weight = source_weights[source]
            adjusted_score = adjusted_score * weight
        
        # 个性化学习调整
        learning_data = config.get('learning_data', {})
        click_keywords = learning_data.get('click_keywords', {})
        
        for keyword, click_count in click_keywords.items():
            if keyword.lower() in content and click_count > 5:
                adjusted_score += 0.05
        
        # 确保评分在合理范围内
        article['importance_score'] = max(0, min(1.0, adjusted_score))
        article['original_importance_score'] = original_score
        
        return article
    
    def record_user_action(self, user_id: str, action: str, article_url: str, metadata: Dict = None) -> bool:
        """记录用户行为"""
        try:
            config = self.get_user_config(user_id)
            if not config:
                return False
            
            timestamp = datetime.now().isoformat()
            
            if action == 'read':
                if article_url not in config['reading_history']['read_articles']:
                    config['reading_history']['read_articles'].append(article_url)
            elif action == 'like':
                if article_url not in config['reading_history']['liked_articles']:
                    config['reading_history']['liked_articles'].append(article_url)
            elif action == 'share':
                if article_url not in config['reading_history']['shared_articles']:
                    config['reading_history']['shared_articles'].append(article_url)
            
            # 更新学习数据
            if metadata and 'keywords' in metadata:
                click_keywords = config['learning_data']['click_keywords']
                for keyword in metadata['keywords']:
                    click_keywords[keyword] = click_keywords.get(keyword, 0) + 1
            
            config['learning_data']['last_active'] = timestamp
            
            return self.update_user_config(user_id, config)
            
        except Exception as e:
            logger.error(f"Error recording user action {action} for {user_id}: {e}")
            return False
    
    def get_all_active_users(self) -> List[str]:
        """获取所有活跃用户ID"""
        active_users = []
        
        try:
            for filename in os.listdir(self.config_path):
                if filename.endswith('.json'):
                    user_id = filename[:-5]  # 移除.json后缀
                    config = self.get_user_config(user_id)
                    
                    if config and config.get('active', True):
                        active_users.append(user_id)
            
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
        
        return active_users
    
    def cleanup_old_data(self, days: int = 30) -> None:
        """清理旧的阅读历史数据"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for user_id in self.get_all_active_users():
                config = self.get_user_config(user_id)
                if not config:
                    continue
                
                # 清理阅读历史（保留最近的）
                read_articles = config['reading_history']['read_articles']
                if len(read_articles) > 1000:  # 只保留最近1000条
                    config['reading_history']['read_articles'] = read_articles[-1000:]
                
                # 清理点击关键词统计（保留高频词汇）
                click_keywords = config['learning_data']['click_keywords']
                filtered_keywords = {k: v for k, v in click_keywords.items() if v >= 3}
                config['learning_data']['click_keywords'] = filtered_keywords
                
                self.update_user_config(user_id, config)
            
            logger.info(f"Cleaned up user data older than {days} days")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class DefaultUserManager:
    """默认用户管理器，用于向后兼容"""
    
    def __init__(self):
        self.subscription_manager = UserSubscription()
        self.default_user_id = "default_user"
        
        # 如果默认用户不存在，创建一个
        if not self.subscription_manager.get_user_config(self.default_user_id):
            self.subscription_manager.create_user(self.default_user_id, {})
    
    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """使用默认用户配置过滤文章"""
        return self.subscription_manager.filter_articles_for_user(self.default_user_id, articles)
    
    def update_preferences(self, updates: Dict) -> bool:
        """更新默认用户偏好"""
        return self.subscription_manager.update_user_config(self.default_user_id, updates)

