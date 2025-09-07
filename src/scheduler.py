import schedule
import requests
import qrcode
from io import BytesIO
import os
import time
import logging
from datetime import datetime
from typing import Dict, List
from crawler import AINewsCrawler
from summarizer import ContentSummarizer
from card_generator import NewsCardGenerator
from dotenv import load_dotenv
from logging_config import setup_logging, get_logger
from notifier import Notifier
from user_subscription import DefaultUserManager, UserSubscription
import re

# 加载环境变量
load_dotenv()

class NewsScheduler:
    """新闻采集调度器"""
    
    def __init__(self):
        self.crawler = AINewsCrawler()
        self.summarizer = ContentSummarizer(
            api_key=os.getenv('DEEPSEEK_API_KEY'),
            base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        )
        self.card_generator = NewsCardGenerator()
        self.notifier = Notifier()
        
        # 用户订阅管理
        self.user_manager = DefaultUserManager()
        self.subscription_manager = UserSubscription()
        
        # 多模板支持
        self.enable_multi_template = os.getenv('ENABLE_MULTI_TEMPLATE', 'false').lower() == 'true'
        self.default_template = os.getenv('DEFAULT_CARD_TEMPLATE', 'detailed')
        
        # 标准化日志
        setup_logging()
        self.logger = get_logger(__name__)
    
    def daily_news_collection(self):
        """每日新闻采集任务"""
        # 记录任务开始时间，用于统一时间戳
        task_start_time = datetime.now()
        
        try:
            self.logger.info(f"开始每日新闻采集任务 - {task_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 1. 爬取文章
            self.logger.info("正在爬取AI行业新闻...")
            articles = self.crawler.crawl_all_sources()
            self.logger.info(f"爬取到 {len(articles)} 篇文章")
            
            # 2. 去重和过滤
            articles = self.crawler.deduplicate_articles(articles)
            articles = self.crawler.filter_recent_articles(articles, hours=24)
            self.logger.info(f"去重后剩余 {len(articles)} 篇文章")
            
            # 3. 生成摘要
            self.logger.info("正在生成文章摘要...")
            summaries = self.summarizer.batch_summarize(articles[:20])  # 限制处理数量
            self.logger.info(f"生成了 {len(summaries)} 个摘要")
            
            # 4. 个性化过滤（使用默认用户配置）
            self.logger.info("正在应用个性化过滤...")
            filtered_summaries = self.user_manager.filter_articles(summaries)
            self.logger.info(f"过滤后剩余 {len(filtered_summaries)} 个摘要")
            
            # 4.5. 预加载图片（提升卡片生成速度）
            try:
                from image_loader import get_image_loader
                image_loader = get_image_loader()
                self.logger.info("正在预加载图片...")
                image_loader.preload_images(filtered_summaries[:10])
                self.logger.info("图片预加载完成")
            except Exception as e:
                self.logger.warning(f"图片预加载失败，将在生成卡片时单独加载: {e}")
            
            # 5. 生成卡片（使用统一时间戳）
            card_paths = []
            if self.enable_multi_template:
                self.logger.info("正在使用多模板生成新闻卡片...")
                # 生成多种模板的卡片
                multi_template_results = self.card_generator.batch_generate_multi_template_cards(
                    filtered_summaries[:5], ['compact', 'detailed', 'image_text'], task_start_time
                )
                # 收集所有卡片路径
                for template_name, paths in multi_template_results.items():
                    card_paths.extend(paths)
                self.logger.info(f"生成了 {len(card_paths)} 张多模板卡片")
            else:
                self.logger.info("正在生成新闻卡片...")
                card_paths = self.card_generator.batch_generate_cards(
                    filtered_summaries[:10], self.default_template, task_start_time
                )
                self.logger.info(f"生成了 {len(card_paths)} 张卡片")
            
            # 6. 保存数据（使用统一时间戳）
            self._save_daily_data(filtered_summaries, card_paths, task_start_time)

            task_duration = (datetime.now() - task_start_time).total_seconds()
            self.logger.info(f"每日新闻采集任务完成，耗时 {task_duration:.1f} 秒")

            # 7. 个性化推送到微信（使用任务开始时间）
            try:
                title = f"AI 行业热点日报 {task_start_time.strftime('%Y-%m-%d %H:%M')}"
                md = self._build_markdown_digest(filtered_summaries, task_start_time)
                pushed = self.notifier.send_serverchan(title, md)
                if pushed:
                    self.logger.info("已通过服务器酱推送到微信")
                else:
                    self.logger.warning("服务器酱推送未成功（可能未配置 SERVERCHAN_SENDKEY）")
            except Exception as e:
                self.logger.error(f"推送到微信失败: {e}")
            
        except Exception as e:
            self.logger.error(f"每日新闻采集任务失败: {e}")
    
    def _save_daily_data(self, summaries, card_paths, task_time=None):
        """保存每日数据"""
        # 使用传入的时间戳或当前时间
        if task_time is None:
            task_time = datetime.now()
        
        # 创建目录（使用任务开始时间的日期）
        today = task_time.strftime('%Y-%m-%d')
        daily_dir = f"daily_news/{today}"
        os.makedirs(daily_dir, exist_ok=True)
        
        # 保存摘要数据（添加任务时间戳）
        import json
        save_data = {
            "task_time": task_time.isoformat(),
            "generation_count": len(summaries),
            "card_count": len(card_paths),
            "summaries": summaries
        }
        
        with open(f"{daily_dir}/summaries.json", 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # 移动卡片到今日目录
        for card_path in card_paths:
            if os.path.exists(card_path):
                filename = os.path.basename(card_path)
                new_path = f"{daily_dir}/{filename}"
                os.rename(card_path, new_path)

    def _build_markdown_digest(self, summaries, task_time=None):
        """构建用于推送的 Markdown 文本（取前5条，优化为微信内易读排版）"""
        # 使用传入的时间戳或当前时间
        if task_time is None:
            task_time = datetime.now()
        def preprocess_for_wechat(text: str) -> str:
            """专为微信优化的排版预处理：
            - 标签词加粗并独立成行（使用更强制的换行）
            - 支持微信的Markdown渲染特性
            - 确保在移动端正确显示
            """
            if not text:
                return ""
            s = text
            
            # 定义标准的标签词（与summarizer.py中的格式保持一致）
            labels = [
                "核心观点", "关键技术", "行业影响", "重要结论",
                # 保留一些常见的变体以兼容历史数据
                "核心发现", "重要数据", "技术对比", "关键词", "结论", "摘要", 
                "技术与公司", "关键技术与企业动态", "技术特点", "市场影响", 
                "投资动态", "产品特色", "应用场景", "发展趋势", "监管动态"
            ]
            
            # 1) 先处理标签词格式化 - 在标签词前换行，并将标签词加粗
            for label in labels:
                # 匹配标签词+冒号的模式，在前面加换行，将标签词加粗
                # 避免重复处理已经加粗的标签词
                # 微信需要更强制的换行，使用三个换行符确保显示效果
                pattern = r"(?<!^)(?<!\*\*)\s*(" + re.escape(label) + r")([：:])"
                replacement = r"\n\n\n**\1**\2"
                s = re.sub(pattern, replacement, s)
            
            # 2) 处理冒号后直接跟短横线的情况 - 短横线换到下一行
            s = re.sub(r"([：:])\s*-", r"\1\n\n-", s)
            
            # 3) 处理序号 - 在非行首的序号前换行，微信需要更明显的换行
            # 处理阿拉伯数字+点号或顿号的格式：1. 2. 或 1、2、
            s = re.sub(r"(?<!^)\s*(?=(\d+[\.、]))", lambda m: "\n\n" if m.start() != 0 else "", s)
            
            # 处理中文数字+括号的格式：1）2）3）
            # 先处理分号后的数字编号，确保换行
            s = re.sub(r"([；;])\s*(\d+）)", r"\1\n\n\2", s)
            # 处理非行首的数字+右括号，在前面加换行
            s = re.sub(r"(?<!^)(?<![\n])\s*(\d+）)", r"\n\n\1", s)
            
            # 4) 处理短横线条目 - 在非行首的短横线前换行
            s = re.sub(r"(?<!^)\s*-(?=\s)", r"\n\n-", s)
            s = re.sub(r"(?<=[:：，。；、\s])-(?=\S)", r"\n\n-", s)
            
            # 5) 处理圆点列表
            s = re.sub(r"(?<!^)\s*○\s*", r"\n\n○ ", s)
            
            # 6) 规范化空白 - 清理多余的空白和换行
            s = re.sub(r"\n\s+", "\n", s)  # 去除行首空格
            s = re.sub(r"\n{4,}", "\n\n\n", s)  # 限制最多三个换行（适应微信）
            
            # 微信特殊处理：在标签词前后增加空行分隔
            # 确保在微信中正确换行显示
            s = re.sub(r'\*\*([^*]+)\*\*:', r'\n\n**\1**:\n', s)
            
            # 最终清理：确保段落间有足够分隔
            s = re.sub(r'\n{1,2}(?=\*\*)', '\n\n\n', s)  # 标签词前强制空行
            s = re.sub(r'\n{5,}', '\n\n\n', s)  # 限制最多三个换行
            
            return s.strip()

        def proxy_image(url: str) -> str:
            """根据环境变量决定是否使用 images.weserv.nl 代理并限制宽度。"""
            if not url or not url.startswith('http'):
                return url
            if os.getenv('IMAGE_PROXY_ENABLED', 'false').lower() not in ('1', 'true', 'yes', 'y'):
                return url
            width = os.getenv('IMAGE_PROXY_WIDTH', '800')
            # 去掉 scheme，以适配 weserv 要求
            no_scheme = url.replace('https://', '').replace('http://', '')
            return f"https://images.weserv.nl/?url={no_scheme}&w={width}"

        lines = [
            f"## 今日 AI 热点速览",
            f"*生成时间: {task_time.strftime('%Y-%m-%d %H:%M')}*",
            "",
        ]

        # 主列表展示前10条
        for i, s in enumerate(summaries[:10], start=1):
            title = s.get('original_title', '无标题').strip()
            source = s.get('source', '未知来源').strip()
            url = s.get('url', '').strip()
            summary = s.get('summary', '')
            image = (s.get('image') or "").strip()

            processed = preprocess_for_wechat(summary)

            # 标题行（编号 + 可点击链接）
            lines.append(f"{i}. [{title}]({url})")
            # 元信息行（来源）
            lines.append(f"来源：`{source}`")
            # 摘要行（逐行引用块，保留换行与条目）
            if processed:
                block = "> " + "\n> ".join(l or "" for l in processed.splitlines())
                lines.append(block)
            # 图片预览（若存在）
            if image.startswith('http'):
                proxied = proxy_image(image)
                lines.append(f"\n![]({proxied})\n")
            # 分隔
            lines.append("\n---\n")

        # 更多：仅列出标题与链接，避免过长
        more = summaries[10:20]
        if more:
            lines.append("\n### 更多")
            for idx, s in enumerate(more, start=11):
                title = s.get('original_title', '无标题').strip()
                url = s.get('url', '').strip()
                lines.append(f"{idx}. [{title}]({url})")

        return "\n".join(lines)
    
    def start_scheduler(self):
        """启动调度器"""
        # 每天 08:00 和 20:00 执行（间隔约 12 小时）
        schedule.every().day.at("08:00").do(self.daily_news_collection)
        schedule.every().day.at("20:00").do(self.daily_news_collection)
        
        self.logger.info("新闻采集调度器已启动")
        self.logger.info("每日 08:00 与 20:00 自动执行新闻采集与推送任务")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def run_once(self):
        """立即执行一次采集任务（用于测试）"""
        self.daily_news_collection()
    
    def create_user_subscription(self, user_id: str, preferences: Dict = None) -> bool:
        """创建用户订阅"""
        if preferences is None:
            preferences = {}
        
        return self.subscription_manager.create_user(user_id, preferences)
    
    def update_user_preferences(self, user_id: str, updates: Dict) -> bool:
        """更新用户偏好设置"""
        return self.subscription_manager.update_user_config(user_id, updates)
    
    def get_personalized_news(self, user_id: str, max_items: int = 10) -> List[Dict]:
        """获取个性化新闻推荐"""
        try:
            # 获取最新文章
            articles = self.crawler.crawl_all_sources()
            articles = self.crawler.deduplicate_articles(articles)
            articles = self.crawler.filter_recent_articles(articles, hours=24)
            
            # 生成摘要
            summaries = self.summarizer.batch_summarize(articles[:30])
            
            # 个性化过滤
            filtered_summaries = self.subscription_manager.filter_articles_for_user(user_id, summaries)
            
            return filtered_summaries[:max_items]
            
        except Exception as e:
            self.logger.error(f"Error getting personalized news for {user_id}: {e}")
            return []
    
    def generate_personalized_cards(self, user_id: str, template_preference: str = None) -> List[str]:
        """为用户生成个性化卡片"""
        try:
            # 获取个性化新闻
            summaries = self.get_personalized_news(user_id, max_items=10)
            
            if not summaries:
                return []
            
            # 获取用户模板偏好
            user_config = self.subscription_manager.get_user_config(user_id)
            if user_config and not template_preference:
                template_preference = user_config['notification_settings']['template_preference']
            
            template_preference = template_preference or self.default_template
            
            # 生成卡片
            card_paths = self.card_generator.batch_generate_cards(summaries, template_preference)
            
            return card_paths
            
        except Exception as e:
            self.logger.error(f"Error generating personalized cards for {user_id}: {e}")
            return []
    
    def record_user_interaction(self, user_id: str, action: str, article_url: str, metadata: Dict = None) -> bool:
        """记录用户交互行为"""
        return self.subscription_manager.record_user_action(user_id, action, article_url, metadata)
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """获取用户统计信息"""
        try:
            config = self.subscription_manager.get_user_config(user_id)
            if not config:
                return {}
            
            reading_history = config['reading_history']
            learning_data = config['learning_data']
            
            stats = {
                'total_read_articles': len(reading_history['read_articles']),
                'total_liked_articles': len(reading_history['liked_articles']),
                'total_shared_articles': len(reading_history['shared_articles']),
                'engagement_score': learning_data['engagement_score'],
                'top_keywords': sorted(learning_data['click_keywords'].items(), 
                                     key=lambda x: x[1], reverse=True)[:10],
                'last_active': learning_data['last_active'],
                'account_created': config['created_at']
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting statistics for {user_id}: {e}")
            return {}

if __name__ == "__main__":
    scheduler = NewsScheduler()
    
    # 可以选择立即运行一次或启动定时任务
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        scheduler.run_once()
    else:
        scheduler.start_scheduler()
