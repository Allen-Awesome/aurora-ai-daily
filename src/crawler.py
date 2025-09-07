import requests
from bs4 import BeautifulSoup
import feedparser
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict
from logging_config import get_logger
import os

# newspaper3k 是可选依赖，缺失时不阻塞主流程
try:
    from newspaper import Article  # type: ignore
    _HAS_NEWSPAPER = True
except Exception:
    Article = None  # type: ignore
    _HAS_NEWSPAPER = False

logger = get_logger(__name__)

class AINewsCrawler:
    """AI行业新闻爬虫"""
    
    def __init__(self):
        # 每源抓取上限可通过环境变量调整
        self.max_per_source = int(os.getenv('MAX_ARTICLES_PER_SOURCE', '10'))

        # RSS/Feed 源
        self.sources = {
            # 英文媒体
            'techcrunch_ai': 'https://techcrunch.com/category/artificial-intelligence/feed/',
            'venturebeat_ai': 'https://venturebeat.com/ai/feed/',
            'arxiv_ai': 'http://export.arxiv.org/rss/cs.AI',
            'towards_data_science': 'https://towardsdatascience.com/feed',
            'ai_news': 'https://artificialintelligence-news.com/feed/',
            'mit_tech_review': 'https://www.technologyreview.com/topic/artificial-intelligence/feed/',

            # 中文媒体 - 原有
            'qbitai': 'https://www.qbitai.com/feed',              # 量子位
            'jiqizhixin': 'https://www.jiqizhixin.com/rss',       # 机器之心
            'zhidx': 'https://zhidx.com/feed',                    # 智东西
            'infoq_cn': 'https://www.infoq.cn/feed',              # InfoQ 中文站
            '36kr': 'https://36kr.com/feed',                      # 36氪全站（后续在代码中过滤 AI 相关）

            # 中文媒体 - 新增
            'xinzhiyuan': 'https://mp.weixin.qq.com/rss?__biz=MzI3MTA0MTk1MA==',  # 新智元
            'ai_tech_review': 'https://www.jiqizhixin.com/rss',   # AI科技评论（使用机器之心RSS作为备选）
            'leiphone_ai': 'https://www.leiphone.com/category/ai/feed',  # 雷锋网AI
            'pingwest': 'https://www.pingwest.com/feed',          # PingWest品玩
            'ifanr': 'https://www.ifanr.com/feed',                # 爱范儿
            'geekpark': 'https://www.geekpark.net/rss',           # 极客公园
            'tmtpost': 'https://www.tmtpost.com/rss.xml',         # 钛媒体
            'ithome_ai': 'https://www.ithome.com/rss/',           # IT之家
            'cnbeta_ai': 'https://www.cnbeta.com/backend/rss/',   # cnBeta
            'oschina': 'https://www.oschina.net/news/rss',       # 开源中国
            
            # 专业AI媒体
            'aibase': 'https://www.aibase.com/rss',               # AIBase（假设RSS地址）
            'deeptech': 'https://www.deeptech.cn/rss',            # DeepTech深科技

            # 社区
            'hn_ai': 'https://hnrss.org/newest?q=ai',             # Hacker News AI 关键词
            'reddit_ml': 'https://www.reddit.com/r/MachineLearning/.rss',
            'reddit_artificial': 'https://www.reddit.com/r/Artificial/.rss',
            'reddit_localllama': 'https://www.reddit.com/r/LocalLLaMA/.rss',
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def crawl_rss_feed(self, url: str, source_name: str) -> List[Dict]:
        """爬取RSS源"""
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[: self.max_per_source]:
                image_url = self._extract_image_url(entry, entry.get('link', ''))
                article_data = {
                    'title': entry.title,
                    'url': entry.link,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'source': source_name,
                    'crawl_time': datetime.now().isoformat(),
                    'image': image_url or ""
                }
                # 对综合性媒体做AI关键词过滤，仅保留AI相关内容
                general_media = ['36kr', 'pingwest', 'ifanr', 'geekpark', 'tmtpost', 'ithome_ai', 'cnbeta_ai', 'oschina']
                if source_name in general_media:
                    text = (entry.get('title', '') + ' ' + entry.get('summary', '')).lower()
                    ai_keywords = [
                        ' ai ', 'ai ', '人工智能', '机器学习', '深度学习', '神经网络', 
                        '大模型', 'chatgpt', 'gpt', 'llm', '自动驾驶', '计算机视觉',
                        'opencv', 'pytorch', 'tensorflow', '算法', 'nlp', '自然语言',
                        '智能', '机器人', '语音识别', '图像识别', '数据挖掘'
                    ]
                    # 检查是否包含任何AI相关关键词
                    has_ai_content = any(keyword in text for keyword in ai_keywords)
                    if not has_ai_content:
                        continue
                articles.append(article_data)
                
            logger.info(f"RSS fetched: {source_name} -> {len(articles)} items")
            return articles
        except Exception as e:
            logger.error(f"Error crawling {source_name}: {e}", exc_info=True)
            return []
    
    def extract_full_content(self, url: str) -> str:
        """提取文章全文"""
        # 优先使用 newspaper3k，如不可用则返回空串（后续摘要将使用 RSS 的 summary）
        if not _HAS_NEWSPAPER or Article is None:
            logger.info("newspaper3k 未安装，跳过全文提取")
            return ""
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}", exc_info=True)
            return ""
    
    def crawl_github_trending(self) -> List[Dict]:
        """爬取GitHub AI相关热门项目"""
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                'q': 'artificial intelligence OR machine learning OR deep learning',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            projects = []
            for repo in data.get('items', []):
                project_data = {
                    'title': repo['name'],
                    'url': repo['html_url'],
                    'description': repo.get('description', ''),
                    'stars': repo['stargazers_count'],
                    'language': repo.get('language', ''),
                    'source': 'github_trending',
                    'crawl_time': datetime.now().isoformat(),
                    'image': ""
                }
                projects.append(project_data)
                
            return projects
        except Exception as e:
            logger.error(f"Error crawling GitHub trending: {e}", exc_info=True)
            return []
    
    def crawl_all_sources(self) -> List[Dict]:
        """爬取所有数据源"""
        all_articles = []
        
        # 爬取RSS源
        for source_name, url in self.sources.items():
            articles = self.crawl_rss_feed(url, source_name)
            all_articles.extend(articles)
            time.sleep(1)  # 避免请求过快
        
        # 爬取GitHub热门项目
        github_projects = self.crawl_github_trending()
        all_articles.extend(github_projects)
        
        return all_articles
    
    def filter_recent_articles(self, articles: List[Dict], hours: int = 24) -> List[Dict]:
        """过滤最近的文章"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_articles = []
        
        for article in articles:
            # 简单的时间过滤逻辑，实际需要更复杂的日期解析
            recent_articles.append(article)
            
        return recent_articles
    
    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """去重文章"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title_lower = article['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)
                
        return unique_articles

    def _extract_image_url(self, entry, fallback_url: str) -> str:
        """从 feed 条目中尽可能获取图片 URL，若无则尝试抓取页面 og:image。
        仅返回 http(s) 的直链，避免 base64 或相对路径。
        """
        # 1) 常见字段：media_content / media_thumbnail
        try:
            media = entry.get('media_content') or []
            if media and isinstance(media, list):
                for m in media:
                    url = (m or {}).get('url')
                    if url and url.startswith('http'):
                        return url
        except Exception:
            pass
        try:
            thumbs = entry.get('media_thumbnail') or []
            if thumbs and isinstance(thumbs, list):
                for m in thumbs:
                    url = (m or {}).get('url')
                    if url and url.startswith('http'):
                        return url
        except Exception:
            pass

        # 2) enclosure 链接
        try:
            for link in entry.get('links', []) or []:
                if link.get('rel') == 'enclosure':
                    url = link.get('href')
                    if url and url.startswith('http') and any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        return url
        except Exception:
            pass

        # 3) 抓取页面 og:image / twitter:image
        try:
            page_url = fallback_url
            if page_url:
                resp = requests.get(page_url, headers=self.headers, timeout=8)
                if resp.status_code == 200:
                    html = resp.text
                    soup = BeautifulSoup(html, 'html.parser')
                    for prop in ['og:image', 'twitter:image']:
                        tag = soup.find('meta', attrs={'property': prop}) or soup.find('meta', attrs={'name': prop})
                        if tag:
                            url = tag.get('content')
                            if url and url.startswith('http'):
                                return url
        except Exception:
            pass

        return ""
