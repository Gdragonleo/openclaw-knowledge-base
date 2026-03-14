# 在 macOS 上配置 Gitee

**创建时间**：2026-03-13 23:59  
**创建者**：小八爪 🐙

---

## 📋 配置步骤

### 1️⃣ 安装 Gitee 客户端

**方式1：Homebrew**
```bash
brew install gitee
```

**方式2：下载安装包**
- 记问：https://gitee.com/homebrew/downloads/
- 下载对应的 macOS 版本

---

### 2️⃣ 配置 Gitee

**步骤**：
1. 打开终端
2. 运行：`gitee config`
3. 设置用户名和邮箱
4. 设置默认编辑器（可以用 vim 或 nano）

---

### 3️⃣ 鷻加远程仓库

```bash
# 克隆 Gitee 仓库
git clone https://gitee.com/whaleandcollab/agent-collaboration.git

# 进入仓库
cd agent-collaboration

# 查看状态
git status
```

---

### 4️⃣ 设置 GitHub remote

```bash
# 添加 GitHub 远程仓库
git remote add github https://github.com/Gdragonleo/agent-collaboration.git

# 设置上游
git push -u origin master

# 后续推送
git push
```

---

## ⚠️ 重要提示

**Gitee vs GitHub**：
- **Gitee**：国内服务器， 速度快， 访问稳定
- **GitHub**：国外服务器
  可能需要科学上网
  速度较慢

**推荐**：优先使用 Gitee

---

## 📌 我的仓库地址

**Gitee**：https://gitee.com/whaleandcollab/agent-collaboration.git  
**GitHub**：https://github.com/Gdragonleo/agent-collaboration（待创建）

---

## 🎯 定时任务配置（待你完成配置）

**创建文件**：`~/.openclaw/cron/gitee-collab-check.sh`

**添加执行权限**：
```bash
chmod +x ~/.openclaw/cron/gitee-collab-check.sh
```

**添加到 crontab**：
```bash
crontab -e
0 */ 2 * * * * /Users/danxiong/.openclaw/cron/gitee-collab-check.sh
```

---

**说明**：
- 每小时第2分钟执行
- 自动查询 Gitee Issues
- 处理任务后关闭 Issue

---

_准备就绪！告诉我你完成了配置！_ 🐙