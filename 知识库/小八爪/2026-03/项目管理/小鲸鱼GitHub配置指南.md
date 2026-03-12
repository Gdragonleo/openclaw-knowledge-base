# 小鲸鱼GitHub配置指南

**创建时间**：2026-03-12 21:31
**创建者**：小八爪 🐙
**用途**：配置小鲸鱼访问GitHub并同步文件

---

## 🎯 目标

让小鲸鱼（腾讯云服务器）访问GitHub，读取小八爪的文件和知识库。

---

## 📋 配置方案

### **方案1：使用HTTPS克隆（最简单）** ⭐⭐⭐⭐⭐

**适用场景**：公开仓库或个人访问令牌

#### 步骤1：在服务器上克隆仓库
```bash
# SSH连接到服务器
ssh ubuntu@118.89.197.244
密码：whale@2026

# 进入小鲸鱼工作目录
cd ~/.openclaw/workspace

# 克隆小八爪的知识库（使用HTTPS）
git clone https://github.com/Gdragonleo/openclaw-knowledge-base.git .

# 验证克隆成功
ls -la
```

#### 步骤2：配置Git用户信息
```bash
# 配置Git用户名和邮箱（用于提交）
git config --global user.name "小鲸鱼"
git config --global user.email "whale@liugroup.com"

# 验证配置
git config --list
```

#### 步骤3：设置自动同步脚本
```bash
# 创建同步脚本
cat > ~/.openclaw/sync-knowledge.sh << 'EOF'
#!/bin/bash
# 同步小八爪的知识库

cd ~/.openclaw/workspace

echo "🔄 开始同步知识库..."
git pull origin main

echo "✅ 同步完成！"
echo "📅 同步时间：$(date)"
EOF

chmod +x ~/.openclaw/sync-knowledge.sh

# 测试同步
~/.openclaw/sync-knowledge.sh
```

---

### **方案2：使用SSH密钥（更安全）** ⭐⭐⭐⭐

**适用场景**：需要推送权限或私有仓库

#### 步骤1：生成SSH密钥
```bash
# 在服务器上生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "whale@liugroup.com"

# 按三次回车（使用默认设置）

# 查看公钥
cat ~/.ssh/id_rsa.pub
```

#### 步骤2：添加到GitHub
```
1. 复制公钥内容（从 ssh-rsa 开始到 whale@liugroup.com 结束）
2. 访问 GitHub → Settings → SSH and GPG keys
3. 点击 "New SSH key"
4. 粘贴公钥内容
5. 保存
```

#### 步骤3：测试SSH连接
```bash
# 测试GitHub SSH连接
ssh -T git@github.com

# 如果显示 "Hi Gdragonleo! ..." 就成功了
```

#### 步骤4：克隆仓库（使用SSH）
```bash
cd ~/.openclaw/workspace

# 使用SSH克隆
git clone git@github.com:Gdragonleo/openclaw-knowledge-base.git .

# 验证
ls -la
```

---

## 🔄 自动同步机制

### **方案A：定时同步（推荐）**

```bash
# 添加到crontab（每30分钟同步一次）
crontab -e

# 添加以下行
*/30 * * * * /home/ubuntu/.openclaw/sync-knowledge.sh >> /home/ubuntu/.openclaw/logs/sync.log 2>&1

# 保存退出
```

### **方案B：PM2管理同步**

```bash
# 创建ecosystem.config.js
cat > ~/.openclaw/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'whale',
      script: 'openclaw',
      args: 'start',
      cwd: '/home/ubuntu/.openclaw/workspace'
    },
    {
      name: 'sync-knowledge',
      script: 'sync-knowledge.sh',
      cron_restart: '*/30 * * * *',
      autorestart: false
    }
  ]
};
EOF

# 启动
pm2 start ~/.openclaw/ecosystem.config.js

# 保存PM2配置
pm2 save
```

---

## 📂 文件结构

### 同步后的目录结构
```
~/.openclaw/workspace/
├── 知识库/
│   ├── 小八爪/
│   │   └── 2026-03/
│   │       ├── 易经/
│   │       ├── 项目管理/
│   │       └── ...
│   ├── 麻将团队/
│   ├── 科研团队/
│   └── ...
├── skills/
├── memory/
├── AGENTS.md
├── MEMORY.md
├── SOUL.md
└── USER.md
```

---

## 🔧 实用命令

### 手动同步
```bash
# 拉取最新文件
cd ~/.openclaw/workspace
git pull origin main

# 查看更新内容
git log --oneline -5

# 查看文件变更
git status
```

### 推送文件（如果有权限）
```bash
# 添加文件
git add .

# 提交
git commit -m "🤖 小鲸鱼更新：..."

# 推送
git push origin main
```

---

## 🆘 常见问题

### 问题1：Permission denied
```bash
# 检查SSH密钥
ls -la ~/.ssh/

# 重新生成密钥
ssh-keygen -t rsa -b 4096 -C "whale@liugroup.com"
```

### 问题2：Repository not found
```bash
# 检查仓库地址
git remote -v

# 更新仓库地址
git remote set-url origin https://github.com/Gdragonleo/openclaw-knowledge-base.git
```

### 问题3：Merge conflict
```bash
# 强制覆盖本地（使用远程版本）
git fetch origin
git reset --hard origin/main
```

---

## 🎯 推荐配置（快速开始）

### **完整执行脚本**：

```bash
#!/bin/bash
echo "🐙 配置小鲸鱼GitHub访问..."

# 1. 配置Git
git config --global user.name "小鲸鱼"
git config --global user.email "whale@liugroup.com"

# 2. 进入工作目录
cd ~/.openclaw/workspace

# 3. 清空现有文件（如果有）
rm -rf 知识库 skills memory *.md

# 4. 克隆小八爪的知识库
git clone https://github.com/Gdragonleo/openclaw-knowledge-base.git .

# 5. 验证克隆成功
echo "📦 克隆完成，文件列表："
ls -la

# 6. 创建同步脚本
cat > ~/.openclaw/sync-knowledge.sh << 'EOF'
#!/bin/bash
cd ~/.openclaw/workspace
git pull origin main
echo "✅ 同步完成：$(date)"
EOF

chmod +x ~/.openclaw/sync-knowledge.sh

# 7. 创建日志目录
mkdir -p ~/.openclaw/logs

# 8. 添加定时任务
(crontab -l 2>/dev/null; echo "*/30 * * * * /home/ubuntu/.openclaw/sync-knowledge.sh >> /home/ubuntu/.openclaw/logs/sync.log 2>&1") | crontab -

echo "🎉 配置完成！"
echo "📅 每30分钟自动同步"
echo "📝 日志位置：~/.openclaw/logs/sync.log"
```

---

## 📊 同步效果

### 同步后的能力
- ✅ 小鲸鱼可以读取小八爪的所有文件
- ✅ 自动每30分钟同步最新内容
- ✅ 小八爪更新知识库，小鲸鱼自动获取
- ✅ 协作中心任务可以基于最新知识

### 协作流程
```
小八爪学习新知识
    ↓
更新知识库（Mac本地）
    ↓
推送到GitHub
    ↓
小鲸鱼自动拉取（每30分钟）
    ↓
基于最新知识执行任务
```

---

## 🔗 相关链接

- **GitHub仓库**：https://github.com/Gdragonleo/openclaw-knowledge-base
- **小鲸鱼服务器**：118.89.197.244
- **协作中心**：https://bcnuqjt2v034.feishu.cn/base/CnBNbHdZnaePv4s4StLcONDXngc

---

**创建时间**：2026-03-12 21:31
**更新时间**：2026-03-12 21:31
**状态**：✅ 已完成
