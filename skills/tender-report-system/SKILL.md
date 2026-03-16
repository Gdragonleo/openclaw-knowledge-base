# 招标智能报告系统

**版本**：v1.0  
**作者**：小八爪 🐙 + 小鲸鱼 🐳  
**更新时间**：2026-03-16 03:11

---

## 📋 技能简介

招标智能报告系统是一个完整的招标信息采集、评分、报告生成工具。

**核心功能**：
- 🕷️ 自动爬取招标网站（Playwright真实浏览器）
- 🧠 智能评分（7维度算法）
- 📊 生成HTML报告（本地打开）
- 🌐 提供localhost服务（实时更新）

---

## 🚀 快速开始

### 方式1：生成HTML报告（推荐）

```bash
# 一键生成报告
openclaw tender-report generate

# 打开报告
openclaw tender-report open
```

**优点**：
- ✅ 无需服务器
- ✅ 即开即用
- ✅ 离线可用

---

### 方式2：启动localhost服务

```bash
# 启动服务
openclaw tender-report serve

# 浏览器访问
# http://localhost:8080
```

**优点**：
- ✅ 实时更新
- ✅ 交互式筛选
- ✅ API接口

---

## 📊 使用示例

### 示例1：生成今日报告

```bash
# 生成HTML报告
python scripts/generate_report.py

# 输出位置
# ~/agent-collaboration/projects/tender-system/reports/daily_report.html
```

### 示例2：启动Web服务

```bash
# 启动服务（后台运行）
python scripts/start_server.py

# 访问地址
# http://localhost:8080
# http://localhost:8080/api/projects (API)
```

---

## ⚙️ 配置文件

**位置**：`scripts/config.json`

**可配置项**：
```json
{
  "company_profile": {
    "preferred_types": ["勘察", "监测", "测绘"],
    "preferred_regions": ["重庆市", "四川省"],
    "preferred_budget_range": [50, 500],
    "excluded_keywords": ["园林", "绿化"],
    "success_keywords": ["岩土", "地质", "水利"]
  },
  "crawler": {
    "sources": [
      {"name": "重庆市公共资源交易中心", "url": "https://www.cqggzy.com"},
      {"name": "湖北省公共资源交易中心", "url": "https://www.hbggzyfwpt.cn"}
    ],
    "timeout": 90,
    "headless": false
  },
  "output": {
    "html_path": "~/agent-collaboration/projects/tender-system/reports/",
    "json_path": "~/agent-collaboration/projects/tender-system/data/"
  }
}
```

---

## 📋 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 业务方向 | 30% | 与公司主营业务的匹配度 |
| 地区匹配 | 10% | 是否在偏好地区 |
| 金额匹配 | 10% | 预算是否在最优范围 |
| 客户关系 | 10% | 是否为长期客户 |
| 成功案例 | 20% | 与历史成功案例的相似度 |
| 时间安排 | 10% | 截止时间是否充裕 |
| 特殊需求 | 10% | 是否匹配公司特殊能力 |

**推荐等级**：
- **A级（≥85分）**：强烈推荐，立即跟进
- **B级（75-84分）**：重点推荐，优先跟进
- **C级（65-74分）**：一般推荐，视情况跟进
- **D级（<65分）**：不推荐，暂缓跟进

---

## 🔧 技术架构

```
🕷️ 爬虫层（Playwright）
    ↓
📊 评分层（7维度算法）
    ↓
🎨 展示层（HTML / localhost）
```

**技术栈**：
- Python 3.9
- Playwright + Chromium
- 7维度评分算法
- HTML + CSS + JavaScript

---

## 📂 文件结构

```
skills/tender-report-system/
├── SKILL.md                    # 本文档
├── scripts/
│   ├── generate_report.py      # 生成报告脚本
│   ├── start_server.py         # 启动服务脚本
│   └── config.json             # 配置文件
├── templates/
│   └── report_template.html    # 报告模板
└── examples/
    └── example_output.html     # 示例输出
```

---

## 🔄 自动更新

**定时任务**：每天凌晨5:00自动运行

**流程**：
```
爬虫采集 → 评分筛选 → 生成HTML → 推送Gitee → 飞书通知
```

---

## 🌐 API接口（localhost模式）

**获取项目列表**：
```
GET http://localhost:8080/api/projects
```

**健康检查**：
```
GET http://localhost:8080/api/health
```

**返回示例**：
```json
{
  "stats": {
    "total": 10,
    "excluded": 5,
    "high_match": 3,
    "avg_score": 78
  },
  "projects": [...]
}
```

---

## ⚠️ 注意事项

1. **首次使用需安装依赖**：
   ```bash
   pip install playwright
   python -m playwright install chromium
   ```

2. **HTML报告需本地打开**（浏览器工具不支持file://协议）

3. **localhost服务需保持运行**

4. **配置文件修改后需重启服务**

---

## 🐛 故障排查

### 问题1：Playwright安装失败
```bash
# 升级pip
python3 -m pip install --upgrade pip

# 重新安装
pip3 install playwright
python3 -m playwright install chromium
```

### 问题2：端口8080被占用
```bash
# 查看占用进程
lsof -i :8080

# 修改端口（在start_server.py中）
python scripts/start_server.py --port 8081
```

---

## 📈 后续优化

- [ ] 支持更多招标网站
- [ ] 添加邮件推送
- [ ] 历史数据统计
- [ ] 中标率预测模型
- [ ] 移动端适配

---

## 📝 更新日志

**v1.0 (2026-03-16)**
- ✅ 初始版本发布
- ✅ Playwright爬虫集成
- ✅ 7维度评分算法
- ✅ HTML报告生成
- ✅ localhost服务支持

---

## 🤝 贡献者

- 🐙 **小八爪**：爬虫开发、系统整合
- 🐳 **小鲸鱼**：评分算法、报告模板

---

## 📄 许可证

内部使用 - 刘氏集团

---

**系统已就绪！** 🚀

——
🐙 小八爪 + 🐳 小鲸鱼
2026-03-16 03:11
