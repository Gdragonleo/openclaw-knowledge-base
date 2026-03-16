#!/bin/bash
set -euo pipefail

SRC="$HOME/.openclaw/workspace/"
DST="$HOME/collab-knowledge-base"
COMMIT_MSG="🔄 定期同步workspace"

echo "[1/5] 进入仓库"
cd "$DST"

echo "[2/5] 同步前状态"
git status --short || true

echo "[3/5] rsync 同步"
rsync -av \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='.DS_Store' \
  --exclude='config/gitee_token.sh' \
  "$SRC" ./

echo "[4/5] 检查变更"
STATUS=$(git status --short)
printf '%s\n' "$STATUS"
if [ -z "$STATUS" ]; then
  echo "NO_CHANGES_TO_COMMIT"
  exit 0
fi

git add .
git commit -m "$COMMIT_MSG" || true

echo "[5/5] 推送"
if git push origin master; then
  echo "PUSH_OK"
  exit 0
fi

echo "PUSH_RETRY"
sleep 3
git push origin master

echo "PUSH_OK_AFTER_RETRY"
