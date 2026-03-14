# 🔐 配置文件目录

本目录存放敏感配置信息，如 API Token、密钥等。

---

## ⚠️ 安全提示

**此目录不应提交到 Git！**

已添加到 `.gitignore`：
```
config/
*.token
*.key
*_token.sh
```

---

## 📁 配置文件列表

| 文件 | 说明 | 用途 |
|------|------|------|
| `gitee_token.sh` | Gitee API Token | 创建 Issues、推送仓库 |

---

## 🔧 使用方法

### 方法1：source 配置文件
```bash
source ~/.openclaw/workspace/config/gitee_token.sh
# 然后可以使用 $GITEE_TOKEN
```

### 方法2：在脚本中引用
```bash
#!/bin/bash
source ~/.openclaw/workspace/config/gitee_token.sh
curl -H "Authorization: token $GITEE_TOKEN" ...
```

---

**创建时间**：2026-03-14
**维护者**：小八爪 🐙
