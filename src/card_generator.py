from PIL import Image, ImageDraw, ImageFont
import qrcode
from typing import Dict
import textwrap
from datetime import datetime
import os
from logging_config import get_logger
from typing import Optional
import re
from card_templates import get_template, TEMPLATES

class NewsCardGenerator:
    """新闻卡片生成器"""
    
    def __init__(self, template_name: str = None):
        # 原有配置保持兼容
        self.card_width = 800
        self.card_height = 600
        self.margin = 40
        self.qr_size = 120
        self.logger = get_logger(__name__)
        
        # 模板配置
        self.template_name = template_name or os.getenv('CARD_TEMPLATE', 'detailed')
        self.template = get_template(self.template_name)
        
        # 颜色配置（保持向后兼容）
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

    def create_card(self, summary_data: Dict, template_override: str = None, task_time: datetime = None) -> str:
        """创建新闻卡片（支持模板选择）"""
        # 使用传入的时间戳或当前时间
        if task_time is None:
            task_time = datetime.now()
            
        # 选择模板
        template_to_use = template_override or self.template_name
        
        # 如果指定了不同的模板，临时切换
        if template_override and template_override != self.template_name:
            template = get_template(template_override)
        else:
            template = self.template
        
        # 使用模板生成卡片（传递时间戳）
        img = template.generate_card(summary_data, self._load_font, task_time)
        
        # 保存图片（使用统一时间戳）
        filename = f"card_{task_time.strftime('%Y%m%d_%H%M%S')}_{hash(summary_data['url']) % 10000}.png"
        filepath = os.path.join("generated_cards", filename)
        
        # 确保目录存在
        os.makedirs("generated_cards", exist_ok=True)
        
        img.save(filepath, "PNG", quality=95)
        self.logger.info(f"Card saved using {template_to_use} template: {filepath}")
        return filepath
    
    def create_card_legacy(self, summary_data: Dict) -> str:
        """创建新闻卡片（原有实现，保持向后兼容）"""
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
        
        # 绘制摘要内容（预处理：冒号、序号、短横线独立成行）
        summary_text = self._preprocess_text(summary_data['summary'])
        wrapped_summary = self._wrap_paragraphs(summary_text, content_font,
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
        """按宽度换行，兼容中英文。优先在空格与标点处分行。"""
        if not text:
            return [""]
        preferred_breaks = set(" ，。；：、,.;:!?）)]】》>\u3002\uFF1A\uFF0C\uFF1B\uFF01\uFF1F")
        lines = []
        buf = ""
        last_break_idx = -1
        for i, ch in enumerate(text):
            candidate = buf + ch
            bbox = font.getbbox(candidate)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                buf = candidate
                if ch == ' ' or ch in preferred_breaks:
                    last_break_idx = len(buf) - 1
                continue
            # 超宽，需要换行
            if last_break_idx >= 0:
                # 在最近的优选断点处分行
                lines.append(buf[: last_break_idx + 1].rstrip())
                # 将剩余部分作为下一行起始
                remainder = buf[last_break_idx + 1 :].lstrip()
                buf = remainder + ch
            else:
                # 没有可用断点，强制按当前字符前换行
                if buf:
                    lines.append(buf)
                buf = ch
            last_break_idx = -1
        if buf:
            lines.append(buf)
        return lines

    def _wrap_paragraphs(self, text: str, font, max_width: int) -> list:
        """对段落进行逐段换行，保持预处理后的结构。"""
        output = []
        for raw_line in text.splitlines():
            raw_line = raw_line.rstrip()
            if not raw_line:
                output.append("")
                continue
            output.extend(self._wrap_text(raw_line, font, max_width))
        return output

    def _preprocess_text(self, text: str) -> str:
        """根据要求优化排版：
        - 含冒号的提示词独立成行（在提示词前断行，但提示词与其后的内容同一行）
        - 序号(1. / 1、)独立成行
        - 短横线(-)作为条目独立成行
        """
        if not text:
            return ""
        s = text
        # 1) 在常见提示词（如 行业影响/重要结论/核心发现/关键技术/关键词 等）前换行
        labels = [
            "行业影响", "重要结论", "重要数据", "核心观点", "核心发现", "关键技术", "结论", "摘要", "关键词"
        ]
        label_pat = r"(?<!^)\s*(?=(?:" + "|".join(labels) + r")[：:])"
        s = re.sub(label_pat, "\n", s)
        # 紧跟标签后的冒号若直接连接短横线，令短横线换到下一行作为条目起始
        s = re.sub(r"([：:])\s*-", r"\1\n-", s)
        # 2) 在非行首出现的编号前换行，如 1. 2. 或 1、2、
        s = re.sub(r"(?<!^)\s*(?=(\d+[\.、]))", lambda m: "\n" if m.start() != 0 else "", s)
        # 3) 在非行首出现的短横线条目前换行（允许无空格，如 -实验…）
        # 前一个字符需是分隔符，避免切断英文连字符
        s = re.sub(r"(?<!^) (?=)", "", s)  # no-op spacer to keep patch distinct
        s = re.sub(r"(?<!^) (?=)", "", s)  # no-op
        s = re.sub(r"(?<!^)\s*-(?=\s)", r"\n-", s)  # 原有规则（有空格的情况）
        s = re.sub(r"(?<=[:：，。；、\s])-(?=\S)", r"\n-", s)  # 无空格直接接文字的情况
        # 4) 规范多余空白
        s = re.sub(r"\n\s+", "\n", s)
        return s.strip()
    
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
    
    def batch_generate_cards(self, summaries: list, template_override: str = None, task_time: datetime = None) -> list:
        """批量生成卡片"""
        card_paths = []
        
        for summary in summaries:
            try:
                card_path = self.create_card(summary, template_override, task_time)
                card_paths.append(card_path)
            except Exception as e:
                self.logger.error(f"Error generating card for {summary['original_title']}: {e}", exc_info=True)
                continue
        
        return card_paths
    
    def batch_generate_multi_template_cards(self, summaries: list, templates: list = None, task_time: datetime = None) -> dict:
        """使用多个模板批量生成卡片"""
        if templates is None:
            templates = ['compact', 'detailed', 'image_text']
        
        results = {}
        
        for template_name in templates:
            try:
                self.logger.info(f"Generating cards using {template_name} template...")
                template_paths = []
                
                for summary in summaries:
                    try:
                        card_path = self.create_card(summary, template_name, task_time)
                        template_paths.append(card_path)
                    except Exception as e:
                        self.logger.error(f"Error generating {template_name} card for {summary['original_title']}: {e}")
                        continue
                
                results[template_name] = template_paths
                self.logger.info(f"Generated {len(template_paths)} cards using {template_name} template")
                
            except Exception as e:
                self.logger.error(f"Error with template {template_name}: {e}")
                results[template_name] = []
        
        return results
