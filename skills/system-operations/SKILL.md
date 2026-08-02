---
name: system-operations
description: "Windows/Hermes 系统运维操作。包含跨设备 Git 同步和进程安全管理。触发方式：同步配置、杀进程、查进程、进程雪崩、git push被拒。"
tags: [system, windows, git, sync, process, operations]
---

# System Operations — Windows/Hermes 系统运维

跨设备配置同步 + Windows 进程安全管理。涵盖日常运维中最常见的两类系统级操作。

---

## 一、跨设备 Git 同步

在多台设备（Windows + Mac）间同步 Hermes 配置、技能和记忆。由 cron 每日自动触发，也可手动执行。

### 核心工作流

```bash
cd "$HERMES_HOME"  # 通常是 ~/.hermes 或 E:/Users/Administrator/AppData/Local/hermes

# 1. 暂存同步目录
git add skills/ config.yaml SOUL.md cron/jobs.json memories/ plugins/

# 2. 检查变更
git status --short

# 3. 如果有改动，提交
git commit -m "auto-sync: $(date +%Y-%m-%d) <设备名>更新"

# 4. 推送（可能被拒绝——见下方冲突处理）
git push origin main

# 5. 拉取远程更新
git pull origin main

# 6. 检查对方改了什么
git log --oneline -5
```

### ⚠️ 冲突处理：merge 优先于 rebase，但 rebase 也可行

**核心原则**：当两端都有独立改动导致 push 被拒绝时，**优先使用 `git merge`**（更简单），但 `git rebase` 也能用（需要系统化冲突解决）。

#### 场景A：本地有未提交改动时拉取远程

当本地有未暂存/未提交的修改（如cron自动更新了数据文件），直接 `git pull` 会失败。用 stash 中转：

```bash
# 1. 暂存本地改动
git stash

# 2. 拉取远程
git pull origin main

# 3. 恢复本地改动（可能产生冲突）
git stash pop

# 4. 解决冲突后提交
git add <冲突文件>
git commit -m "resolve merge conflict: <说明>"
git push origin main
```

**判断保留哪边数据**：看时间戳和数据新鲜度。cron自动更新的数据文件（如发展日志），本地stashed版本通常比远程更新（因为cron刚跑过）。审核记录等累积性内容，取条目更多的版本。

**批量解决冲突**：如果终端Python有环境问题（如SRE module mismatch），用 `execute_code` + `hermes_tools` 批量处理：
```python
from hermes_tools import read_file, write_file
import re
result = read_file('conflict-file.md', limit=2000)
content = result['content']
# 去掉行号（read_file格式是 "     N|content"）
lines = content.split('\n')
clean = [l.split('|',1)[1] if '|' in l and l.split('|',1)[0].strip().isdigit() else l for l in lines]
content = '\n'.join(clean)
# 用正则保留stashed版本
pattern = r'<<<<<<< Updated upstream\n.*?=======\n(.*?)>>>>>>> Stashed changes\n'
resolved = re.sub(pattern, r'\1', content, flags=re.DOTALL)
write_file('conflict-file.md', resolved)
```

#### 推荐路径：merge（简单自动合并）
```bash
# ✅ merge 更宽容，大多数冲突自动合并
git pull origin main
# 检查是否有冲突
git status
# 有冲突则手动解决，无冲突则完成
```

#### 备选路径：rebase（线性历史，需手动解决）
```bash
# 适用于 cron 任务或需要干净线性历史的场景
git pull origin main --rebase

# 查看冲突文件
git diff --name-only --diff-filter=U

# 解决冲突后，先 git add
git add <冲突文件>

# 继续 rebase（cron/非交互式环境必须跳过编辑器）
GIT_EDITOR=true git rebase --continue
# 或手动提交：git commit -m "auto-sync: ..." && git rebase --continue
```

**⚠️ rebase --continue 的编辑器陷阱**：`git rebase --continue` 会尝试打开编辑器（通常是 nano）让你编辑 commit message。在 cron / 非交互式终端中 nano 无法启动，报 `Standard input is not a terminal`。两种解决方法：

- **方法A（推荐，更简洁）**：设置环境变量跳过编辑器：`GIT_EDITOR=true git rebase --continue`
- **方法B（备选）**：先手动提交再 rebase：`git commit -m "..."` 然后 `git rebase --continue`（rebase --continue 发现 commit 已存在就会直接继续）

#### 冲突解决策略（按文件类型）

| 文件类型 | 策略 | 说明 |
|---------|------|------|
| 状态文件（.curator_state, .usage.json） | 取较新版本 | 包含最近运行数据 |
| 内存文件（MEMORY.md） | 合并双方内容 | 两边的 tip 都有价值 |
| SKILL.md | 合并双方内容 | 两边的改动都保留 |
| config.yaml | 合并双方配置 | 保留所有配置项 |
| JSON 状态（jobs.json） | 取较新版本 | `completed` 计数和 `last_run_at` 时间戳取较新值；冲突字段均为运行时状态，无语义冲突 |
| 重命名/删除冲突 | 保留重命名版本 | 保留新结构 |

