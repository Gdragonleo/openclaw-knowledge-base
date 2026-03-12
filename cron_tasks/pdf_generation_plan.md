# 📄 PDF自动生成方案

**创建时间**：2026-03-13 00:30
**创建者**：小八爪 🐙
**用途**：每天自动生成招标报告PDF版本

---

## 🎯 目标

**每天9:00自动生成招标报告，同时输出两种格式**：
- ✅ Markdown（现有）
- ✅ PDF（新增）

---

## 📋 实现方案

### **方案1：使用Pandoc**（推荐）⭐⭐⭐⭐⭐

#### **优势**：
```
✅ 开源免费
✅ 支持中文
✅ 格式标准
✅ Mac已预装或易安装
✅ 命令行操作简单
```

#### **安装**：
```bash
# 检查是否安装
which pandoc

# 如果未安装
brew install pandoc

# 安装中文字体支持
brew install basictex
sudo tlmgr install xecjk
```

#### **转换命令**：
```bash
# 基础转换
pandoc 招标日报_2026-03-13.md -o 招标日报_2026-03-13.pdf

# 带样式的转换
pandoc 招标日报_2026-03-13.md \
  -o 招标日报_2026-03-13.pdf \
  --pdf-engine=xelatex \
  -V mainfont="PingFang SC" \
  -V geometry:margin=1in \
  --toc \
  --toc-depth=3 \
  -V colorlinks=true

# 输出路径
输出到：知识库/科研团队/2026/03月/PDF/
```

---

### **方案2：使用Markdown-to-PDF库** ⭐⭐⭐⭐

#### **优势**：
```
✅ Node.js原生
✅ 样式可控
✅ 适合自动化
```

#### **安装**：
```bash
npm install -g md-to-pdf
```

#### **使用**：
```bash
md-to-pdf 招标日报_2026-03-13.md \
  --pdf-options "{\"format\": \"A4\", \"margin\": \"20mm\"}"
```

---

### **方案3：使用Python WeasyPrint** ⭐⭐⭐⭐

#### **优势**：
```
✅ Python生态
✅ 功能强大
✅ CSS样式支持
```

#### **安装**：
```bash
pip3 install weasyprint markdown
```

#### **使用**：
```python
import markdown
from weasyprint import HTML

# 读取Markdown
with open('招标日报.md', 'r') as f:
    md_content = f.read()

# 转HTML
html_content = markdown.markdown(md_content)

# 转PDF
HTML(string=html_content).write_pdf('招标日报.pdf')
```

---

## 🚀 推荐实现流程（方案1）

### **步骤1：安装Pandoc**（1分钟）
```bash
# 检查安装
which pandoc

# 如果未安装
brew install pandoc

# 验证
pandoc --version
```

### **步骤2：创建转换脚本**
```bash
#!/bin/bash
# 文件：scripts/convert_to_pdf.sh

# 输入：招标日报Markdown文件
INPUT_MD=$1
OUTPUT_PDF=$2

# 使用Pandoc转换
pandoc "$INPUT_MD" \
  -o "$OUTPUT_PDF" \
  --pdf-engine=xelatex \
  -V mainfont="PingFang SC" \
  -V geometry:margin=1in \
  -V colorlinks=true \
  --metadata title="招标日报" \
  2>&1

if [ $? -eq 0 ]; then
  echo "✅ PDF生成成功：$OUTPUT_PDF"
else
  echo "❌ PDF生成失败"
  exit 1
fi
```

### **步骤3：集成到定时任务**
```bash
# 修改：cron_tasks/daily_tender_report.md

任务4：生成PDF版本（新增）
```bash
# 1. 生成Markdown报告
生成招标日报 > 知识库/科研团队/2026/03月/招标日报_2026-03-13.md

# 2. 转换为PDF
~/.openclaw/workspace/scripts/convert_to_pdf.sh \
  知识库/科研团队/2026/03月/招标日报_2026-03-13.md \
  知识库/科研团队/2026/03月/PDF/招标日报_2026-03-13.pdf

# 3. 验证PDF
if [ -f "知识库/科研团队/2026/03月/PDF/招标日报_2026-03-13.pdf" ]; then
  echo "✅ PDF生成成功"
  ls -lh 知识库/科研团队/2026/03月/PDF/招标日报_2026-03-13.pdf
fi
```

---

## 📊 PDF样式配置

### **基础样式**：
```yaml
格式：A4
边距：上下左右各25mm
字体：PingFang SC（Mac默认）
标题：自动编号
链接：蓝色高亮
表格：带边框
```

### **高级样式**（可选）：
```bash
# 自定义CSS样式
pandoc 招标日报.md \
  -o 招标日报.pdf \
  --pdf-engine=xelatex \
  --css=styles/report.css \
  -V mainfont="PingFang SC" \
  -V monofont="Menlo"
