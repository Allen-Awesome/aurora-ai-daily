# AI行业热点采集系统

一个自动化的AI行业新闻采集、摘要生成和卡片制作系统，帮助AI从业者每日获取行业热点资讯。

## 功能特性

- 🕷️ **多源数据采集**：自动爬取TechCrunch、VentureBeat、arXiv等权威AI资讯源
- 🤖 **智能内容总结**：使用DeepSeek生成200-300字的精准摘要
- 🎨 **卡片图片生成**：自动生成包含摘要和二维码的精美卡片
- 📱 **二维码跳转**：扫码直达原文，便于深度阅读
- ⏰ **定时任务**：每日早8点自动执行采集任务
- 🏷️ **智能分类**：自动提取关键词和重要性评分

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd ai-news-collector

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，添加你的DeepSeek API Key
```

### 2. 配置说明

在`.env`文件中配置必要参数：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 日志配置

系统使用集中式日志（控制台 + 旋转文件）。通过环境变量控制：

```env
# 日志等级：DEBUG/INFO/WARNING/ERROR
LOG_LEVEL=INFO
# 是否输出为 JSON（便于 ELK/Datadog）
LOG_JSON=false
# 文件名与滚动策略
LOG_FILE=news_system.log
LOG_MAX_BYTES=1048576   # 单文件最大 1MB
LOG_BACKUP_COUNT=5      # 轮转份数
```

### 3. 运行系统

```bash
# 立即执行一次采集任务（测试用）
python src/scheduler.py --now

# 启动定时任务（每日8点自动执行）
python src/scheduler.py
```

## 项目结构

```
├── src/
│   ├── crawler.py          # 新闻爬虫模块
│   ├── summarizer.py       # 内容总结模块
│   ├── card_generator.py   # 卡片生成模块
│   └── scheduler.py        # 任务调度模块
├── daily_news/             # 每日生成的新闻数据
├── generated_cards/        # 生成的卡片图片
├── requirements.txt        # 项目依赖
├── .env.example           # 环境变量示例
└── README.md              # 项目说明
```

## 核心模块说明

### 新闻爬虫 (crawler.py)
- 支持RSS源和API采集
- 内置去重和时间过滤
- 覆盖主要AI资讯网站和GitHub热门项目

### 内容总结 (summarizer.py)
- 集成DeepSeek API
- 智能提取关键词
- 基于来源权威性的重要性评分

### 卡片生成 (card_generator.py)
- 自动布局设计
- 重要性颜色编码
- 二维码集成
- 支持中文字体

### 任务调度 (scheduler.py)
- 定时任务管理
- 完整的工作流程
- 日志记录和错误处理

## 数据源

当前支持的数据源包括：

- **TechCrunch AI** - 科技新闻
- **VentureBeat AI** - 行业动态
- **arXiv AI** - 学术论文
- **Towards Data Science** - 技术博客
- **MIT Technology Review** - 深度分析
- **GitHub Trending** - 热门开源项目

## 输出示例

系统每日会生成：

1. **JSON摘要文件**：包含所有文章的结构化摘要数据
2. **卡片图片**：PNG格式的新闻卡片，包含：
   - 文章标题和摘要
   - 来源和时间信息
   - 关键词标签
   - 重要性颜色指示
   - 原文跳转二维码

## 自定义配置

### 修改数据源
在`crawler.py`中的`sources`字典添加新的RSS源：

```python
self.sources = {
    'your_source': 'https://example.com/rss',
    # ... 其他源
}
```

### 调整卡片样式
在`card_generator.py`中修改颜色和布局配置：

```python
self.colors = {
    'background': '#FFFFFF',
    'primary': '#2E3440',
    # ... 其他颜色
}
```

### 修改执行时间
在`scheduler.py`中调整定时任务：

```python
schedule.every().day.at("08:00").do(self.daily_news_collection)
```

## 部署建议

### 本地部署
- 适合个人使用
- 需要稳定的网络环境
- 建议配置代理以提高爬取稳定性

### 云服务器部署
- 推荐使用Linux服务器
- 配置systemd服务实现开机自启
- 使用nginx反向代理（如需Web界面）

### Docker部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/scheduler.py"]
```

## 注意事项

1. **API费用**：使用DeepSeek API会产生费用，建议设置使用限额
2. **爬虫礼仪**：遵守robots.txt，避免过于频繁的请求
3. **版权合规**：生成的摘要仅供个人学习使用
4. **数据存储**：定期清理旧数据以节省存储空间

## 故障排除

### 常见问题

**Q: DeepSeek API调用失败**
A: 检查API Key是否正确，账户是否有余额

**Q: 爬取某些网站失败**
A: 可能是反爬虫机制，建议添加请求头或使用代理

**Q: 生成的卡片中文显示异常**
A: 确保系统安装了中文字体，或修改字体路径

**Q: 定时任务不执行**
A: 检查系统时间设置，确保服务持续运行

## 贡献指南

欢迎提交Issue和Pull Request来改进项目：

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过Issue联系。
