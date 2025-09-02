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
            r = requests.post(url, data=data, timeout=10)
            if r.status_code == 200:
                logger.info("ServerChan 推送成功")
                return True
            logger.error(f"ServerChan 推送失败: {r.status_code} {r.text}")
            return False
        except Exception as e:
            logger.error(f"ServerChan 请求异常: {e}", exc_info=True)
            return False
