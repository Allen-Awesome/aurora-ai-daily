from PIL import Image, ImageDraw, ImageFont
import qrcode
from typing import Dict
import textwrap
from datetime import datetime
import os
from logging_config import get_logger
from typing import Optional

class NewsCardGenerator:
    """新闻卡片生成器"""
    
    def __init__(self):
        self.card_width = 800
        self.card_height = 600
        self.margin = 40
        self.qr_size = 120
        self.logger = get_logger(__name__)
        
        # 颜色配置
        self.colors = {
            'background': '#FFFFFF',
            'primary': '#2E3440',
            'secondary': '#5E81AC',
            'accent': '#88C0D0',
            'text': '#2E3440',
            'text_light': '#4C566A',
            'border': '#E5E9F0',
            'high_importance': '#BF616A',
            'medium_importance': '#EBCB8B',
            'low_importance': '#A3BE8C'
        }
    
    def _resolve_font_path(self) -> Optional[str]:
        """选择支持中英文的字体路径。
        优先级：环境变量 FONT_PATH -> 常见系统字体 -> None(回退默认字体)
        """
        env_path = os.getenv("FONT_PATH")
        if env_path and os.path.exists(env_path):
            return env_path
        candidates = [
            # Ubuntu GitHub Runner 常见 Noto CJK 路径
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJKSC-Regular.otf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.ttf",
            # 中文常用开源字体
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            # Windows 常见路径（如在本地运行）
            os.path.expandvars(r"C:\\Windows\\Fonts\\msyh.ttc"),  # 微软雅黑
            os.path.expandvars(r"C:\\Windows\\Fonts\\simhei.ttf"),  # 黑体
        ]
        for p in candidates:
            if p and os.path.exists(p):
                return p
        return None

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        path = self._resolve_font_path()
        if path:
            try:
                return ImageFont.truetype(path, size)
            except Exception as e:
                self.logger.warning(f"Failed to load font at {path}: {e}")
        # 回退
        self.logger.warning("Falling back to default PIL font (may cause tofu for CJK)")
        return ImageFont.load_default()

    def create_card(self, summary_data: Dict) -> str:
        """创建新闻卡片"""
        # 创建画布
        img = Image.new('RGB', (self.card_width, self.card_height), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # 加载支持 CJK 的字体（避免中文方块/乱码）
        title_font = self._load_font(28)
        content_font = self._load_font(16)
        meta_font = self._load_font(12)
        
        # 绘制边框
        draw.rectangle([0, 0, self.card_width-1, self.card_height-1], 
                      outline=self.colors['border'], width=2)
        
        # 绘制重要性指示条
        importance_color = self._get_importance_color(summary_data['importance_score'])
        draw.rectangle([0, 0, 8, self.card_height], fill=importance_color)
        
        # 绘制标题
        title = summary_data['original_title']
        wrapped_title = self._wrap_text(title, title_font, self.card_width - 2*self.margin - self.qr_size - 20)
        
        y_pos = self.margin
        for line in wrapped_title:
            draw.text((self.margin, y_pos), line, fill=self.colors['text'], font=title_font)
            y_pos += 35
        
        # 绘制来源和时间
        source_text = f"来源: {summary_data['source']}"
        time_text = f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        draw.text((self.margin, y_pos + 10), source_text, 
                 fill=self.colors['text_light'], font=meta_font)
        draw.text((self.margin, y_pos + 30), time_text, 
                 fill=self.colors['text_light'], font=meta_font)
        
        # 绘制摘要内容
        summary_text = summary_data['summary']
        wrapped_summary = self._wrap_text(summary_text, content_font, 
                                        self.card_width - 2*self.margin - self.qr_size - 20)
        
        y_pos += 70
        for line in wrapped_summary:
            if y_pos > self.card_height - 100:  # 避免文字超出卡片
                break
            draw.text((self.margin, y_pos), line, fill=self.colors['text'], font=content_font)
            y_pos += 22
        
        # 绘制关键词标签
        if summary_data['keywords']:
            keywords_text = "关键词: " + " | ".join(summary_data['keywords'][:3])
            draw.text((self.margin, self.card_height - 60), keywords_text, 
                     fill=self.colors['secondary'], font=meta_font)
        
        # 生成并添加二维码
        qr_img = self._generate_qr_code(summary_data['url'])
        qr_position = (self.card_width - self.qr_size - self.margin, self.margin)
        img.paste(qr_img, qr_position)
        
        # 二维码说明文字
        draw.text((self.card_width - self.qr_size - self.margin, 
                  self.margin + self.qr_size + 10), 
                 "扫码阅读原文", fill=self.colors['text_light'], font=meta_font)
        
        # 保存图片
        filename = f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(summary_data['url']) % 10000}.png"
        filepath = os.path.join("generated_cards", filename)
        
        # 确保目录存在
        os.makedirs("generated_cards", exist_ok=True)
        
        img.save(filepath, "PNG", quality=95)
        self.logger.info(f"Card saved: {filepath}")
        return filepath
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """文字换行处理"""
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _get_importance_color(self, score: float) -> str:
        """根据重要性评分获取颜色"""
        if score >= 0.8:
            return self.colors['high_importance']
        elif score >= 0.6:
            return self.colors['medium_importance']
        else:
            return self.colors['low_importance']
    
    def _generate_qr_code(self, url: str) -> Image:
        """生成二维码"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((self.qr_size, self.qr_size))
        
        return qr_img
    
    def batch_generate_cards(self, summaries: list) -> list:
        """批量生成卡片"""
        card_paths = []
        
        for summary in summaries:
            try:
                card_path = self.create_card(summary)
                card_paths.append(card_path)
            except Exception as e:
                self.logger.error(f"Error generating card for {summary['original_title']}: {e}", exc_info=True)
                continue
        
        return card_paths
