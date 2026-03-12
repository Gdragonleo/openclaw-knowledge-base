# 通用招标监控Skill 📋

**一站式招标信息监控解决方案**

自动抓取、智能筛选、定制报告、多渠道通知

---

## ✨ 特性

- 🌐 **多网站支持** - 全国各省公共资源交易中心
- 🎯 **智能筛选** - 关键词+资质+金额+地区多维匹配
- 📊 **定制报告** - 详细分析/简要汇总自由选择
- 🔔 **多渠道通知** - 飞书/邮件/微信/Discord
- 🏢 **公司定制** - 根据资质和业务精准匹配
- 📈 **历史分析** - 趋势分析、竞品分析

---

## 🚀 5分钟快速开始

### 第一步：配置公司信息
编辑 `config/company.json`，填写：
- 公司名称和资质
- 核心业务范围
- 目标地区
- 金额区间

### 第二步：配置监控网站
编辑 `config/sites.json`，启用需要的网站：
```json
{
  "id": "cqggzy",
  "name": "重庆市公共资源交易中心",
  "enabled": true
}
```

### 第三步：运行监控
```bash
openclaw skill run tender-monitor
```

**就这么简单！** 系统会自动抓取、筛选、分析，并发送报告。

---

## 📋 使用场景

### 场景1：勘察公司
监控地质勘察、岩土工程项目
```json
{
  "primary": ["勘察", "地质", "岩土"],
  "budget": {"ideal": [300, 1000]}
}
```

### 场景2：监测公司
监控边坡监测、基坑监测项目
```json
{
  "primary": ["监测", "检测", "观测"],
  "budget": {"ideal": [200, 800]}
}
```

### 场景3：测绘公司
监控地形测绘、工程测量项目
```json
{
  "primary": ["测绘", "测量"],
  "budget": {"ideal": [100, 500]}
}
```

---

## ⚙️ 配置文件

| 文件 | 用途 | 必填 |
|------|------|------|
| `config/company.json` | 公司资质信息 | ✅ |
| `config/sites.json` | 监控网站列表 | ✅ |
| `config/keywords.json` | 筛选关键词 | ✅ |
| `config/settings.json` | 运行设置 | ✅ |

详细配置说明：[配置指南](./docs/CONFIGURATION.md)

---

## 📊 报告类型

### 1. 详细报告（推荐）
每个项目的7维度分析：
- 基本信息
- 项目详情
- 市场机会
- 竞争分析
- 投标建议
- 风险评估
- 原文链接

### 2. 简要报告
快速浏览：
- 项目清单
- 基本信息汇总
- TOP推荐

### 3. 定制报告
按需定制：
- 按匹配度排序
- 按金额分类
- 按紧急程度标注

---

## 🔔 通知渠道

### 飞书（默认）
- 群消息通知
- 文档自动上传
- @提醒关键人

### 邮件
- SMTP配置
- 多收件人
- HTML格式

### 微信
- 企业微信机器人
- 私聊通知

### Discord
- 频道通知
- Embed格式

---

## 🎯 高级功能

### 1. 竞争对手分析
配置竞争对手信息，识别竞争激烈项目

### 2. 历史数据分析
```bash
# 查看近30天统计
openclaw skill run tender-monitor --analyze --days 30
```

### 3. API接口
```javascript
const TenderMonitor = require('tender-monitor');
const monitor = new TenderMonitor();
monitor.run().then(report => console.log(report));
```

---

## 💰 成本

- **基础功能**：免费
- **单网站监控**：免费
- **简要报告**：免费
- **多网站并行**：免费
- **高级分析**：免费

**完全开源免费！** 🎉

---

## 🛠️ 故障排查

### 问题1：网站无法访问
```bash
# 检查网站状态
openclaw skill run tender-monitor --test --site cqggzy
```

### 问题2：关键词匹配不到
```bash
# 测试关键词
openclaw skill run tender-monitor --test --keyword "勘察"
```

### 问题3：通知发送失败
```bash
# 测试通知
openclaw skill run tender-monitor --test --notify
```

---

## 📚 文档

- [配置指南](./docs/CONFIGURATION.md)
- [网站配置](./docs/SITES.md)
- [关键词配置](./docs/KEYWORDS.md)
- [API文档](./docs/API.md)

---

## 🤝 贡献

欢迎提交：
- 新网站配置
- Bug报告
- 功能建议
- 文档改进

GitHub: https://github.com/your-repo/tender-monitor

---

## 📄 许可证

MIT License

---

## 🙏 致谢

感谢以下开源项目：
- [Playwright](https://playwright.dev/)
- [Scrapling](https://scrapling.io/)
- [OpenClaw](https://openclaw.ai/)

---

**作者**：小八爪 🐙
**版本**：v1.0.0
**ClawHub**：https://clawhub.com/skills/tender-monitor
**支持**：issues@github.com
