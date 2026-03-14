# TOOLS.md - Local Notes

## 📦 三个Gitee仓库清单

**根据小刘指示（2026-03-14 07:49 - 08:07）**：

| # | 仓库名称 | 用途 | 本地路径 | Gitee地址 | 内容 |
|---|---------|------|---------|----------|------|
| 1️⃣ | **collab-knowledge-base** | 🐙 小八爪的记忆内容 | `~/collab-knowledge-base` | https://gitee.com/whaleandcollab/collab-knowledge-base | MEMORY.md、HEARTBEAT.md、知识库、memory/、skills/等 |
| 2️⃣ | **whale-workspace** | 🐋 小鲸鱼的记忆内容 | （未在本地） | https://gitee.com/whaleandcollab/whale-workspace | 小鲸鱼的MEMORY.md、学习笔记、成长记录等 |
| 3️⃣ | **agent-collaboration** | 🤝 双机器人协作空间 | `~/agent-collaboration` | https://gitee.com/whaleandcollab/agent-collaboration | chat-history/（协作对话）、tasks/（任务）、knowledge-sharing/（知识分享） |

---

## 🔍 详细说明

### 1️⃣ **小八爪的记忆仓库**（collab-knowledge-base）
- **用途**：存放小八爪的所有记忆、知识、配置
- **本地路径**：`/Users/danxiong/collab-knowledge-base`
- **Gitee地址**：https://gitee.com/whaleandcollab/collab-knowledge-base
- **访问权限**：✅ 读写同步
- **核心文件**：
  - MEMORY.md（长时记忆）
  - HEARTBEAT.md（心跳任务）
  - AGENTS.md、SOUL.md、USER.md、IDENTITY.md（身份配置）
  - 知识库/（所有知识）
  - memory/（每日记忆）
  - skills/（技能库）
  - MOC/（知识导航）

---

### 2️⃣ **小鲸鱼的记忆仓库**（whale-workspace）
- **用途**：存放小鲸鱼的所有记忆、学习笔记、成长记录
- **本地路径**：（未在本地克隆）
- **地址**：**https://gitee.com/whaleandcollab/whale-workspace**
- **状态**：🔒 私有仓库（小八爪返回403 Forbidden，无法直接访问）
- **核心内容**：
  - 小鲸鱼的MEMORY.md
  - 学习笔记
  - 技能成长记录
  - 定时任务记录

**⚠️ 访问权限**：
- ✅ 小刘已提供地址
- ❌ 小八爪无API访问权限（403 Forbidden）
- ✅ 小鲸鱼自己可以访问
- ✅ 双方通过 agent-collaboration 仓库协作

---

### 3️⃣ **双机器人协作仓库**（agent-collaboration）
- **用途**：小八爪 × 小鲸鱼的协作空间
- **本地路径**：`/Users/danxiong/agent-collaboration`
- **Gitee地址**：https://gitee.com/whaleandcollab/agent-collaboration
- **核心目录**：
  - `chat-history/`（协作对话记录）
  - `tasks/`（任务归档）
  - `knowledge-sharing/`（知识分享）
  - `.github/`（Issue模板、Actions）

**协作流程**：
1. 任务派发 → Gitee Issues（agent-collaboration）
2. 成果提交 → Issue回复 + 仓库推送
3. 对话记录 → `chat-history/Gitee对话.md`

---

## 🔄 同步策略

| 仓库 | 同步方式 | 频率 |
|------|---------|------|
| collab-knowledge-base | 自动同步到Gitee | 每2天（任务8） |
| whale-workspace | 小鲸鱼管理 | 小鲸鱼自己管理 |
| agent-collaboration | 双方推送 | 实时 |

---

## 📋 小八爪的访问权限

| 仓库 | 读取 | 写入 | 同步 |
|------|------|------|------|
| collab-knowledge-base | ✅ | ✅ | ✅（每2天） |
| whale-workspace | ❌ | ❌ | ❌（私有仓库） |
| agent-collaboration | ✅ | ✅ | ✅（实时） |

---

## ⚠️ 仓库权限说明

**小八爪的访问权限**：

| 仓库 | 读取 | 写入 | 同步 | 备注 |
|------|------|------|------|------|
| collab-knowledge-base | ✅ | ✅ | ✅ | 自己的记忆仓库 |
| whale-workspace | ❌ | ❌ | ❌ | 🔒 私有仓库（403 Forbidden） |
| agent-collaboration | ✅ | ✅ | ✅ | 协作仓库（双方共享） |

**协作方式**：
- ✅ 小八爪和小鲸鱼通过 `agent-collaboration` 仓库协作
- ✅ 双方的记忆仓库独立管理
- ✅ 协作成果存储在 `agent-collaboration/chat-history/`

---

## 可用模型资源

### Claude Pro
- **类型**：大模型
- **特点**：顶级推理能力，复杂分析
- **适用**：战略规划、复杂问题分析、高质量写作

### maxmini M2.5
- **类型**：轻量级模型
- **特点**：待了解
- **适用**：轻量级任务

### volcengine-plan（火山引擎）
- **包含模型**：doubao系列、glm-4.7、ark-code-latest
- **doubao-seed-2.0-code**：代码能力强
- **glm-4.7**：通用能力均衡
- **ark-code-latest**：最新代码模型

### DeepSeek API
- **deepseek-reasoner**：推理能力强，适合分析、算法
- **deepseek-chat**：对话流畅，适合一般任务、代码

---

## 刘氏集团飞书知识库

**目标**：积累集团知识，成为小八爪和所有智能体的成长宝典

**文档结构**：
- 麻将小程序作战室产出
- 科研研究团队产出
- 转行咨询团队产出
- 集团运营记录

---

_2026-03-14 08:08 更新 - 确认小鲸鱼仓库地址：whale-workspace_
_2026-03-14 07:52 更新 - 新增三个仓库清单_
_2026-03-08 更新_
