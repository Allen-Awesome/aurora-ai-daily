import schedule
import requests
import qrcode
from io import BytesIO
import os
import time
import logging
from datetime import datetime
from crawler import AINewsCrawler
from summarizer import ContentSummarizer
from card_generator import NewsCardGenerator
from dotenv import load_dotenv
from logging_config import setup_logging, get_logger
from notifier import Notifier

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
        
        # 标准化日志
        setup_logging()
        self.logger = get_logger(__name__)
    
    def daily_news_collection(self):
        """每日新闻采集任务"""
        try:
            self.logger.info("开始每日新闻采集任务")
            
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
            
            # 4. 生成卡片
            self.logger.info("正在生成新闻卡片...")
            card_paths = self.card_generator.batch_generate_cards(summaries[:10])  # 生成前10个重要的
            self.logger.info(f"生成了 {len(card_paths)} 张卡片")
            
            # 5. 保存数据（这里可以添加数据库存储逻辑）
            self._save_daily_data(summaries, card_paths)

            self.logger.info("每日新闻采集任务完成")

            # 6. 推送到微信（服务器酱·Turbo）
            try:
                title = f"AI 行业热点日报 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                md = self._build_markdown_digest(summaries)
                pushed = self.notifier.send_serverchan(title, md)
                if pushed:
                    self.logger.info("已通过服务器酱推送到微信")
                else:
                    self.logger.warning("服务器酱推送未成功（可能未配置 SERVERCHAN_SENDKEY）")
            except Exception as e:
                self.logger.error(f"推送到微信失败: {e}")
            
        except Exception as e:
            self.logger.error(f"每日新闻采集任务失败: {e}")
    
    def _save_daily_data(self, summaries, card_paths):
        """保存每日数据"""
        # 创建今日目录
        today = datetime.now().strftime('%Y-%m-%d')
        daily_dir = f"daily_news/{today}"
        os.makedirs(daily_dir, exist_ok=True)
        
        # 保存摘要数据
        import json
        with open(f"{daily_dir}/summaries.json", 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=2)
        
        # 移动卡片到今日目录
        for card_path in card_paths:
            if os.path.exists(card_path):
                filename = os.path.basename(card_path)
                new_path = f"{daily_dir}/{filename}"
                os.rename(card_path, new_path)

    def _build_markdown_digest(self, summaries):
        """构建用于推送的 Markdown 文本（取前5条，优化为微信内易读排版）"""
        def one_line(text: str) -> str:
            return " ".join((text or "").split())  # 去掉换行与多余空格

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
            "",
        ]

        # 主列表展示前10条
        for i, s in enumerate(summaries[:10], start=1):
            title = s.get('original_title', '无标题').strip()
            source = s.get('source', '未知来源').strip()
            url = s.get('url', '').strip()
            summary = s.get('summary', '')
            image = (s.get('image') or "").strip()

            short = one_line(summary)  # 显示完整摘要，不再截断

            # 标题行（编号 + 可点击链接）
            lines.append(f"{i}. [{title}]({url})")
            # 元信息行（来源）
            lines.append(f"来源：`{source}`")
            # 摘要行（引用块更易读）
            lines.append(f"> {short}")
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

if __name__ == "__main__":
    scheduler = NewsScheduler()
    
    # 可以选择立即运行一次或启动定时任务
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        scheduler.run_once()
    else:
        scheduler.start_scheduler()
