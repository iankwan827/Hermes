# 2026-07-03 同步冲突解决记录

## 场景
Windows 端本地有 9 个文件变更（config.yaml, cron/jobs.json, memories/MEMORY.md, skills/.usage.json, douyin-data-check 相关, douyin-download, browser-access），远程 Mac 端有 1 个 commit（browser-access skill 新增 + 大规模 skill 清理）。

## 尝试 1：Rebase（失败）
```bash
git pull origin main --rebase
```
结果：7 个文件冲突（config.yaml, cron/jobs.json, memories/MEMORY.md, skills/.usage.json, douyin-data-check/SKILL.md, 发展日志.md, douyin-download/SKILL.md），每个文件多处 conflict markers。

原因：rebase 在每个本地 commit 上重放远程变更，当两端都改了相同文件时产生级联冲突。

## 尝试 2：Abort + Merge（成功）
```bash
git rebase --abort
git merge origin/main --no-commit --no-ff
# 自动合并成功，无冲突
git commit -m "merge: 合并远程Mac端更新 2026-07-03"
git push origin main
```

## 教训
- Rebase 适合单边修改的线性历史
- Merge 适合两边都有独立修改的分叉历史
- 对于每日自动同步场景，merge 是更安全的选择