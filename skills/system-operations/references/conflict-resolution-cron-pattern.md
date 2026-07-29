# Cron 模式冲突解决模式

## 场景：2026-07-27 Windows-Mac 双向同步

### 时间线
1. `git add` + `git commit` — 本地 23 个文件变更（+521/-770行）
2. `git push` → 被拒（Mac 端有新提交 a4b4ef8）
3. `git pull --rebase` → 12 个文件冲突（10个 yulu.md + jobs.json + 发展日志.md）
4. `git rebase --abort` → 回退到合并前状态
5. `git merge origin/main -X theirs` → 自动解决所有冲突（仅 1 文件有实质变更）
6. `git push` → 再次被拒（Mac 端又有新 push）
7. 再次 `git pull --rebase` → 同样 12 个冲突
8. 再次 `abort` + `merge -X theirs` → 成功
9. `git push` → 成功（a4b4ef8..d3250c9）

### 冲突文件详情

| 文件 | 冲突原因 | `-X theirs` 结果 |
|------|---------|-----------------|
| `cron/jobs.json` | completed 计数器 54 vs 56 | 取远程版本 |
| 10× `yulu.md` | 结构化格式 vs 扁平列表 | 取远程版本（更完整） |
| `发展日志.md` | 各自追加内容 | 取远程版本，自动合并 1 文件 |

### 关键教训

1. **`-X theirs` 适合 cron 场景**：远程（Mac）通常是最新编辑源，优先取远程版本合理
2. **abort → merge 是最短路径**：rebase 冲突多时，abort + merge -X theirs 比手动解决快
3. **竞态是正常的**：两端同时在线时，2-3 轮 pull-merge-push 才能收敛
4. **`execute_code` 被阻止**：cron 模式下不能用 Python 脚本，必须依赖 git 原生命令

### 最终 git log
```
d3250c9 sync: 合并远程Mac更新 2026-07-27
e1dd77a merge remote updates
a4b4ef8 auto-sync: 2026-07-27 Mac更新 - 发展日志.md
ba2eda6 auto-sync: 2026-07-27 Windows更新
471e1eb feat: 用脚本重新分配十神语录
```