#### rename/delete 冲突专项处理
```bash
# 当 Windows 端重命名了文件，Mac 端删除了原目录时
git add <新路径文件>   # 保留重命名后的文件
git rm <旧路径文件>    # 删除旧路径（如果存在）
# rebase --continue 或 commit
```

### 同步范围

**✅ 同步的文件：** skills/、config.yaml、SOUL.md、cron/jobs.json、memories/、plugins/

**❌ 不同步的文件：** .env（API密钥）、auth.json（OAuth令牌）、sessions/（会话数据）、logs/、*.db、cache/、gateway.lock/pid

### ⚠️ GitHub 连接问题：代理/防火墙绕过

在某些网络环境下（如中国大陆），GitHub HTTPS (443端口) 可能被防火墙阻断。症状：`git pull/push` 超时，curl 也连不上 `github.com:443`。

#### 解决方案：本地代理（推荐）

本机代理在 **7897 端口**（Clash），但 git 默认不走系统代理，需要手动设置：

```bash
# 1. 设 git 代理
git config http.proxy http://127.0.0.1:7897
git config https.proxy http://127.0.0.1:7897

# 2. 正常 push/pull
git push origin main

# 3. 用完清理（可选，避免影响局域网操作）
git config --unset http.proxy
git config --unset https.proxy
```

**⚠️ 关键发现**：系统代理开了 ≠ git 能走代理。git 不会自动读取系统代理设置，必须用 `git config http.proxy` 手动指定。报 "Connection was reset" / "Could not connect to server" 时，先检查代理端口是否通：

```bash
# 检查代理端口是否在监听
netstat -an | grep 7897

# 检查代理是否能通 GitHub
curl -x http://127.0.0.1:7897 -s --connect-timeout 10 https://github.com | head -c 50
```

#### 备选方案：GitHub 加速代理

```bash
git config --global url."https://ghfast.top/https://github.com/".insteadOf "https://github.com/"
git pull origin main --rebase
git config --global --unset url."https://ghfast.top/https://github.com/".insteadOf
git push origin main
```

#### SSH 方案（备选）

如果不想每次处理 HTTPS 代理，可配置 SSH key：
- `git remote set-url origin git@github.com:iankwan827/Hermes.git`
- 但需要先确保 SSH key 已配置并添加到 GitHub（本机目前未配置）

#### 诊断命令

```bash
# 检查 git 代理配置
git config --get http.proxy
git config --get https.proxy

# 检查 HTTPS 连通性（走代理）
curl -x http://127.0.0.1:7897 -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://github.com

# 检查 HTTPS 连通性（不走代理，通常会超时）
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://github.com
```

### 常见问题

- **Push 被拒绝**：远程有本地没有的 commit → 先 pull（merge）再 push
- **.env 被 add**：`git reset HEAD .env` 然后加到 `.gitignore`
- **GitHub Secret Scanning 拒绝推送**：文件中包含 token/密钥 → 见下方专项处理

### ⚠️ GitHub Secret Scanning 拒绝推送

GitHub Push Protection 会扫描提交内容，检测到密钥/token 时拒绝推送。即使 `.env` 没被同步，密钥也可能泄露在其他同步文件中（如 skills references、部署文档）。

**触发条件**：push 返回 `remote rejected — Push cannot contain secrets` + 具体文件和行号

**处理流程**：
```bash
# 1. 读取被标记的文件，定位 secret
cat <被标记文件路径>

# 2. 脱敏（替换为环境变量引用或占位符）
#    ❌ VERCEL_TOKEN=vcp_xxx...
#    ✅ VERCEL_TOKEN=$VERCEL_TOKEN  （引用环境变量）
#    ✅ Token 存储在 .env 中（不入库）

# 3. amend 提交
git add <修改后的文件>
git commit --amend -m "auto-sync: $(date +%Y-%m-%d) <设备名>更新"

# 4. 重新推送
git push origin main
```

**预防**：新建含部署信息的 reference 文件时，不要写入实际 token，只写环境变量名或「见 .env」。在 `git add` 之前用 `git diff --cached` 检查是否有敏感内容。
- **GitHub 连接超时**：可能是防火墙阻断 443 端口 → 用 `ghfast.top` 代理绕过（见上方）

### Cron 模式专用策略：`-X theirs`

当作为 cron 任务运行时（无人值守、无交互终端），手动解决冲突不可行。**推荐路径**：

