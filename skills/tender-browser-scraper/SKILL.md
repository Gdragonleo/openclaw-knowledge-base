---
name: tender-browser-scraper
description: 招标网站自动化爬取工具，支持反爬绕过、验证码处理、智能过滤。专门用于抓取公共资源交易中心招标公告，支持Playwright和Scrapling双重模式。
version: 1.0.0
author: 小龙
metadata:
  clawdbot:
    emoji: "📋"
    requires:
      bins: ["node"]
      skills: ["playwright-scraper", "openclaw-scrapling"]
---

# 招标网站自动化爬取工具

专门用于抓取公共资源交易中心招标公告的智能爬虫工具。

## 功能特性

### 🎯 核心功能
- **真实浏览器模拟**：使用Playwright模拟真实用户行为
- **智能反爬绕过**：自动处理Cloudflare、创宇盾等反爬机制
- **双重模式切换**：Playwright失败自动切换Scrapling
- **验证码人工介入**：遇到验证码暂停并飞书通知
- **智能过滤**：根据资质关键词自动筛选相关项目

### 📊 支持的网站
- 重庆市公共资源交易中心：https://www.cqggzy.com
- （可扩展其他公共资源交易网站）

### 🔍 过滤条件
关键词白名单（根据公司资质）：
- 建筑工程、市政工程、园林绿化、钢结构
- 装饰装修、房建、道路、桥梁
- 给排水、景观、幕墙、内装

## 使用方法

### 基础用法
```bash
# 抓取重庆公共资源交易中心招标公告
node scripts/scrape.js --site cqggzy

# 指定输出目录
node scripts/scrape.js --site cqggzy --output ./output/tenders

# 设置最大项目数
node scripts/scrape.js --site cqggzy --max 50
```

### 高级选项
```bash
# 启用Scrapling模式（绕过强反爬）
node scripts/scrape.js --site cqggzy --use-scrapling

# 自定义间隔时间（秒）
node scripts/scrape.js --site cqggzy --min-interval 5 --max-interval 10

# 指定时间范围（最近N天）
node scripts/scrape.js --site cqggzy --days 30

# 飞书通知开关
node scripts/scrape.js --site cqggzy --notify
```

## 配置说明

### 环境变量
- `TENDER_OUTPUT_DIR`：输出目录（默认：./output/tenders）
- `FEISHU_WEBHOOK`：飞书通知webhook地址
- `CAPTCHA_NOTIFY`：是否通知验证码（true/false）

### 招标网站配置
配置文件：`config/sites.json`

```json
{
  "cqggzy": {
    "name": "重庆市公共资源交易中心",
    "url": "https://www.cqggzy.com",
    "selectors": {
      "listContainer": ".tender-list",
      "itemTitle": ".tender-title",
      "itemAmount": ".tender-amount",
      "itemDate": ".tender-date",
      "detailLink": ".tender-link"
    }
  }
}
```

## 工作流程

### 1. 初始化阶段
```
启动浏览器 → 检测反爬机制 → 选择爬取模式
```

### 2. 列表抓取阶段
```
访问首页 → 等待加载 → 截图快照 
→ 点击"招标公告" → 筛选时间 → 提取列表
```

### 3. 详情抓取阶段
```
逐条访问详情页 → 提取完整信息 → 关键词过滤 
→ 保存MD文件
```

### 4. 异常处理
```
遇到验证码 → 暂停 → 飞书通知 → 等待人工处理
Playwright失败 → 切换Scrapling → 重试
```

## 输出格式

### 文件结构
```
output/tenders/
├── 2026-03-09_cqggzy.md          # 当日抓取汇总
├── projects/
│   ├── project_001.md            # 单个项目详情
│   ├── project_002.md
│   └── ...
└── logs/
    ├── scrape_2026-03-09.log     # 抓取日志
    └── error_2026-03-09.log      # 错误日志
```

### MD文件格式
```markdown
# 项目名称

**招标单位**：XXX公司
**项目金额**：XXX万元
**地区**：重庆市XX区
**发布时间**：2026-03-09
**截止时间**：2026-03-20

## 项目详情
...

## 联系方式
...

## 原文链接
[查看详情](URL)
```

## 技术栈

- **Playwright**：真实浏览器自动化
- **Scrapling**：反爬绕过增强
- **Cheerio**：HTML解析
- **Markdown**：输出格式

## 注意事项

⚠️ **合规使用**
- 遵守robots.txt
- 控制访问频率
- 不抓取敏感信息
- 仅用于公开招标信息

⚠️ **反爬机制**
- 随机间隔3-8秒
- 模拟真实用户行为
- 遇到验证码暂停
- 飞书通知人工处理

## 更新日志

### v1.0.0 (2026-03-09)
- ✅ 初始版本
- ✅ 支持重庆公共资源交易中心
- ✅ Playwright + Scrapling双重模式
- ✅ 智能关键词过滤
- ✅ 飞书验证码通知
