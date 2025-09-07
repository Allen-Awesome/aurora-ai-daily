from PIL import Image, ImageDraw, ImageFont
import qrcode
from typing import Dict, Tuple, List
from abc import ABC, abstractmethod
import os
import re
from datetime import datetime

class CardTemplate(ABC):
    """卡片模板基类"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.margin = 40
        self.qr_size = 120
        
        # 通用颜色配置
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
    
    @abstractmethod
    def generate_card(self, summary_data: Dict, font_loader, task_time=None) -> Image:
        """生成卡片的抽象方法"""
        pass
    
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
            box_size=8,
            border=3,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((self.qr_size, self.qr_size))
        return qr_img

class CompactTemplate(CardTemplate):
    """紧凑型模板 - 适合快速浏览"""
    
    def __init__(self):
        super().__init__(width=600, height=400)
        self.qr_size = 80
        self.margin = 20
    
    def generate_card(self, summary_data: Dict, font_loader, task_time=None) -> Image:
        img = Image.new('RGB', (self.width, self.height), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # 字体
        title_font = font_loader(20)
        content_font = font_loader(12)
        meta_font = font_loader(10)
        
        # 重要性指示条
        importance_color = self._get_importance_color(summary_data['importance_score'])
        draw.rectangle([0, 0, 6, self.height], fill=importance_color)
        
        # 标题（限制行数）
        title = summary_data['original_title']
        title_lines = self._wrap_text(title, title_font, self.width - 2*self.margin - self.qr_size - 20)[:2]
        
        y_pos = self.margin
        for line in title_lines:
            draw.text((self.margin, y_pos), line, fill=self.colors['text'], font=title_font)
            y_pos += 25
        
        # 来源信息（使用统一时间戳）
        if task_time is None:
            task_time = datetime.now()
        source_text = f"{summary_data['source']} | {task_time.strftime('%m-%d %H:%M')}"
        draw.text((self.margin, y_pos + 5), source_text, 
                 fill=self.colors['text_light'], font=meta_font)
        
        # 摘要（压缩版本）
        summary_short = summary_data['summary'][:150] + "..." if len(summary_data['summary']) > 150 else summary_data['summary']
        summary_lines = self._wrap_text(summary_short, content_font, self.width - 2*self.margin - self.qr_size - 20)[:4]
        
        y_pos += 35
        for line in summary_lines:
            draw.text((self.margin, y_pos), line, fill=self.colors['text'], font=content_font)
            y_pos += 16
        
        # 关键词（横向显示）
        if summary_data['keywords']:
            keywords_text = " | ".join(summary_data['keywords'][:3])
            draw.text((self.margin, self.height - 40), keywords_text, 
                     fill=self.colors['secondary'], font=meta_font)
        
        # 二维码
        qr_img = self._generate_qr_code(summary_data['url'])
        qr_position = (self.width - self.qr_size - self.margin, self.margin)
        img.paste(qr_img, qr_position)
        
        return img
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """简单文本换行"""
        if not text:
            return [""]
        
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines

class DetailedTemplate(CardTemplate):
    """详细型模板 - 信息丰富，适合深度阅读"""
    
    def __init__(self):
        super().__init__(width=900, height=700)
        self.margin = 50
        self.qr_size = 140
    
    def generate_card(self, summary_data: Dict, font_loader, task_time=None) -> Image:
        img = Image.new('RGB', (self.width, self.height), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # 字体
        title_font = font_loader(32)
        subtitle_font = font_loader(18)
        content_font = font_loader(16)
        meta_font = font_loader(14)
        
        # 背景装饰
        draw.rectangle([0, 0, self.width, 60], fill=self.colors['accent'])
        
        # 重要性指示
        importance_color = self._get_importance_color(summary_data['importance_score'])
        draw.circle((self.width - 30, 30), 15, fill=importance_color)
        
        # 标题区域
        title = summary_data['original_title']
        title_lines = self._wrap_text(title, title_font, self.width - 2*self.margin)
        
        y_pos = 80
        for line in title_lines:
            draw.text((self.margin, y_pos), line, fill=self.colors['primary'], font=title_font)
            y_pos += 40
        
        # 元信息栏
        draw.rectangle([self.margin, y_pos + 10, self.width - self.margin, y_pos + 50], 
                      fill=self.colors['border'])
        
        # 使用统一时间戳
        if task_time is None:
            task_time = datetime.now()
        source_text = f"来源: {summary_data['source']}"
        time_text = f"时间: {task_time.strftime('%Y-%m-%d %H:%M')}"
        score_text = f"重要性: {'★' * int(summary_data['importance_score'] * 5)}"
        
        draw.text((self.margin + 10, y_pos + 20), source_text, fill=self.colors['text'], font=meta_font)
        draw.text((self.margin + 250, y_pos + 20), time_text, fill=self.colors['text'], font=meta_font)
        draw.text((self.margin + 500, y_pos + 20), score_text, fill=self.colors['text'], font=meta_font)
        
        # 摘要内容区域
        y_pos += 80
        summary_text = self._preprocess_text(summary_data['summary'])
        content_lines = self._wrap_paragraphs(summary_text, content_font, 
                                            self.width - 2*self.margin - self.qr_size - 30)
        
        for line in content_lines:
            if y_pos > self.height - 120:
                break
            draw.text((self.margin, y_pos), line, fill=self.colors['text'], font=content_font)
            y_pos += 24
        
        # 关键词标签区域
        if summary_data['keywords']:
            y_pos = self.height - 80
            draw.text((self.margin, y_pos), "关键词:", fill=self.colors['primary'], font=subtitle_font)
            
            tag_x = self.margin
            tag_y = y_pos + 25
            for keyword in summary_data['keywords'][:5]:
                tag_width = meta_font.getbbox(keyword)[2] + 20
                draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_width, tag_y + 25], 
                                     radius=5, fill=self.colors['secondary'])
                draw.text((tag_x + 10, tag_y + 5), keyword, fill='white', font=meta_font)
                tag_x += tag_width + 10
                
                if tag_x > self.width - self.qr_size - 100:
                    break
        
        # 二维码区域
        qr_img = self._generate_qr_code(summary_data['url'])
        qr_position = (self.width - self.qr_size - self.margin, self.margin + 60)
        img.paste(qr_img, qr_position)
        
        draw.text((self.width - self.qr_size - self.margin, 
                  self.margin + self.qr_size + 75), 
                 "扫码阅读原文", fill=self.colors['text_light'], font=meta_font)
        
        return img
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """详细模板的文本换行"""
        if not text:
            return [""]
        
        lines = []
        current_line = ""
        
        for char in text:
            test_line = current_line + char
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _wrap_paragraphs(self, text: str, font, max_width: int) -> list:
        """段落换行处理"""
        output = []
        for raw_line in text.splitlines():
            raw_line = raw_line.rstrip()
            if not raw_line:
                output.append("")
                continue
            output.extend(self._wrap_text(raw_line, font, max_width))
        return output
    
    def _preprocess_text(self, text: str) -> str:
        """优化排版预处理（与推送内容保持一致）"""
        if not text:
            return ""
        s = text
        
        # 定义需要特殊格式化的标签词
        labels = [
            "行业影响", "重要结论", "重要数据", "核心观点", "核心发现", 
            "关键技术", "技术对比", "关键词", "结论", "摘要", "技术与公司",
            "关键技术与企业动态", "技术特点", "市场影响", "投资动态",
            "产品特色", "应用场景", "发展趋势", "监管动态"
        ]
        
        # 1) 处理标签词格式化 - 在标签词前换行
        for label in labels:
            # 避免重复处理的简单模式（卡片中不使用markdown加粗）
            pattern = r"(?<!^)\s*(" + re.escape(label) + r")([：:])"
            replacement = r"\n\n\1\2"
            s = re.sub(pattern, replacement, s)
        
        # 2) 处理冒号后直接跟短横线的情况
        s = re.sub(r"([：:])\s*-", r"\1\n-", s)
        
        # 3) 处理序号独立成行
        # 处理阿拉伯数字+点号或顿号的格式：1. 2. 或 1、2、
        s = re.sub(r"(?<!^)\s*(?=(\d+[\.、]))", lambda m: "\n" if m.start() != 0 else "", s)
        
        # 处理中文数字+括号的格式：1）2）3）
        s = re.sub(r"([；;])\s*(\d+）)", r"\1\n\n\2", s)
        s = re.sub(r"(?<!^)(?<![\n])\s*(\d+）)", r"\n\n\1", s)
        
        # 4) 处理短横线条目
        s = re.sub(r"(?<!^)\s*-(?=\s)", r"\n-", s)
        s = re.sub(r"(?<=[:：，。；、\s])-(?=\S)", r"\n-", s)
        
        # 5) 处理圆点列表
        s = re.sub(r"(?<!^)\s*○\s*", r"\n○ ", s)
        
        # 6) 规范化空白
        s = re.sub(r"\n\s+", "\n", s)
        s = re.sub(r"\n{3,}", "\n\n", s)
        
        return s.strip()

class ImageTextTemplate(CardTemplate):
    """图文型模板 - 突出图片展示"""
    
    def __init__(self):
        super().__init__(width=800, height=800)
        self.image_height = 250
    
    def generate_card(self, summary_data: Dict, font_loader, task_time=None) -> Image:
        img = Image.new('RGB', (self.width, self.height), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # 字体
        title_font = font_loader(24)
        content_font = font_loader(14)
        meta_font = font_loader(12)
        
        current_y = 0
        
        # 如果有图片，使用优化的图片加载器
        if summary_data.get('image') and summary_data['image'].startswith('http'):
            try:
                from image_loader import get_image_loader
                
                # 使用优化的图片加载器（带缓存和重试）
                image_loader = get_image_loader()
                article_img = image_loader.load_image(
                    summary_data['image'], 
                    target_size=(self.width, self.image_height)
                )
                
                if article_img:
                    # 居中显示图片
                    img_x = (self.width - article_img.width) // 2
                    img.paste(article_img, (img_x, current_y))
                    current_y += article_img.height
                    
                    # 图片下方加阴影分割线
                    draw.rectangle([0, current_y, self.width, current_y + 3], 
                                 fill=self.colors['border'])
                    current_y += 20
                else:
                    # 图片加载失败，显示占位区域
                    draw.rectangle([0, current_y, self.width, current_y + self.image_height], 
                                 fill=self.colors['border'])
                    draw.text((self.width//2 - 50, current_y + self.image_height//2), 
                             "图片加载失败", fill=self.colors['text_light'], font=content_font)
                    current_y += self.image_height + 20
                    
            except Exception as e:
                # 如果图片加载器出错，显示占位区域
                draw.rectangle([0, current_y, self.width, current_y + self.image_height], 
                             fill=self.colors['border'])
                draw.text((self.width//2 - 50, current_y + self.image_height//2), 
                         "图片服务异常", fill=self.colors['text_light'], font=content_font)
                current_y += self.image_height + 20
        
        # 重要性指示条
        importance_color = self._get_importance_color(summary_data['importance_score'])
        draw.rectangle([0, current_y, 8, self.height], fill=importance_color)
        
        # 标题区域
        title = summary_data['original_title']
        title_lines = self._wrap_text(title, title_font, self.width - 2*self.margin - self.qr_size - 20)
        
        current_y += self.margin
        for line in title_lines:
            draw.text((self.margin, current_y), line, fill=self.colors['primary'], font=title_font)
            current_y += 30
        
        # 来源和时间（使用统一时间戳）
        if task_time is None:
            task_time = datetime.now()
        source_text = f"来源: {summary_data['source']}"
        time_text = f"时间: {task_time.strftime('%Y-%m-%d %H:%M')}"
        
        current_y += 10
        draw.text((self.margin, current_y), source_text, fill=self.colors['text_light'], font=meta_font)
        current_y += 20
        draw.text((self.margin, current_y), time_text, fill=self.colors['text_light'], font=meta_font)
        current_y += 30
        
        # 摘要内容
        summary_text = summary_data['summary']
        content_lines = self._wrap_text(summary_text, content_font, 
                                      self.width - 2*self.margin - self.qr_size - 20)
        
        for line in content_lines:
            if current_y > self.height - 100:
                break
            draw.text((self.margin, current_y), line, fill=self.colors['text'], font=content_font)
            current_y += 20
        
        # 关键词（底部）
        if summary_data['keywords']:
            keywords_text = "关键词: " + " | ".join(summary_data['keywords'][:4])
            draw.text((self.margin, self.height - 60), keywords_text, 
                     fill=self.colors['secondary'], font=meta_font)
        
        # 二维码（右上角）
        qr_img = self._generate_qr_code(summary_data['url'])
        qr_position = (self.width - self.qr_size - self.margin, 
                      self.image_height + 40 if summary_data.get('image') else self.margin)
        img.paste(qr_img, qr_position)
        
        draw.text((self.width - self.qr_size - self.margin, 
                  qr_position[1] + self.qr_size + 10), 
                 "扫码阅读", fill=self.colors['text_light'], font=meta_font)
        
        return img
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """图文模板的文本换行"""
        if not text:
            return [""]
        
        lines = []
        words = text.replace('\n', ' ').split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines

# 模板注册表
TEMPLATES = {
    'compact': CompactTemplate,
    'detailed': DetailedTemplate,
    'image_text': ImageTextTemplate,
}

def get_template(template_name: str = 'detailed') -> CardTemplate:
    """获取指定的卡片模板"""
    template_class = TEMPLATES.get(template_name, DetailedTemplate)
    return template_class()
