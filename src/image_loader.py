import os
import hashlib
import time
from io import BytesIO
from typing import Optional, Dict, List
from PIL import Image
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging_config import get_logger

logger = get_logger(__name__)

class ImageLoader:
    """优化的图片加载器 - 解决图片加载慢的问题"""
    
    def __init__(self):
        self.cache_dir = "image_cache"
        self.max_cache_age = 24 * 3600  # 24小时缓存
        self.session = self._create_session()
        self._ensure_cache_dir()
        
        # 配置参数
        self.timeout = int(os.getenv('IMAGE_LOAD_TIMEOUT', '20'))  # 20秒超时
        self.max_retries = int(os.getenv('IMAGE_MAX_RETRIES', '3'))  # 最大重试3次
        self.max_workers = int(os.getenv('IMAGE_MAX_WORKERS', '5'))  # 并发下载5个
        self.max_image_size = int(os.getenv('MAX_IMAGE_SIZE_MB', '10')) * 1024 * 1024  # 10MB限制
        
        # 图片代理配置
        self.proxy_enabled = os.getenv('IMAGE_PROXY_ENABLED', 'true').lower() in ('1', 'true', 'yes', 'y')
        self.proxy_width = os.getenv('IMAGE_PROXY_WIDTH', '800')
        self.proxy_quality = os.getenv('IMAGE_PROXY_QUALITY', '80')
        
    def _create_session(self) -> requests.Session:
        """创建优化的请求会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # 连接池配置
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # 手动处理重试
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_path(self, url: str) -> str:
        """获取缓存文件路径"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.cache")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(cache_path):
            return False
        
        file_age = time.time() - os.path.getmtime(cache_path)
        return file_age < self.max_cache_age
    
    def _apply_image_proxy(self, url: str) -> str:
        """应用图片代理优化"""
        if not self.proxy_enabled or not url.startswith('http'):
            return url
        
        # 使用 images.weserv.nl 代理服务
        no_scheme = url.replace('https://', '').replace('http://', '')
        proxy_url = f"https://images.weserv.nl/?url={no_scheme}&w={self.proxy_width}&q={self.proxy_quality}&output=webp"
        
        logger.debug(f"应用图片代理: {url} -> {proxy_url}")
        return proxy_url
    
    def _download_image_with_retry(self, url: str) -> Optional[bytes]:
        """带重试机制的图片下载"""
        original_url = url
        url = self._apply_image_proxy(url)
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"下载图片 (尝试 {attempt + 1}/{self.max_retries}): {url}")
                
                # 设置动态超时 - 重试时增加超时时间
                timeout = self.timeout + (attempt * 5)
                
                response = self.session.get(url, timeout=timeout, stream=True)
                response.raise_for_status()
                
                # 检查内容大小
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.max_image_size:
                    logger.warning(f"图片过大，跳过: {url} ({content_length} bytes)")
                    return None
                
                # 流式下载，避免内存问题
                content = BytesIO()
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded += len(chunk)
                        if downloaded > self.max_image_size:
                            logger.warning(f"图片下载过程中超出大小限制: {url}")
                            return None
                        content.write(chunk)
                
                logger.info(f"图片下载成功: {url} ({downloaded} bytes)")
                return content.getvalue()
                
            except requests.exceptions.Timeout:
                last_error = f"超时 (尝试 {attempt + 1})"
                logger.warning(f"图片下载超时: {url} (尝试 {attempt + 1}/{self.max_retries})")
                
            except requests.exceptions.ConnectionError:
                last_error = f"连接错误 (尝试 {attempt + 1})"
                logger.warning(f"图片下载连接错误: {url} (尝试 {attempt + 1}/{self.max_retries})")
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    logger.warning(f"图片不存在 (404): {url}")
                    return None
                last_error = f"HTTP错误: {e.response.status_code}"
                logger.warning(f"图片下载HTTP错误: {url} - {e}")
                
            except Exception as e:
                last_error = f"未知错误: {str(e)}"
                logger.warning(f"图片下载异常: {url} - {e}")
            
            # 重试前等待
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                time.sleep(wait_time)
        
        logger.error(f"图片下载失败，已重试 {self.max_retries} 次: {original_url} - {last_error}")
        return None
    
    def load_image(self, url: str, target_size: tuple = None) -> Optional[Image.Image]:
        """加载单张图片（带缓存）"""
        if not url or not url.startswith('http'):
            return None
        
        cache_path = self._get_cache_path(url)
        
        # 检查缓存
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    img = Image.open(BytesIO(f.read()))
                    logger.debug(f"从缓存加载图片: {url}")
                    
                    if target_size:
                        img.thumbnail(target_size, Image.Resampling.LANCZOS)
                    
                    return img
            except Exception as e:
                logger.warning(f"缓存图片损坏，重新下载: {url} - {e}")
                os.remove(cache_path)
        
        # 下载图片
        image_data = self._download_image_with_retry(url)
        if not image_data:
            return None
        
        try:
            # 保存到缓存
            with open(cache_path, 'wb') as f:
                f.write(image_data)
            
            # 创建Image对象
            img = Image.open(BytesIO(image_data))
            
            # 转换为RGB（避免RGBA等格式问题）
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            if target_size:
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            logger.info(f"图片处理完成: {url} -> {img.size}")
            return img
            
        except Exception as e:
            logger.error(f"图片处理失败: {url} - {e}")
            # 删除损坏的缓存
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None
    
    def load_images_batch(self, image_urls: List[str], target_size: tuple = None) -> Dict[str, Optional[Image.Image]]:
        """批量并行加载图片"""
        if not image_urls:
            return {}
        
        results = {}
        
        # 过滤有效URL
        valid_urls = [url for url in image_urls if url and url.startswith('http')]
        
        if not valid_urls:
            return results
        
        logger.info(f"开始并行下载 {len(valid_urls)} 张图片...")
        start_time = time.time()
        
        # 并行下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任务
            future_to_url = {
                executor.submit(self.load_image, url, target_size): url 
                for url in valid_urls
            }
            
            # 收集结果
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    image = future.result()
                    results[url] = image
                except Exception as e:
                    logger.error(f"并行图片加载异常: {url} - {e}")
                    results[url] = None
        
        download_time = time.time() - start_time
        success_count = sum(1 for img in results.values() if img is not None)
        
        logger.info(f"批量图片加载完成: {success_count}/{len(valid_urls)} 成功，耗时 {download_time:.2f}s")
        
        return results
    
    def preload_images(self, summaries: List[Dict]):
        """预加载文章图片"""
        image_urls = []
        for summary in summaries:
            image_url = summary.get('image')
            if image_url and image_url.startswith('http'):
                image_urls.append(image_url)
        
        if not image_urls:
            return
        
        logger.info(f"开始预加载 {len(image_urls)} 张图片...")
        self.load_images_batch(image_urls, target_size=(800, 400))
    
    def clear_cache(self, max_age_hours: int = 72):
        """清理过期缓存"""
        if not os.path.exists(self.cache_dir):
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleared_count = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                file_path = os.path.join(self.cache_dir, filename)
                if current_time - os.path.getmtime(file_path) > max_age_seconds:
                    try:
                        os.remove(file_path)
                        cleared_count += 1
                    except Exception as e:
                        logger.warning(f"清理缓存失败: {file_path} - {e}")
        
        if cleared_count > 0:
            logger.info(f"清理了 {cleared_count} 个过期缓存文件")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        if not os.path.exists(self.cache_dir):
            return {"files": 0, "size_mb": 0}
        
        file_count = 0
        total_size = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                file_path = os.path.join(self.cache_dir, filename)
                file_count += 1
                total_size += os.path.getsize(file_path)
        
        return {
            "files": file_count,
            "size_mb": round(total_size / (1024 * 1024), 2)
        }

# 全局图片加载器实例
_image_loader = None

def get_image_loader() -> ImageLoader:
    """获取全局图片加载器实例"""
    global _image_loader
    if _image_loader is None:
        _image_loader = ImageLoader()
    return _image_loader

