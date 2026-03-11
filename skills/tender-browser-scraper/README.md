# 招标网站自动化爬取工具

## 快速开始

### 1. 安装依赖
```bash
cd /Users/danxiong/.openclaw/workspace/skills/tender-browser-scraper
npm install
```

### 2. 运行爬虫
```bash
# 基础用法：抓取重庆公共资源交易中心
node scripts/scrape.js --site cqggzy

# 指定输出目录和最大项目数
node scripts/scrape.js --site cqggzy --output ./my-tenders --max 50

# 启用Scrapling模式（绕过强反爬）
node scripts/scrape.js --site cqggzy --use-scrapling

# 开启飞书通知
node scripts/scrape.js --site cqggzy --notify
```

### 3. 查看结果
输出文件位于：`./output/tenders/`

文件格式：
```
output/tenders/
├── 2026-03-09_cqggzy.md          # 汇总报告
├── logs/
│   ├── homepage.png               # 首页截图
│   └── scrape_2026-03-09.log      # 日志
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--site` | 网站代码（cqggzy） | cqggzy |
| `--output` | 输出目录 | ./output/tenders |
| `--max` | 最大项目数 | 50 |
| `--min-interval` | 最小间隔（秒） | 3 |
| `--max-interval` | 最大间隔（秒） | 8 |
| `--days` | 抓取最近N天 | 30 |
| `--use-scrapling` | 使用Scrapling模式 | false |
| `--notify` | 飞书通知 | false |

## 功能特性

### ✅ 已实现
- [x] Playwright真实浏览器模拟
- [x] Stealth插件反爬绕过
- [x] 随机间隔模拟人工浏览
- [x] 智能关键词过滤
- [x] 详情页完整提取
- [x] Markdown格式输出
- [x] 首页截图存证

### 🔄 待实现
- [ ] Scrapling模式切换
- [ ] 验证码检测与飞书通知
- [ ] 分页自动翻页
- [ ] 时间范围筛选
- [ ] 多网站支持

## 注意事项

⚠️ **使用前确保**：
1. Playwright已安装：`npx playwright install chromium`
2. 浏览器隔离模式已启用（已在~/.openclaw/openclaw.json配置）
3. 飞书webhook已配置（如需通知）

⚠️ **合规使用**：
- 仅抓取公开招标信息
- 遵守网站robots.txt
- 控制访问频率
- 不用于商业牟利

## 故障排查

### 问题1：浏览器启动失败
```bash
# 安装Playwright浏览器
npx playwright install chromium
```

### 问题2：被反爬机制拦截
```bash
# 使用Scrapling模式重试
node scripts/scrape.js --site cqggzy --use-scrapling
```

### 问题3：找不到招标公告
检查`config/sites.json`中的选择器是否正确

## 联系方式

如有问题，联系小龙（智能助手）💪
