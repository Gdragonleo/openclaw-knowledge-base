#!/bin/bash
set -euo pipefail

BASE="$HOME/.openclaw/workspace/skills/tender-browser-scraper"
SCRIPTS="$BASE/scripts"
OUTDIR="$BASE/output/tenders"
LOGDIR="$BASE/output/logs"
WHALE="$HOME/Desktop/项目管理平台代码/whale/whale"
REPORT_DIR="$HOME/.openclaw/workspace/知识库/招标监控"
mkdir -p "$OUTDIR" "$LOGDIR" "$REPORT_DIR"

DETAIL_OK=0

echo "[1/4] 尝试详细抓取..."
python3 - <<PY > "$LOGDIR/scrape_run.log" 2>&1
import subprocess, sys
cmd = ['node', '$SCRIPTS/scrape.js', '--site', 'cqggzy', '--max', '12', '--days', '30', '--output', '$OUTDIR']
try:
    subprocess.run(cmd, check=True, timeout=180)
    sys.exit(0)
except subprocess.TimeoutExpired:
    print('DETAIL_TIMEOUT')
    sys.exit(124)
except subprocess.CalledProcessError as e:
    print(f'DETAIL_FAILED:{e.returncode}')
    sys.exit(e.returncode)
PY
SCRAPE_EXIT=$?

if [ "$SCRAPE_EXIT" -eq 0 ]; then
  echo "✅ 详细抓取成功"
  DETAIL_OK=1
else
  echo "⚠️ 详细抓取失败，准备降级到 quick_report"
fi

if [ "$DETAIL_OK" -ne 1 ]; then
  echo "[2/4] 执行 quick_report 降级方案..."
  node "$SCRIPTS/quick_report.js" > "$LOGDIR/quick_report.log" 2>&1
  echo "✅ quick_report 完成"
else
  echo "[2/4] 跳过 quick_report（已拿到详细抓取）"
fi

echo "[3/4] 导入 whale 并生成正式报告..."
python3 "$BASE/integrate_with_whale.py" > "$LOGDIR/integrate_with_whale.log" 2>&1
cat "$LOGDIR/integrate_with_whale.log"

echo "[4/4] 生成可分享 HTML..."
cd "$WHALE"
python3 export_results.py > "$LOGDIR/export_results.log" 2>&1
cp "$WHALE/output/daily_report.html" "$REPORT_DIR/招标日报_whale.html"
cp "$WHALE/output/daily_summary.json" "$REPORT_DIR/招标日报_whale_summary.json"
cp "$WHALE/output/daily_scored_projects.json" "$REPORT_DIR/招标日报_whale_projects.json"
echo "✅ HTML 已生成: $REPORT_DIR/招标日报_whale.html"

echo "✅ 正式版流水线执行完成"
