# Git 冲突解决模式库

> 2026-07-04 积累：bidirectional sync 冲突解决的实战经验

## 文件类型 → 解决策略映射

### 状态文件（.curator_state, .usage.json）
**策略：取较新版本（remote or local，看时间戳）**

理由：状态文件包含运行时计数和时间戳，较新版本自然包含更多信息。
```bash
# 如果远程更新：git checkout --theirs <file>
# 如果本地更新：git checkout --ours <file>
```

### 内存文件（MEMORY.md, USER.md）
**策略：合并双方内容，保留所有 tip**

理由：两边各自积累了不同的经验 tip，丢弃任何一边都是损失。
解决方法：手动删除 conflict markers，保留双方的 tip 段落。

### SKILL.md 文件
**策略：合并双方内容，保留所有改动**

理由：两边可能分别修改了不同段落（如新增 pitfalls、修改步骤）。
解决方法：检查 conflict markers 范围，保留两边的有效改动。

### config.yaml
**策略：合并双方配置项**

理由：双方可能分别添加了不同的配置项（如 platform_toolsets vs fallback_model）。
解决方法：保留所有配置项，删除重复。

### JSON 状态（jobs.json）
**策略：取较新版本**

理由：包含任务计数和时间戳，较新版本更完整。

### 重命名/删除冲突（rename/delete）
**策略：保留重命名版本**

理由：重命名方（通常是 Windows）构建了新的目录结构，删除方（Mac）只是清理旧路径。
```bash
# Windows 端重命名了文件，Mac 端删除了原目录
git add <新路径文件>   # 保留重命名后的文件
git rm <旧路径文件>    # 删除旧路径（如果存在）
# rebase --continue 或 commit
```

## 冲突解决命令模板

### 查看所有冲突文件
```bash
git diff --name-only --diff-filter=U
```

### 批量解决（假设远程版本更完整）
```bash
# 对于状态文件和 JSON：取远程版本
git checkout --theirs .curator_state .usage.json jobs.json
git add .curator_state .usage.json jobs.json

# 对于需要合并的文件：手动编辑后
git add <file>
```

### 解决 rename/delete 冲突
```bash
# 保留重命名后的文件
git add skills/system-operations/references/batch-transcribe-run-runaway.md
git add skills/system-operations/references/windows-processes.md

# 删除旧路径（如果 git 仍然跟踪）
git rm skills/system/process-management/references/batch-transcribe-runaway.md 2>/dev/null
git rm skills/system/process-management/references/windows-processes.md 2>/dev/null
```

## 注意事项

1. **不要急着解决**：先 `git diff --name-only --diff-filter=U` 看清楚有多少冲突
2. **优先解决简单文件**：状态文件、JSON 先取较新版本，减少认知负担
3. **合并文件最后处理**：MEMORY.md、SKILL.md 需要仔细阅读 conflict markers
4. **验证解决结果**：`git status` 确认没有遗留冲突，然后 `git rebase --continue`
