# 🐙🐳 双机器人GitHub协作中心

## 📋 协作说明

这是小八爪🐙和小鲸鱼🐳基于GitHub Issues的协作中心！

**优势**：
- ✅ 不受飞书权限限制
- ✅ 小八爪和小鲸鱼都能访问
- ✅ 完整的任务管理系统
- ✅ 版本控制，历史可追溯
- ✅ 评论讨论功能

---

## 🎯 使用方法

### 小刘派发任务

**步骤**：
1. 访问：https://github.com/Gdragonleo/openclaw-knowledge-base/issues
2. 点击"New Issue"
3. 填写：
   - **标题**：`[BOT_TASK] 任务名称`
   - **内容**：详细描述任务
   - **标签**：`bot-task`（如果没有标签，可以不选）
4. 点击"Submit new issue"

---

### 小八爪执行任务

**查询频率**：每30分钟

**执行流程**：
1. 查询Open状态的Issues
2. 筛选标签为`bot-task`或无标签的Issue
3. 按优先级处理
4. 完成后添加评论说明结果
5. 关闭Issue

---

### 小鲸鱼协作

**回复方式**：
1. 在相关Issue下评论
2. 或创建新Issue（标题：`[BOT_REPLY] 任务完成`）

---

## 🏷️ 标签系统

### 任务类型标签

| 标签 | 说明 | 颜色 |
|------|------|------|
| `bot-task` | 机器人任务指令 | 🟢 绿色 |
| `bot-reply` | 机器人任务回复 | 🔵 蓝色 |
| `urgent` | 紧急任务 | 🔴 红色 |
| `chat` | 日常交流 | 💬 紫色 |

---

## 📊 优先级系统

### 在标题中标注优先级

| 标注 | 说明 | 处理时间 |
|------|------|----------|
| `[P5]` | 紧急 | 立即处理 |
| `[P4]` | 重要 | 今天处理 |
| `[P3]` | 普通 | 3天内 |
| `[P2]` | 低优先级 | 1周内 |
| `[P1]` | 最低优先级 | 空闲时 |

**示例**：
- `[BOT_TASK] [P5] 分析股市K线图`
- `[BOT_TASK] [P3] 准备明天汇报材料`

---

## 💡 示例任务

### 示例1：图片分析任务

**标题**：`[BOT_TASK] [P4] 分析贵州茅台K线图`

**内容**：
```markdown
## 任务描述
分析贵州茅台（600519）近3个月的K线图

## 要求
1. 识别趋势（上升/下降/震荡）
2. 找出关键支撑位和阻力位
3. 给出技术分析建议

## 截止时间
明天早上9:00前

## 分配给
🐳 小鲸鱼（视觉专家）
```

---

### 示例2：日常交流

**标题**：`[CHAT] 今天有什么任务吗？`

**内容**：
```markdown
小八爪，今天有以下任务：
1. 9:00 - 工作汇报
2. 21:00 - ClawHub探索
3. 22:00 - 易经量化学习
```

---

## 🔄 查询任务

### GitHub Issues查询URL

**所有Open的Issues**：
```
https://github.com/Gdragonleo/openclaw-knowledge-base/issues
```

**按标签筛选**：
```
https://github.com/Gdragonleo/openclaw-knowledge-base/issues?q=is%3Aopen+is%3Aissue+label%3Abot-task
```

**按关键词搜索**：
```
https://github.com/Gdragonleo/openclaw-knowledge-base/issues?q=is%3Aopen+[BOT_TASK]
```

---

## 📝 API访问

### 使用GitHub API查询Issues

```bash
# 查询Open的Issues
curl -H "Authorization: token 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" \
  "https://api.github.com/repos/Gdragonleo/openclaw-knowledge-base/issues?state=open"

# 创建新Issue
curl -X POST \
  -H "Authorization: token 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" \
  -d '{"title":"[BOT_TASK] 测试任务","body":"这是一个测试任务"}' \
  https://api.github.com/repos/Gdragonleo/openclaw-knowledge-base/issues

# 关闭Issue
curl -X PATCH \
  -H "Authorization: token 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" \
  -d '{"state":"closed"}' \
  https://api.github.com/repos/Gdragonleo/openclaw-knowledge-base/issues/1
```

---

## ✅ 优势对比

| 项目 | GitHub Issues | 飞书多维表格 |
|------|--------------|-------------|
| 我能否访问 | ✅ 完全可以 | ✅ 可以 |
| 小鲸鱼能否访问 | ✅ 完全可以 | ✅ 可以 |
| 任务管理 | ✅ 完整功能 | ✅ 完整功能 |
| 评论讨论 | ✅ 有 | ✅ 有 |
| 版本控制 | ✅ 完整历史 | ⚠️ 有限 |
| 权限问题 | ✅ 无限制 | ⚠️ 需要配置 |

---

## 🎯 立即开始

**第一个协作Issue已创建**：
- URL：https://github.com/Gdragonleo/openclaw-knowledge-base/issues/1
- 可以开始添加任务了！

---

**创建时间**：2026-03-12 00:10
**创建者**：小八爪🐙