```bash
# 1. 如果 rebase 失败，先 abort
git rebase --abort

# 2. 用 merge + theirs 自动解决冲突（优先取远程版本）
git merge origin/main -X theirs -m "sync: 合并远程更新 $(date +%Y-%m-%d)"

# 3. 如果远程又有新提交（push 被拒），再 pull 一次
git pull origin main --rebase  # 或再次 merge -X theirs
git push origin main
```

**`-X theirs` 的含义**：冲突时自动采用远程（"theirs"）的版本。适用于：
- 语录文件（yulu.md）：远程通常有更完整的结构化内容
- jobs.json：远程计数器通常更新
- 发展日志等累积文件：远程内容通常是最新编辑

**⚠️ cron 模式限制**：`execute_code`（Python 脚本）在 cron 模式下被阻止，不能用 Python 正则批量解决冲突。必须依赖终端命令或 `git merge -X theirs` 自动解决。

**多轮同步竞态**：同步过程中 Mac 端可能也在推送，导致 pull 后 push 被拒。这是正常的——再次 pull + merge + push 即可，通常 2-3 轮完成。

---

### 冲突解决实例

**2026-07-03 场景（merge 成功）：**
Windows 端 9 个文件变更，远程 Mac 端 1 个 commit。Rebase 产生 7 文件冲突，abort 后改 merge 成功自动合并。

**2026-07-04 场景（rebase + 手动解决）：**
Windows 端 17 文件变更，远程 Mac 端 4 commits（Chrome/CDP 修复）。Rebase 产生 8 文件冲突，通过系统化冲突解决（按文件类型策略）成功合并。

**教训对比：**
- Rebase 适合单边修改的线性历史；Merge 适合两边都有独立修改的分叉历史
- 8 个文件以下的冲突可用 rebase + 手动解决；超过 8 个文件建议用 merge
- 每日自动同步场景用 merge 更安全，但如果 cron 指定了 --rebase，可用上述策略手动解决

---

## 二、Windows 进程管理

### 核心原则

**永远不要用 `killall python` 或 `taskkill /IM python.exe /F`** — Hermes agent 本身就是 Python 进程，会把自己杀掉。

### 安全流程

**1. 列出所有 Python 进程**
```powershell
tasklist | findstr python
```

**2. 识别每个进程的具体内容**
```powershell
wmic process where "name='python.exe'" get ProcessId,ParentProcessId,CommandLine
```

**3. 检查进程树（处理自动重启）**
如果杀掉进程后它又出现，说明有父进程在自动重启：
```powershell
wmic process where "ProcessId=<ParentPID>" get Name,CommandLine
```

**4. 安全终止进程**
```powershell
# 只杀指定 PID，不要用 /IM 杀同名进程
taskkill /PID <目标PID> /F
```

### ⚠️ MSYS bash 下 taskkill 转义问题

MSYS 会把 `/PID` 解析成路径，导致 `taskkill /PID xxx /F` 报错。解决方案：
- 用 `wmic process where "ProcessId=xxx" call terminate`
- 或用 `cmd //c "taskkill /PID xxx /F"` 双斜杠转义

### 批量杀进程（按命令行模式匹配）

```powershell
# 杀所有包含特定关键字的进程
wmic process where "commandline like '%keyword%'" call terminate
```

### 常见进程占用

- whisper 模型（small）：约 1.5-1.7GB
- Hermes agent：约 170-200MB
- Python 基础：约 5MB

---

## 三、Vercel 部署管理

用户有 5 个 Vercel 项目（bazi-new-web, sanbanfu, sanbanfu2, taigongqimen, 以及一个旧的 bazi）。大部分项目通过 Gemini 拖拽上传部署，非 Git 连接。

### CLI Token 认证

OAuth 在无头环境（hermes terminal）下经常失败。直接用 token：

```bash
# 用户在浏览器 https://vercel.com/account/tokens 创建 token
VERCEL_TOKEN=<token> vercel whoami          # 验证
VERCEL_TOKEN=<token> vercel projects ls     # 列项目
VERCEL_TOKEN=<token> vercel --prod --yes --name <project>  # 部署
```

### ⚠️ 拖拽部署 vs CLI 部署的别名问题

**拖拽部署**（用户常用方式）：上传文件夹到 Vercel 网站 → 构建成功 → 但自定义域名（如 shiyibazi.top）可能仍指向旧部署。

**原因**：Vercel 的 domain alias 绑定到特定 deployment ID，拖拽上传产生新 deployment 但不一定更新 alias。

**修复**：
```bash
VERCEL_TOKEN=<token> vercel promote <deployment-url> --yes
```

**验证当前指向**：
```bash
VERCEL_TOKEN=<token> vercel inspect https://<domain>
# 看 Aliases 部分指向的 deployment URL 和创建时间
```

### CLI 首次部署流程

```bash
cd <project-dir>
VERCEL_TOKEN=<token> vercel pull --yes      # 拉取项目设置
VERCEL_TOKEN=<token> vercel --prod --yes    # 部署
```

