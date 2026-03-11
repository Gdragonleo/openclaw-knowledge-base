# 每30分钟查询GitHub协作任务

## 任务说明

每30分钟自动查询GitHub Issues协作中心，检查是否有新任务需要执行。

## 执行时间

- **触发时间**：每30分钟（每小时的00分和30分）
- **Cron表达式**：`0,30 * * * *`

## 执行步骤

### 1. 查询GitHub Issues

**仓库信息**：
- Owner: `Gdragonleo`
- Repo: `openclaw-knowledge-base`
- URL: https://github.com/Gdragonleo/openclaw-knowledge-base/issues

**查询条件**：
- 状态：Open
- 标题包含：`[BOT_TASK]`
- 排序：创建时间（最新的在前）

**API调用**：
```bash
curl -H "Authorization: token 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" \
  "https://api.github.com/repos/Gdragonleo/openclaw-knowledge-base/issues?state=open&labels=bot-task"
```

---

### 2. 处理任务

**优先级排序**：
1. [P5] - 紧急（立即处理）
2. [P4] - 重要（优先处理）
3. [P3] - 普通
4. [P2] - 低优先级
5. [P1] - 最低优先级

**处理流程**：
1. 读取Issue内容
2. 执行任务
3. 添加评论说明结果
4. 关闭Issue

---

### 3. 任务类型处理

#### [BOT_TASK] 任务指令

**处理步骤**：
1. 解析任务描述
2. 判断任务类型（自己执行 or 交给小鲸鱼）
3. 执行任务
4. 添加评论：
   ```markdown
   ## 任务完成

   **执行结果**：[结果说明]

   **执行时间**：YYYY-MM-DD HH:MM

   **产出文件**：[文件路径]

   ---
   🐙 小八爪
   ```
5. 关闭Issue

---

#### [CHAT] 日常交流

**处理步骤**：
1. 阅读内容
2. 评论回复
3. 不关闭Issue（可以持续讨论）

---

#### [P5] 紧急任务

**处理步骤**：
1. 立即处理（不等待定时任务）
2. 完成后私聊通知小刘
3. 评论说明结果
4. 关闭Issue

---

### 4. 示例任务

#### 示例Issue

**标题**：`[BOT_TASK] [P4] 分析股市K线图`

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
```

**小八爪处理**：
1. 发现Issue
2. 判断这是图片分析任务
3. 交给小鲸鱼执行（通过多维表格或私聊）
4. 小鲸鱼完成后，整合结果
5. 评论：
   ```markdown
   ## 任务完成

   **执行结果**：
   - 趋势：上升趋势
   - 支撑位：1850元
   - 阻力位：2050元
   - 建议：继续持有，关注2050元阻力位

   **执行时间**：2026-03-12 08:30

   **产出文件**：`outputs/股市分析_贵州茅台_2026-03-12.md`

   ---
   🐙 小八爪
   ```
6. 关闭Issue

---

## API参考

### 查询Issues

```bash
# 查询所有Open的Issues
GET https://api.github.com/repos/Gdragonleo/openclaw-knowledge-base/issues?state=open

# 查询特定标签的Issues
GET https://api.github.com/repos/Gdragonleo/openclaw-knowledge-base/issues?state=open&labels=bot-task

# 搜索标题包含[BOT_TASK]的Issues
GET https://api.github.com/search/issues?q=repo:Gdragonleo/openclaw-knowledge-base+is:issue+is:open+[BOT_TASK]
```

---

### 添加评论

```bash
POST https://api.github.com/repos/Gdragonleo/openclaw-knowledge-base/issues/{issue_number}/comments

Body:
{
  "body": "## 任务完成\n\n执行结果：..."
}
```

---

### 关闭Issue

```bash
PATCH https://api.github.com/repos/Gdragonleo/openclaw-knowledge-base/issues/{issue_number}

Body:
{
  "state": "closed"
}
```

---

## 错误处理

### 问题1：API调用失败

**症状**：无法查询或操作Issues

**解决**：
- 检查Token是否有效
- 记录错误日志
- 下次重试

### 问题2：任务执行失败

**症状**：无法完成任务

**解决**：
- 评论说明失败原因
- 不关闭Issue
- 私聊通知小刘

---

## 日志记录

**保存位置**：`outputs/小八爪/2026-03/团队协作/GitHub任务日志_YYYY-MM-DD.md`

**日志格式**：
```markdown
## 查询时间：2026-03-12 08:00

### 发现任务：2个

#### Issue #2：[BOT_TASK] [P4] 分析股市K线图
- Issue ID: 2
- 优先级: P4
- 状态: Open
- 处理结果: 已完成
- 完成时间: 2026-03-12 08:30

#### Issue #3：[CHAT] 今天有什么任务？
- Issue ID: 3
- 优先级: 普通
- 状态: Open
- 处理结果: 已评论回复
```

---

**创建时间**：2026-03-12 00:10
**更新时间**：2026-03-12 00:15
**创建人**：小八爪🐙
