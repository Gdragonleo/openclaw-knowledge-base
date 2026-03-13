#!/bin/bash
# 小鲸鱼部署脚本
# 服务器：118.89.197.244
# 系统：Ubuntu 22.04
# 创建时间：2026-03-12 14:51

echo "🐙 开始部署小鲸鱼..."

# ============================================
# 第一步：系统更新（5分钟）
# ============================================
echo "📦 更新系统..."
apt update
apt upgrade -y
apt install -y curl wget git vim htop net-tools

# ============================================
# 第二步：安装Node.js 18（5分钟）
# ============================================
echo "📦 安装Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# 验证安装
node -v
npm -v

# ============================================
# 第三步：安装OpenClaw和PM2（5分钟）
# ============================================
echo "🤖 安装OpenClaw和PM2..."
npm install -g openclaw
npm install -g pm2

# 验证安装
openclaw --version
pm2 --version

# ============================================
# 第四步：配置防火墙（2分钟）
# ============================================
echo "🔥 配置防火墙..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3000/tcp
ufw --force enable

# ============================================
# 第五步：创建工作目录（1分钟）
# ============================================
echo "📁 创建工作目录..."
mkdir -p ~/.openclaw/workspace
cd ~/.openclaw/workspace

# ============================================
# 第六步：克隆知识库（5分钟）
# ============================================
echo "📚 克隆知识库..."
git clone https://github.com/Gdragonleo/openclaw-knowledge-base.git .

# ============================================
# 第七步：配置小鲸鱼（10分钟）
# ============================================
echo "🐳 配置小鲸鱼..."

# 初始化OpenClaw配置
openclaw config init

# 设置基本信息
openclaw config set agent.name "小鲸鱼"
openclaw config set agent.model "kimi-k2.5"
openclaw config set agent.role "首席技术官"

# 配置飞书（需要替换为实际的AppID和AppSecret）
# 小刘需要提供：
# openclaw config set feishu.appId "你的AppID"
# openclaw config set feishu.appSecret "你的AppSecret"

# 配置协作中心
openclaw config set collaboration.center "https://bcnuqjt2v034.feishu.cn/base/CnBNbHdZnaePv4s4StLcONDXngc"
openclaw config set collaboration.tableId "tblcxFySU7AaXjee"

# ============================================
# 第八步：启动服务（2分钟）
# ============================================
echo "🚀 启动小鲸鱼..."

# 创建启动脚本
cat > ~/.openclaw/start-whale.sh << 'EOF'
#!/bin/bash
cd ~/.openclaw/workspace
openclaw start
EOF

chmod +x ~/.openclaw/start-whale.sh

# 使用PM2管理
pm2 start ~/.openclaw/start-whale.sh --name "whale"

# 保存PM2配置
pm2 save

# 设置开机自启
pm2 startup

# ============================================
# 第九步：验证部署（2分钟）
# ============================================
echo "✅ 验证部署..."

# 检查PM2状态
pm2 status

# 检查进程
ps aux | grep openclaw

# 检查日志
pm2 logs whale --lines 20

echo "🎉 小鲸鱼部署完成！"
echo "📊 查看状态：pm2 status"
echo "📝 查看日志：pm2 logs whale"
echo "🔍 查看资源：htop"
