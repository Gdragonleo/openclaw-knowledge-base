# 每2天同步 workspace 到 Gitee（旧 GitHub 版本已停用）

## 状态
- 本文件保留作历史说明
- 原 GitHub 同步逻辑已停用
- 当前正式使用的是 **Gitee 同步链路**

## 当前正式脚本
- `/Users/danxiong/.openclaw/workspace/scripts/cron/sync_workspace_to_gitee.sh`

## 当前正式任务
- 目标仓库：`~/collab-knowledge-base`
- 同步方式：`rsync + git add + git commit + git push`
- 安全排除：`.git` / `node_modules` / `.DS_Store` / `config/gitee_token.sh`
- 失败处理：push 失败自动重试一次
- 无变更处理：记录 `NO_CHANGES_TO_COMMIT`

## 说明
这里不再维护 GitHub 旧流程，避免后续定时任务继续读取到过时配置。

**最后更新**：2026-03-16 第三轮收口