```

---

## 📂 目录结构

```
知识库/科研团队/2026/03月/
├── 招标日报_2026-03-13.md（Markdown版本）
├── 招标日报_2026-03-14.md
├── 招标日报_2026-03-15.md
└── PDF/（PDF版本）
    ├── 招标日报_2026-03-13.pdf
    ├── 招标日报_2026-03-14.pdf
    └── 招标日报_2026-03-15.pdf
```

---

## 🔧 飞书上传配置

### **方式1：上传PDF到飞书云文档**
```bash
# 使用飞书API上传
curl -X POST "https://open.feishu.cn/open-apis/drive/v1/files/upload" \
  -H "Authorization: Bearer $FEISHU_ACCESS_TOKEN" \
  -F "file=@招标日报_2026-03-13.pdf" \
  -F "file_name=招标日报_2026-03-13.pdf" \
  -F "parent_token=fldxxx" # 云空间文件夹token
```

### **方式2：生成飞书文档链接**
```bash
# 上传成功后返回
{
  "file_token": "xxx",
  "url": "https://feishu.cn/file/xxx",
  "name": "招标日报_2026-03-13.pdf"
}

# 将链接发送到群
飞书机器人发送 "今日招标报告PDF版本：[链接]"
```

---

## ⏰ 明天执行计划

### **时间安排**：
```
09:00 - 开始生成招标报告
09:05 - Markdown报告生成完成
09:06 - 开始转换PDF（预计2-3分钟）
09:09 - PDF生成完成
09:10 - 上传飞书云文档
09:11 - 发送群通知（附Markdown链接 + PDF链接）
```

### **产出**：
```
1. ✅ Markdown报告（现有）
2. ✅ PDF报告（新增）
3. ✅ 飞书云文档链接（新增）
4. ✅ 群通知（Markdown链接 + PDF链接）
```

---

## 📋 群通知格式

### **新通知模板**：
```
📋 招标日报 - 2026-03-13

📊 统计：
- 总项目：120个
- 重点推荐：15个
- 金额范围：50-5000万

🔗 查看方式：
1️⃣ 在线查看：[GitHub链接]
2️⃣ PDF版本：[飞书云文档链接]

重点推荐项目：
1. ⭐ [重庆] XX边坡监测项目（300万）
2. ⭐ [四川] XX勘察项目（150万）
3. ⭐ [贵州] XX监测项目（200万）

——小八爪 🐙 自动生成
```

---

## ✅ 验证清单

### **PDF生成成功标准**：
```
[ ] PDF文件已生成
[ ] 文件大小合理（100KB-1MB）
[ ] 中文字体正常显示
[ ] 表格格式正确
[ ] 链接可点击
[ ] 可正常打开
```

### **上传成功标准**：
```
[ ] 飞书云文档已上传
[ ] 链接可访问
[ ] 权限配置正确（可查看）
[ ] 群通知已发送
```

---

## 🛠️ 备用方案

### **如果Pandoc失败**：

#### **备用1：使用md-to-pdf**
```bash
npm install -g md-to-pdf
md-to-pdf 招标日报.md
```

#### **备用2：使用Python**
```python
# 预先准备好Python脚本
python3 scripts/md_to_pdf.py 招标日报.md
```

#### **备用3：手动转换**
```
1. 打开Markdown文件
2. 使用Mac预览导出PDF
3. 上传到飞书
```

---

## 💰 成本分析

| 项目 | 成本 | 说明 |
|------|------|------|
| Pandoc | **免费** | 开源软件 |
| 飞书云存储 | **免费** | 企业版足够 |
| 总成本 | **¥0/月** | 完全免费 |

---

## 📝 配置文件

### **脚本位置**：
```
/Users/danxiong/.openclaw/workspace/scripts/convert_to_pdf.sh
```

### **配置位置**：
```
/Users/danxiong/.openclaw/workspace/cron_tasks/daily_tender_report.md
```

### **输出位置**：
```
/Users/danxiong/.openclaw/workspace/知识库/科研团队/2026/03月/PDF/
```

---

## 🚀 立即行动

### **明天6:00自动执行**：
```
✅ 早间学习任务中
✅ 先安装Pandoc
✅ 测试PDF生成
✅ 准备明天9:00正式使用
```

### **明天9:00正式输出**：
```
✅ Markdown报告（现有）
✅ PDF报告（新增）
✅ 飞书云文档链接（新增）
✅ 群通知（双格式链接）
```

---

## 🎯 预期效果

### **明天收到**：
```
1. ✅ Markdown报告（在线查看）
2. ✅ PDF报告（下载查看，格式标准）
3. ✅ 飞书云文档链接（分享给同事）
```

### **同事体验**：
```
✅ 电脑端：在线查看Markdown
✅ 手机端：下载PDF查看
✅ 分享：发送飞书云文档链接
✅ 打印：PDF格式标准
```

---

**创建时间**：2026-03-13 00:30
**执行时间**：2026-03-13 06:00（准备）+ 09:00（正式）
**状态**：⏳ 已计划，明天执行

---

**小八爪 🐙**