### Vite + PWA manifest 路径陷阱

当 Vite 项目部署在子路径（如 `/bazi/`）时，`vite-plugin-pwa` 生成的 manifest 中 icon 路径可能不带 base 前缀。

**错误示例**：`vite.config.js` 中 `src: 'assets/icon.png'` → 构建后 manifest 写 `/assets/icon.png`（404）
**正确写法**：`src: '/bazi/assets/icon.png'` → 绝对路径，不受 base 影响

### JS 语法错误导致的级联 "undefined"

**症状**：控制台报 `XXX is not a function` 或 `XXX is not defined`，但源码中明明定义了。

**常见原因**：
1. **孤立的 `*/`**（没有匹配的 `/*`）— 最常见，导致语法错误，后续所有代码不执行
2. **函数缺少关闭 `}`** — IIFE 或嵌套函数没有正确关闭，导致后续代码在错误的作用域中
3. **IIFE 中多余空格** — `}) ()` 可能被某些环境解析为语法错误，改为 `})()`

**诊断**：
```bash
node --check <file.js>                    # 直接报语法错误位置
node -e "require('fs').readFileSync('file.js','utf8')" | node --check  # 远程文件也可
# 批量检查项目中所有 JS：
grep 'src="js/' index.html | sed 's/.*src="\([^"]*\)".*/\1/' | sed 's/\?.*//' | while read f; do node --check "$f"; done
```

**深度诊断**（语法通过但运行时报错）：
```bash
# 检查括号匹配深度
node -e "
const code = require('fs').readFileSync('file.js','utf8');
let d=0; code.split('\n').forEach((l,i) => {
  for(const c of l){if(c==='{')d++;if(c==='}')d--}
  if(d<0) console.log('L'+(i+1)+': NEGATIVE depth='+d);
});
console.log('Final depth:', d);
"
```
最终 depth 不为 0 = 有未关闭的 `{`。

**修复**：删除孤立 `*/`，补上缺失的 `}`，重新部署。

---

## Pitfalls

- ⚠️ Hermes agent = Python 进程，误杀会导致会话断开
- ⚠️ whisper 模型加载后占用 1.6GB 内存，需要等它加载完再操作
- ⚠️ 自动重启的进程：杀了子进程会重生，必须找到父进程
- ⚠️ Windows 下不要用 `kill` 命令（那是 MSYS/Git Bash 的），用 `taskkill` 或 `wmic`
- ⚠️ Git 同步时 merge 优于 rebase（自动合并更多）；但如果 cron 指定了 --rebase，可用按文件类型策略手动解决冲突
- ⚠️ `git stash pop` 后冲突：用正则保留stashed版本（`<<<<<<< Updated upstream\n.*?=======\n(.*?)>>>>>>> Stashed changes`），终端Python有环境问题时用 `execute_code` + `hermes_tools` 批量处理
- ⚠️ GitHub HTTPS 被墙时：git 默认不走系统代理，必须手动 `git config http.proxy http://127.0.0.1:7897` 设代理才能 push/pull。报 Connection reset/timeout 先查代理端口
- ⚠️ Windows Credential Manager (`credential.helper=manager`) 在 cron/后台上下文中会弹出 GUI 对话框，导致 git push 挂起直到超时。症状：push 卡住无输出，`GIT_CURL_VERBOSE=1` 显示 401 后无后续。修复：`git config credential.helper store` 切换到文件存储凭据，或在 push 前设置 `GIT_TERMINAL_PROMPT=0` 避免交互式提示
- ⚠️ Vercel 拖拽部署后自定义域名可能仍指向旧 deployment → 用 `vercel promote` 更新别名
- ⚠️ Vite PWA manifest icon 路径必须用绝对路径（`/bazi/assets/icon.png`），相对路径在子路径部署时会 404
- ⚠️ JS 文件中孤立的 `*/` 或缺失的函数关闭 `}` 会导致语法错误 → 后续所有变量报 "not defined" → `node --check` 快速定位，深度诊断用括号匹配检查
- ⚠️ GitHub Secret Scanning：密钥可能泄露在 skills references/部署文档中（不只是 .env） → push 前检查 `git diff --cached`，发现后 amend + 脱敏重推
- ⚠️ rebase --continue 在非交互式终端（cron）中会失败：nano 无法打开编辑器 → 设置 `GIT_EDITOR=true git rebase --continue` 跳过编辑器，或先 `git commit -m "..."` 手动提交再 rebase --continue
- ⚠️ `execute_code` 在 cron 模式下被阻止（安全策略）→ 不能用 Python 脚本批量解决冲突，只能用 `git merge -X theirs` 自动合并或终端命令
- ⚠️ 同步过程中远程可能有新 push → merge 后 push 被拒是正常的，再 pull + merge + push 即可，通常 2-3 轮收敛
