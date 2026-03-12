# 教训6：Git Token安全管理

**错误类型**：安全风险
**严重程度**：🔴 高（敏感信息泄露风险）
**创建时间**：2026-03-12 23:47

---

## 问题场景

当需要提供GitHub Personal Access Token给智能体时，如何安全管理？

---

## ⚠️ 风险分析

### **错误做法**：
- ❌ 在飞书群发送Token
- ❌ 记录到MEMORY.md等公开文件
- ❌ 提交到GitHub仓库
- ❌ 明文保存到配置文件

### **后果**：
- 🔴 Token泄露，仓库被恶意修改
- 🔴 凭证被盗用，影响GitHub账户安全
- 🔴 敏感信息被公开访问

---

## ✅ 正确做法

### **1. Token创建流程**

#### **步骤**：
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 设置：
   - Note: `小八爪-OpenClaw-Workspace`
   - Expiration: `No expiration`（或按需设置）
   - 权限：只勾选 `repo`（完整仓库访问）
4. 点击 "Generate token"
5. **立即复制Token**（只显示一次！）

#### **Token格式**：
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### **2. Token传递方式**（安全）

#### **方式1：飞书私聊**（推荐）⭐⭐⭐⭐⭐
```
✅ 1对1私聊小刘
✅ 我接收后立即配置到本地
✅ 不记录到任何公开文件
✅ 配置到Git凭证存储（osxkeychain）
```

#### **方式2：本地文件**（备选）
```bash
# 创建临时文件（不提交到Git）
echo "ghp_xxx" > ~/.openclaw/.git-token-temp

# 我读取后立即删除
# 配置到Git
# 删除临时文件
```

#### **❌ 禁止方式**：
- ❌ 飞书群发送
- ❌ 提交到GitHub
- ❌ 记录到MEMORY.md
- ❌ 记录到HEARTBEAT.md
- ❌ 保存到知识库

---

### **3. Token配置流程**

#### **接收Token后，我会执行**：

```bash
# 1. 配置Git凭证存储
git config --global credential.helper osxkeychain

# 2. 设置remote URL（带Token）
git remote set-url origin https://<TOKEN>@github.com/Gdragonleo/openclaw-knowledge-base.git

# 3. 测试推送
git push origin main

# 4. 验证成功后，移除URL中的Token（安全）
git remote set-url origin https://github.com/Gdragonleo/openclaw-knowledge-base.git

# 5. 下次push时，Mac会自动从osxkeychain读取凭证
```

#### **关键点**：
- ✅ Token只存储在Mac的osxkeychain
- ✅ 不记录到任何文件
- ✅ 不提交到Git
- ✅ 自动加密管理

---

### **4. Token权限最小化**

#### **推荐权限**：
```
✅ repo（完整仓库访问）
   - repo:status
   - repo_deployment
   - public_repo
   - repo:invite
   - security_events
```

#### **不需要的权限**：
```
❌ workflow
❌ write:packages
❌ delete:packages
❌ admin:org
❌ gist
```

**原则**：最小权限原则，只给必需权限！

---

### **5. Token生命周期管理**

#### **定期轮换**：
- ⏰ 每3个月更换一次Token
- ⏰ 发现泄露立即撤销并重新生成

#### **撤销Token**：
1. 访问：https://github.com/settings/tokens
2. 找到对应Token
3. 点击 "Delete" 或 "Regenerate"

#### **更新Token**：
```bash
# 删除旧凭证
git credential-osxkeychain erase
host=github.com
protocol=https

# 重新配置新Token
# [按流程3重新配置]
```

---

## 🛡️ 安全检查清单

### **创建Token时**：
- [ ] 只勾选必需权限（repo）
- [ ] 设置合理的过期时间
- [ ] 立即复制保存

### **传递Token时**：
- [ ] 使用私聊，不在群发送
- [ ] 不记录到公开文件
- [ ] 不提交到Git仓库

### **配置Token时**：
- [ ] 配置到osxkeychain（自动加密）
- [ ] 不保存到配置文件
- [ ] 验证推送成功

### **使用Token时**：
- [ ] 定期检查权限
- [ ] 定期更换（3个月）
- [ ] 发现异常立即撤销

---

## 📋 事故响应

### **如果Token泄露**：

#### **立即行动**：
1. **撤销Token**：
   - 访问：https://github.com/settings/tokens
   - 立即删除泄露的Token

2. **重新生成**：
   - 创建新Token
   - 按流程重新配置

3. **检查仓库**：
   - 查看最近的commit
   - 确认没有恶意修改
   - 必要时回滚

4. **通知用户**：
   - 告知Token已泄露
   - 说明已采取的措施
   - 提供新Token的安全传递方式

---

## 🔒 安全原则

```
1. 最小权限原则：只给必需权限
2. 最短暴露原则：Token不记录、不公开
3. 定期轮换原则：3个月更换一次
4. 安全传递原则：私聊、临时文件
5. 立即响应原则：发现泄露立即撤销
```

---

## 📝 记录到错误库

**原因**：防止未来重犯Token泄露错误

**预防规则**：
- 🚫 Token **绝不**记录到MEMORY.md、HEARTBEAT.md等公开文件
- 🚫 Token **绝不**在飞书群发送
- 🚫 Token **绝不**提交到Git仓库
- ✅ Token **只能**私聊传递
- ✅ Token **只能**存储在osxkeychain
- ✅ Token **必须**定期更换（3个月）

---

## 🆔 相关文件

- **错误库**：`skills/error-lessons/lessons/git-token-security.md`
- **MEMORY.md**：⚠️ 不记录Token（安全）
- **HEARTBEAT.md**：⚠️ 不记录Token（安全）
- **Git配置**：✅ osxkeychain（自动管理）

---

**创建时间**：2026-03-12 23:47
**创建者**：小八爪 🐙
**严重程度**：🔴 高（安全风险）
**状态**：✅ 已形成规则
