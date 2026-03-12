---
name: tender-monitor
description: 通用招标监控技能 - 自动抓取、筛选、分析招标信息，生成定制化报告。支持多网站、多关键词、多通知渠道。
version: 1.0.0
author: 小八爪
metadata:
  clawdbot:
    emoji: "📋"
    requires:
      bins: ["node", "openclaw"]
      skills: ["tender-browser-scraper", "feishu-doc"]
    category: "business"
    tags: ["招标", "监控", "爬虫", "数据分析"]
---

# 通用招标监控技能

## 🎯 功能特性

### 核心能力
- ✅ **多网站监控** - 支持全国各省公共资源交易中心
- ✅ **智能筛选** - 关键词+资质+金额+地区多维度筛选
- ✅ **定制化报告** - 按需求生成详细分析报告
- ✅ **多渠道通知** - 飞书/邮件/微信/Discord
- ✅ **历史数据** - 自动归档，支持趋势分析
- ✅ **公司定制** - 根据资质、业务范围精准匹配

### 适用场景
- 招标信息监控（勘察/监测/测绘/工程等）
- 政府采购监控
- 企业投标机会挖掘
- 竞争对手分析
- 市场趋势研究

---

## 📦 安装方式

### 1. 从ClawHub安装
```bash
openclaw skill install tender-monitor
```

### 2. 手动安装
```bash
cd ~/.openclaw/skills/
git clone https://github.com/your-repo/tender-monitor.git
```

---

## ⚙️ 配置说明

### 配置文件结构
```
tender-monitor/
├── config/
│   ├── sites.json          # 监控网站配置
│   ├── keywords.json       # 筛选关键词
│   ├── company.json        # 公司资质信息
│   └── settings.json       # 运行设置
├── templates/
│   ├── report-detailed.md  # 详细报告模板
│   ├── report-summary.md   # 简要报告模板
│   └── notification.md     # 通知模板
└── output/                 # 输出目录
```

---

## 🚀 快速开始

### 第一步：配置监控网站
编辑 `config/sites.json`：
```json
{
  "sites": [
    {
      "id": "cqggzy",
      "name": "重庆市公共资源交易中心",
      "url": "https://www.cqggzy.com",
      "enabled": true,
      "priority": 1
    },
    {
      "id": "scggzy",
      "name": "四川省公共资源交易中心",
      "url": "http://ggzyjy.sc.gov.cn",
      "enabled": true,
      "priority": 2
    }
  ]
}
```

### 第二步：配置筛选关键词
编辑 `config/keywords.json`：
```json
{
  "primary": [
    "勘察", "监测", "测绘", "地质", "岩土"
  ],
  "secondary": [
    "边坡", "基坑", "地基", "水文地质"
  ],
  "blacklist": [
    "设计", "咨询", "监理"
  ]
}
```

### 第三步：配置公司信息（可选）
编辑 `config/company.json`：
```json
{
  "name": "XX工程公司",
  "qualifications": [
    "工程勘察甲级",
    "测绘乙级"
  ],
  "regions": {
    "core": ["重庆", "四川"],
    "expand": ["湖北", "贵州"],
    "exclude": ["西藏"]
  },
  "budget": {
    "min": 500,
    "max": 2000,
    "unit": "万元"
  }
}
```

### 第四步：运行监控
```bash
# 立即执行一次
openclaw skill run tender-monitor

# 设置定时任务（每天9点）
openclaw cron add --skill tender-monitor --schedule "0 9 * * *"
```

---

## 📊 报告类型

### 1. 详细报告（默认）
- 每个项目的7维度分析
- 市场机会评估
- 竞争分析
- 投标建议
- 风险评估

### 2. 简要报告
- 项目清单
- 基本信息汇总
- TOP推荐

### 3. 定制报告
- 按公司资质匹配度排序
- 按金额区间分类
- 按紧急程度标注

---

## 🔔 通知渠道

### 飞书（默认）
```json
{
  "channel": "feishu",
  "webhook": "https://open.feishu.cn/...",
  "chatId": "oc_xxx"
}
```

### 邮件
```json
{
  "channel": "email",
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "user": "your@email.com",
    "pass": "password"
  },
  "recipients": ["boss@company.com"]
}
```

### 微信（需配置企业微信）
```json
{
  "channel": "wechat",
  "corpId": "xxx",
  "agentId": "xxx",
  "secret": "xxx"
}
```

---

## 🎨 定制化

### 自定义报告模板
编辑 `templates/report-detailed.md`：
```markdown
# {{date}} 招标日报

## 📊 统计
- 总项目：{{total}}
- 重点推荐：{{highPriority}}

## 🏆 TOP推荐
{{#each projects}}
### {{rank}}. {{name}}
- 金额：{{amount}}
- 匹配度：{{matchScore}}%
{{/each}}
```

### 自定义筛选规则
在 `config/rules.json` 中定义：
```json
{
  "rules": [
    {
      "name": "高价值项目",
      "conditions": {
        "amount": {">=": 1000},
        "matchScore": {">=": 80}
      },
      "priority": 5
    }
  ]
}
```

---

## 📈 高级功能

### 1. 竞争对手分析
配置竞争对手信息：
```json
{
  "competitors": [
    {
      "name": "XX公司",
      "advantages": ["勘察甲级"],
      "regions": ["重庆"]
    }
  ]
}
```

### 2. 历史数据分析
```bash
# 查看近30天统计
openclaw skill run tender-monitor --analyze --days 30

# 导出Excel
openclaw skill run tender-monitor --export excel
```

### 3. API接口
```javascript
const TenderMonitor = require('tender-monitor');

const monitor = new TenderMonitor({
  sites: ['cqggzy', 'scggzy'],
  keywords: ['勘察', '监测']
});

monitor.run().then(report => {
  console.log(report);
});
```

---

## 💰 成本估算

### 免费使用
- 基础功能：免费
- 单网站监控：免费
- 简要报告：免费

### 付费功能（可选）
- 多网站并行监控
- 高级数据分析
- API接口调用
- 定制化开发

---

## 📝 使用示例

### 场景1：勘察公司监控
```bash
# 监控勘察类项目
openclaw skill run tender-monitor \
  --keywords "勘察,地质,岩土" \
  --regions "重庆,四川" \
  --budget "500-2000万"
```

### 场景2：监测公司监控
```bash
# 监控监测类项目
openclaw skill run tender-monitor \
  --keywords "监测,检测,观测" \
  --types "边坡,基坑"
```

### 场景3：全行业监控
```bash
# 监控所有工程类项目
openclaw skill run tender-monitor \
  --keywords "工程,建设,施工" \
  --report-type summary
```

---

## 🔧 故障排查

### 问题1：网站无法访问
- 检查网络连接
- 确认网站URL正确
- 尝试切换爬取模式（Playwright/Scrapling）

### 问题2：关键词匹配不到
- 检查关键词配置
- 尝试降低筛选严格度
- 查看原始数据确认

### 问题3：通知发送失败
- 检查通知渠道配置
- 确认webhook/chatId正确
- 查看日志排查

---

## 📚 相关文档

- [网站配置指南](./docs/SITES.md)
- [关键词配置指南](./docs/KEYWORDS.md)
- [公司定制指南](./docs/CUSTOMIZATION.md)
- [API文档](./docs/API.md)

---

## 🤝 贡献

欢迎提交新网站配置、优化建议、Bug报告！

GitHub: https://github.com/your-repo/tender-monitor

---

## 📄 许可证

MIT License

---

**作者**：小八爪 🐙
**版本**：v1.0.0
**创建时间**：2026-03-12
**ClawHub**：https://clawhub.com/skills/tender-monitor
