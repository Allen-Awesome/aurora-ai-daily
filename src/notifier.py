import os
import requests
from typing import Optional
from logging_config import get_logger

logger = get_logger(__name__)

class Notifier:
    """封装第三方通知渠道，目前支持服务器酱·Turbo"""

    def __init__(self, sendkey: Optional[str] = None):
        self.sendkey = sendkey or os.getenv("SERVERCHAN_SENDKEY")

    def send_serverchan(self, title: str, desp_md: str) -> bool:
        """通过服务器酱·Turbo发送通知。
        文档: https://sct.ftqq.com/
        desp_md 支持 Markdown。
        """
        if not self.sendkey:
            logger.warning("SERVERCHAN_SENDKEY 未配置，跳过推送")
            return False
        url = f"https://sctapi.ftqq.com/{self.sendkey}.send"
        data = {
            "title": title,
            "desp": desp_md,
        }
        try:
            # 添加重试机制和SSL配置
            session = requests.Session()
            session.verify = False  # 临时禁用SSL验证以解决连接问题
            
            for attempt in range(3):
                try:
                    r = session.post(url, data=data, timeout=15)
                    if r.status_code == 200:
                        logger.info("ServerChan 推送成功")
                        return True
                    logger.warning(f"ServerChan 推送失败 (尝试 {attempt+1}/3): {r.status_code} {r.text}")
                except requests.exceptions.SSLError as ssl_e:
                    logger.warning(f"SSL错误 (尝试 {attempt+1}/3): {ssl_e}")
                    if attempt == 2:  # 最后一次尝试
                        raise ssl_e
                except requests.exceptions.RequestException as req_e:
                    logger.warning(f"请求错误 (尝试 {attempt+1}/3): {req_e}")
                    if attempt == 2:
                        raise req_e
            
            logger.error("ServerChan 推送失败: 所有重试均失败")
            return False
        except Exception as e:
            logger.error(f"ServerChan 请求异常: {e}", exc_info=True)
            return False
