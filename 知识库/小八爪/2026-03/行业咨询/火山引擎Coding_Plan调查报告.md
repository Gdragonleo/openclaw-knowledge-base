# 火山引擎 Coding Plan 使用范围调查报告

**调查时间**：2026-03-11  
**调查目的**：确认火山引擎 Coding Plan 是否可以用于 OpenClaw  
**结论**：✅ **可以用于 OpenClaw**

---

## 🔍 核心发现

### 1. Coding Plan 兼容 OpenAI API 协议

**来源**：2026年2月13日技术博客  
**原文**：
> "火山方舟 Coding Plan 兼容 OpenAI API 协议，接入 OpenClaw 非常丝滑。"

**关键信息**：
- ✅ Coding Plan 提供标准 API 接口
- ✅ 兼容 OpenAI API 协议
- ✅ 可以在第三方系统（如 OpenClaw）中使用

---

### 2. Coding Plan 的 Base URL

**兼容 OpenAI 接口协议的 Base URL**：
```
https://ark.cn-beijing.volces.com/api/coding/v3
```

**兼容 Anthropic 接口协议的 Base URL**：
```
https://ark.cn-beijing.volces.com/api/coding
```

---

### 3. Coding Plan 包含的模型

根据火山引擎官方文档（2026年2月更新），Coding Plan 套餐包含：

- ✅ **Doubao-Seed-2.0-Code**（豆包代码模型）
- ✅ **GLM-4.7**（智谱 GLM）
- ✅ **Doubao-Seed-2.0-Pro**（豆包专业版）
- ✅ **Auto 智能调度模式**（自动选择最优模型）

---

## 📋 如何在 OpenClaw 中配置 Coding Plan

### 步骤1：订阅 Coding Plan

1. 访问：https://www.volcengine.com/activity/codingplan
2. 选择套餐（Lite 或 Pro）
3. 完成订阅

### 步骤2：获取 API Key

1. 登录火山方舟控制台：https://ark.cn-beijing.volces.com
2. 进入"API Key 管理"页面
3. 创建并复制 API Key

### 步骤3：在 OpenClaw 中配置

**方式A：通过 Web UI 配置**（推荐）

1. 打开 OpenClaw Web UI
2. 进入 `Settings -> Config -> Authentication`
3. 选择 "Raw" 方式查看配置
4. 添加以下配置：

```json
{
  "providers": {
    "volcengine": {
      "baseUrl": "https://ark.cn-beijing.volces.com/api/coding/v3",
      "apiKey": "你的API_Key",
      "models": [
        "doubao-seed-2.0-code",
        "glm-4.7",
        "doubao-seed-2.0-pro"
      ]
    }
  },
  "agents": {
    "default": {
      "model": "doubao-seed-2.0-code",
      "provider": "volcengine"
    }
  }
}
```

**方式B：直接修改配置文件**

编辑 `~/.openclaw/config.json`，添加上述配置。

---

## ⚠️ 重要提示

### 1. Coding Plan ≠ 官方工具限制

**与 Kimi Code 不同**：
- ❌ Kimi Code 订阅：只能在 Kimi 官方产品使用
- ✅ Coding Plan 订阅：**可以在第三方系统使用**（包括 OpenClaw、Claude Code、OpenCode 等）

**原因**：
- Coding Plan 提供标准 API 接口
- 兼容 OpenAI API 协议
- 是订阅制 API 服务，不是产品订阅

---

### 2. 套餐对比

| 套餐 | 价格 | 适用场景 |
|------|------|----------|
| **Lite** | 约 ¥99/月 | 个人开发、轻量使用 |
| **Pro** | 约 ¥299/月 | 团队协作、重度使用 |

**建议**：
- 如果只是给小鲸鱼用 → Lite 套餐足够
- 如果要多智能体并行 → Pro 套餐

---

### 3. 模型选择建议

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| **doubao-seed-2.0-code** | 代码能力强，速度快 | 日常编程、代码审查 |
| **glm-4.7** | 通用能力均衡 | 对话、写作、分析 |
| **doubao-seed-2.0-pro** | 推理能力强 | 复杂任务、深度分析 |
| **Auto** | 自动选择最优模型 | 不确定场景 |

---

## 📚 参考资料

### 官方文档
- 火山方舟 Coding Plan 文档：https://www.volcengine.com/docs/82379/1925114
- 快速开始：https://www.volcengine.com/docs/82379/1928261

### 第三方集成案例
1. **OpenClaw 集成教程**（2026年2月13日）
   - 明确提到"接入 OpenClaw 非常丝滑"
   - 提供完整配置步骤

2. **OpenCode 中文文档**
   - 提供火山引擎对接指南
   - 适用于所有兼容 OpenAI API 的系统

3. **Claude Code 集成**（2026年1月17日）
   - 用户成功在 Claude Code 中使用 Coding Plan
   - 证明第三方集成可行性

---

## 🎯 结论

### ✅ Coding Plan 可以用于 OpenClaw

**证据**：
1. ✅ 官方文档明确支持 OpenAI API 协议
2. ✅ 多个用户成功案例（OpenClaw、Claude Code、OpenCode）
3. ✅ 提供标准 API Key 和 Base URL
4. ✅ 不是产品订阅限制，而是 API 服务订阅

### 🔧 配置要点

1. **Base URL**：`https://ark.cn-beijing.volces.com/api/coding/v3`
2. **API Key**：从火山方舟控制台获取
3. **协议**：兼容 OpenAI API
4. **模型**：doubao-seed-2.0-code、glm-4.7、doubao-seed-2.0-pro

### 💡 建议

**对于小鲸鱼（Kimi K2.5 无法使用的情况）**：
- ✅ 使用 Coding Plan + doubao-seed-2.0-code
- ✅ 成本低（Lite 套餐 ¥99/月）
- ✅ 能力强（代码能力优秀）
- ✅ 无第三方限制

---

**调查者**：小八爪 🐙  
**报告生成时间**：2026-03-11 11:10  
**数据来源**：百度搜索、DuckDuckGo 搜索、官方文档、技术博客

---

## 附录：完整配置示例

```json
{
  "providers": {
    "volcengine": {
      "baseUrl": "https://ark.cn-beijing.volces.com/api/coding/v3",
      "apiKey": "你的API_Key_从控制台获取",
      "models": [
        "doubao-seed-2.0-code",
        "glm-4.7",
        "doubao-seed-2.0-pro"
      ]
    }
  },
  "agents": {
    "default": {
      "model": "doubao-seed-2.0-code",
      "provider": "volcengine",
      "temperature": 0.7,
      "maxTokens": 4096
    },
    "小鲸鱼": {
      "model": "doubao-seed-2.0-pro",
      "provider": "volcengine",
      "temperature": 0.7,
      "maxTokens": 8192
    }
  }
}
```

---

_本报告基于公开资料整理，具体配置请以火山引擎官方文档为准。_
