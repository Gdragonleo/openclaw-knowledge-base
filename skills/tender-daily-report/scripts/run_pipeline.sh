#!/bin/bash
# ============================================================
# 招标日报流水线 - tender-daily-report v2.0
# 功能：爬取 → 硬筛选 → 7维度评分 → 报告生成 → 按日期归档 → 验证
# ============================================================
set -euo pipefail

# ---- 路径 ----
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE="${HOME}/.openclaw/workspace"
CONFIG_DIR="${SKILL_DIR}/config"
SCRAPER_DIR="${WORKSPACE}/skills/tender-browser-scraper"
DATE_STR="$(date +%Y-%m-%d)"

# 加载配置
settings() { cat "${CONFIG_DIR}/settings.json"; }
OUTPUT_BASE="${WORKSPACE}/$(settings | python3 -c "import sys,json;print(json.load(sys.stdin)['output_dir'])")"
DAYS_RANGE="$(settings | python3 -c "import sys,json;print(json.load(sys.stdin)['days_range'])")"
MAX_ITEMS="$(settings | python3 -c "import sys,json;print(json.load(sys.stdin)['max_items'])")"
ARCHIVE_DIR="${OUTPUT_BASE}/历史报告"

# 日期归档目录
DATE_DIR="${OUTPUT_BASE}/${DATE_STR}"
LATEST_DIR="${OUTPUT_BASE}/_latest"

mkdir -p "$DATE_DIR" "$LATEST_DIR" "$ARCHIVE_DIR"

LOG_FILE="${DATE_DIR}/pipeline_${DATE_STR}.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "========================================="
echo "🚀 招标日报流水线启动 - ${DATE_STR}"
echo "========================================="

# ---- [1/4] 爬取 ----
echo ""
echo "[1/4] 爬取招标公告..."
SCRAPE_OK=0

if [ -d "${SCRAPER_DIR}/scripts" ]; then
  python3 - <<PY > "${DATE_DIR}/scrape.log" 2>&1
import subprocess, sys
cmd = ['node', '${SCRAPER_DIR}/scripts/scrape.js', '--site', 'cqggzy',
       '--max', '${MAX_ITEMS}', '--days', '${DAYS_RANGE}',
       '--output', '${SCRAPER_DIR}/output/tenders']
try:
    subprocess.run(cmd, check=True, timeout=180)
    print('SCRAPE_OK')
    sys.exit(0)
except subprocess.TimeoutExpired:
    print('SCRAPE_TIMEOUT')
    sys.exit(124)
except subprocess.CalledProcessError as e:
    print(f'SCRAPE_FAILED:{e.returncode}')
    sys.exit(e.returncode)
PY
  if grep -q "SCRAPE_OK" "${DATE_DIR}/scrape.log"; then
    echo "✅ 爬取成功"
    SCRAPE_OK=1
  else
    echo "⚠️ 爬取失败，准备降级"
  fi
else
  echo "⚠️ 爬虫目录不存在，跳过爬取"
fi

# ---- [2/4] 降级方案 ----
if [ "$SCRAPE_OK" -ne 1 ]; then
  echo ""
  echo "[2/4] 执行 quick_report 降级方案..."
  if [ -f "${SCRAPER_DIR}/scripts/quick_report.js" ]; then
    node "${SCRAPER_DIR}/scripts/quick_report.js" > "${DATE_DIR}/quick_report.log" 2>&1
    echo "✅ quick_report 完成"
  else
    echo "⚠️ quick_report.js 不存在，跳过"
  fi
else
  echo "[2/4] 跳过降级方案（爬取已成功）"
fi

# ---- [3/4] 评分 + 报告 ----
echo ""
echo "[3/4] 7维度评分 + 报告生成..."
python3 "${SCRIPT_DIR}/score_and_report.py" \
  --config "${CONFIG_DIR}" \
  --output-dir "${DATE_DIR}" \
  --scraper-dir "${SCRAPER_DIR}" \
  --date "${DATE_STR}" \
  > "${DATE_DIR}/score_report.log" 2>&1

if [ $? -eq 0 ]; then
  echo "✅ 评分+报告生成成功"
else
  echo "❌ 评分+报告生成失败"
  exit 1
fi

# ---- [4/4] 归档 + 验证 ----
echo ""
echo "[4/4] 按日期归档 + 验证产物..."

# 验证
python3 "${SCRIPT_DIR}/verify_outputs.py" \
  --dir "${DATE_DIR}" \
  --date "${DATE_STR}" \
  > "${DATE_DIR}/verify.log" 2>&1

if [ $? -eq 0 ]; then
  echo "✅ 验证通过"
else
  echo "⚠️ 验证有警告（产物可能不完整）"
fi

# 更新 _latest 快捷入口
rm -rf "$LATEST_DIR"/*
for f in "${DATE_DIR}"/*; do
  [ -f "$f" ] && ln -sf "$f" "${LATEST_DIR}/$(basename "$f")"
done
echo "✅ _latest 快捷入口已更新"

# 归档旧报告到历史目录
for old_dir in "${OUTPUT_BASE}"/202*; do
  [ -d "$old_dir" ] || continue
  old_date="$(basename "$old_dir")"
  [ "$old_date" = "$DATE_STR" ] && continue
  [ "$old_date" = "_latest" ] && continue
  [ "$old_date" = "历史报告" ] && continue
  target="${ARCHIVE_DIR}/${old_date}"
  [ -d "$target" ] || mv "$old_dir" "$target"
done
echo "✅ 历史报告已归档"

# ---- 完成 ----
echo ""
echo "========================================="
echo "🎉 流水线完成 - ${DATE_STR}"
echo "========================================="
echo "📁 产物目录: ${DATE_DIR}"
echo "📁 快捷入口: ${LATEST_DIR}"
echo "📋 日志文件: ${LOG_FILE}"
echo ""
ls -la "${DATE_DIR}"/*.md "${DATE_DIR}"/*.json 2>/dev/null || true
