# tender-daily-report 📊

招标日报自动生成工具 v2.0

从 tender-browser-scraper + integrate_with_whale.py 整合封装。

## 一条命令运行

```bash
bash scripts/run_pipeline.sh
```

## 流水线

```
爬取 → 硬筛选 → 7维度评分 → 生成报告 → 按日期归档 → 验证
```

## 文件结构

```
tender-daily-report/
├── SKILL.md                    # 技能说明（OpenClaw读取）
├── README.md                   # 本文件
├── config/
│   ├── settings.json           # 运行配置（天数、条数、输出目录等）
│   ├── keywords.json           # 关键词配置（筛选+排除规则）
│   ├── company_profile.json    # 公司画像（7维度评分依据）
│   └── sites.json              # 站点配置（公共资源交易中心列表）
├── scripts/
│   ├── run_pipeline.sh         # 主流水线脚本（一键运行）
│   ├── score_and_report.py     # 评分+报告生成（可单独调用）
│   └── verify_outputs.py       # 产物验证（检查文件是否正确生成）
└── templates/                  # 报告模板（预留）
```

## 输出

```
知识库/招标监控/
├── 2026-03-20/                          # 当日归档
│   ├── 招标日报_2026-03-20.md
│   ├── 招标日报_2026-03-20_projects.json
│   ├── 招标日报_2026-03-20_summary.json
│   └── pipeline_2026-03-20.log
├── _latest/                             # 最新快捷入口（符号链接）
└── 历史报告/                            # 自动归档
```

## 依赖

- Node.js >= 18（爬虫部分）
- Python 3 >= 3.9（评分+报告）
- puppeteer-extra + stealth（反爬，已安装在 tender-browser-scraper/node_modules）

## 与旧版的关系

| 旧文件 | 新位置 | 说明 |
|--------|--------|------|
| tender-browser-scraper/run_whale_pipeline.sh | scripts/run_pipeline.sh | 新增日期归档+验证 |
| tender-browser-scraper/integrate_with_whale.py | scripts/score_and_report.py | 重构为可配置版本 |
| 硬编码路径 | config/settings.json | 全部可配置 |
| 固定文件名覆盖 | 日期目录归档 | 不再覆盖历史 |

---

**作者**: 小八爪 🐙 | **版本**: v2.0.0 | **日期**: 2026-03-20
