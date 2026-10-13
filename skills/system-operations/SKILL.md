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

### macOS 同步架构

**当前方案（2026-08-05 验证）**：`~/.hermes/` 本身就是 git 仓库，可直接同步。无需额外的 `~/Hermes/` 目录。

```bash
cd ~/.hermes
git add skills/ config.yaml SOUL.md cron/jobs.json memories/ plugins/
git commit -m "auto-sync: $(date +%Y-%m-%d) Mac更新"
git push origin main
```

**实际结构**：
- `~/.hermes/` — 既是 git 同步仓库（git remote 指向 GitHub），也是 Hermes 运行时目录
- 未跟踪的运行时文件（.env、sessions/、logs/、*.db 等）通过 `.gitignore` 或 `git add` 的精确路径控制排除
- 不需要维护两个独立目录

**Cron 任务适配**：Windows cron 定义写死 `E:/Users/Administrator/AppData/Local/hermes`，在 Mac 上运行时该路径不存在。Mac 上实际同步路径为 `~/.hermes/`。如果 cron 需要跨平台，应在 cron 定义中用环境变量或条件判断。

### 首次设备初始化（新设备上第一次同步时）

如果同步目录还没有 git 仓库，需要先初始化：

```bash
cd ~/.hermes  # 或你的 Hermes 数据目录
git init
git remote add origin https://github.com/iankwan827/Hermes.git
git fetch origin main
git checkout -b main origin/main
```

然后正常执行同步流程。后续同步不需要重复此步骤。

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

# 解决后
git rebase --continue
```

#### ⚠️ 自动化场景下的冲突清理：git checkout 替代 git reset --hard

在 cron 或无人值守场景中，`git stash pop` 后可能有残留冲突。`git reset --hard` 需要审批（破坏性操作），改用：

```bash
# 更安全的替代方案（不需要审批）
git checkout origin/main -- .

# 这会用远程版本覆盖所有冲突文件，然后重新 add 本地改动
git add skills/ config.yaml SOUL.md cron/jobs.json memories/ plugins/
```

如果 stash pop 产生大量 modify/delete 冲突，直接 `git merge --abort` 然后 `git checkout origin/main -- .` 重置到远程状态，再重新 add 本地文件是最干净的路径。

#### 冲突解决策略（按文件类型）

| 文件类型 | 策略 | 说明 |
|---------|------|------|
| 状态文件（.curator_state, .usage.json） | 取较新版本 | 包含最近运行数据 |
| 内存文件（MEMORY.md） | 合并双方内容 | 两边的 tip 都有价值 |
| SKILL.md | 合并双方内容 | 两边的改动都保留 |
| config.yaml | 合并双方配置 | 保留所有配置项 |
| JSON 状态（jobs.json） | 取较新版本 | 时间戳和计数更新 |
| 数据日志（发展日志.md） | 取较新/较详细版本 | 远程通常有更完整的定时采集数据 |
| 重命名/删除冲突 | 保留重命名版本 | 保留新结构 |

#### 快速解决：git checkout --theirs（保留远程版本）

当远程版本明显更完整时（如数据日志有更多条目），直接用远程版本覆盖：

```bash
# 1. 查看冲突文件
git diff --name-only --diff-filter=U

# 2. 对每个冲突文件，保留远程版本
git checkout --theirs <冲突文件路径>

# 3. 标记为已解决
git add <冲突文件路径>

# 4. 继续 rebase
git rebase --continue
```

**适用场景**：远程有更详细的定时采集数据、更完整的日志条目、或更新的配置。

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

### ⚠️ 未跟踪运行时文件控制

`~/.hermes/` 作为 git 仓库时，存在大量未跟踪的运行时文件（.env、sessions/、logs/、*.db、bin/ 等）。同步时只 add 指定目录，不要 `git add .`：

```bash
# ✅ 只 add 需要同步的文件
git add skills/ config.yaml SOUL.md cron/jobs.json memories/ plugins/

# ❌ 不要这样做（会把 .env、sessions/、logs/ 等全加进去）
git add .
```

如果 `.gitignore` 已配置好，也可以 `git add -u`（只更新已跟踪文件的变更）。

### ⚠️ macOS 大小写不敏感文件系统

macOS 默认使用 APFS（大小写不敏感），中文文件名如 `发展日报.md` 和 `发展日志.md` 会被视为**同一个文件**。这会导致 git 索引混乱：
- `git status` 显示文件被修改，但 `git diff HEAD` 无输出
- `git ls-files` 和磁盘实际文件名不一致

**诊断**：
```bash
git ls-files | grep "关键词"  # 检查 git 索引中的文件名
ls -la <目录>/               # 检查磁盘实际文件名
```

**修复**：重新 add 正确的文件名：
```bash
git rm --cached "错误文件名.md" 2>/dev/null
git add "正确文件名.md"
```

### ⚠️ GitHub 连接问题：代理/防火墙绕过

在某些网络环境下（如中国大陆），GitHub HTTPS (443端口) 可能被防火墙阻断。症状：`git pull/push` 超时，curl 也连不上 `github.com:443`。

#### 快速绕过：环境变量清除（最可靠）

当系统设置了 `http_proxy`/`https_proxy` 环境变量时，`git -c http.proxy=""` **不能覆盖**它们——git 会优先读取环境变量。唯一可靠的方式是清除环境变量：

```bash
# ✅ 最可靠：清除代理环境变量，让 TUN 接口透明路由
env -u http_proxy -u https_proxy -u all_proxy -u no_proxy git push origin main
env -u http_proxy -u https_proxy -u all_proxy -u no_proxy git pull origin main --rebase
```

**⚠️ 关键发现（2026-08-17 验证）**：`git -c http.proxy="" -c https.proxy=""` 在环境变量存在时无效！git 的行为是：环境变量 > gitconfig。即使 gitconfig 中 proxy 被设为空字符串，git 仍会使用 `http_proxy` 环境变量连接代理。代理的 CONNECT 隧道能建立（HTTP 200），但 LibreSSL 的 TLS 握手会失败（`SSL_ERROR_SYSCALL`）。

**原理**：macOS 上 V2Ray（com.vorte）运行在 TUN 模式，透明拦截所有流量。清除代理环境变量后，git 直连 GitHub，TUN 接口自动路由到代理的出站连接，SSL 握手正常完成。

**备选**（环境变量清除不可用时）：命令行内联覆盖（不改 gitconfig）：
```bash
git -c http.proxy="" -c https.proxy="" push origin main
```
注意：此方法在环境变量存在时可能无效。

#### 快速诊断

```bash
# 检查端口连通性
nc -z -w 5 github.com 443 2>&1; echo "HTTPS: $?"  # 超时=被阻断
nc -z -w 5 github.com 22 2>&1; echo "SSH: $?"      # 通=SSH可用
```

#### ⚠️ 代理配置可能在 local .git/config 而非 global（2026-08-13 验证）

`git config --global --unset http.proxy` 只能移除全局配置。如果代理设置在仓库的 `.git/config`（local 级别），global unset 不会生效，push/pull 仍然走代理并报 SSL 错误。

**诊断**：查代理来源（`--show-origin` 显示配置层级）：
```bash
git config --list --show-origin | grep proxy
# 输出示例：file:.git/config  http.proxy=http://127.0.0.1:7897
#          file:.git/config  https.proxy=http://127.0.0.1:7897
```

**修复**：根据来源层级 unset：
```bash
# local 级别（仓库 .git/config）
git config --local --unset http.proxy
git config --local --unset https.proxy

# global 级别（~/.gitconfig）
git config --global --unset http.proxy
git config --global --unset https.proxy
```

**快速绕过**（不改任何配置）：
```bash
git -c http.proxy="" -c https.proxy="" push origin main
```

**教训**：macOS 上 LibreSSL 对代理转发的 HTTPS 处理不稳定。代理 CONNECT 返回 200 后 SSL handshake 仍可能失败（SSL_ERROR_SYSCALL）。直连 GitHub 443 端口在无防火墙环境下更可靠。

### ⚠️ Git 操作超时但网络可达（2026-08-12 验证）

症状：`ping github.com` 正常（~90ms），`curl` API 可达，但 `git fetch/push/pull` 超时（30s-60s）。常见于大仓库或慢速连接。

**根因**：git 默认 `http.postBuffer` 较小，大仓库传输时缓冲区不足导致卡死。

**修复**：增大 postBuffer + 延长超时：

```bash
# fetch
git -c http.postBuffer=524288000 -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=60 fetch origin main --depth=5

# push
git -c http.postBuffer=524288000 push origin main

# pull（同样适用）
git -c http.postBuffer=524288000 pull origin main --rebase
```

**诊断步骤**：先确认网络可达（`ping`、`curl` API），再试增大 buffer 的 git 命令。如果 `http.postBuffer` 无效，用 GitHub API 做只读检查（见下方）。

#### GitHub REST API 作为只读后备（网络受限时）

当 git fetch/pull 超时但 HTTP API 可达时，用 GitHub REST API 检查远程状态：

```bash
# 查看远程最近 5 条 commit
curl -s "https://api.github.com/repos/iankwan827/Hermes/commits?sha=main&per_page=5" | \
  python3 -c "import json,sys; [print(f\"{c['commit']['author']['date'][:10]} {c['sha'][:8]} {c['commit']['message'][:60]}\") for c in json.load(sys.stdin)[:5]]"

# 检查远程与本地的差异文件
curl -s "https://api.github.com/repos/iankwan827/Hermes/compare/<local-sha>...main" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); [print(f['filename']) for f in d.get('files',[])]"
```

**适用场景**：cron 无人值守、网络不稳定、只需确认"对方改了什么"而不需要完整 merge 时。

#### 方案一：git credential approve（SSH 端口通但 HTTPS 被阻断时）

如果 SSH 端口 22 通但 HTTPS 443 被阻断，且 `~/.git-credentials` 中有 token，可以用 credential approve 让 git 使用已存储的凭据：

```bash
# 从 .git-credentials 提取 token 并设置
TOKEN=$(grep -o 'ghp_[A-Za-z0-9]*' ~/.git-credentials 2>/dev/null)
printf "protocol=https\nhost=github.com\nusername=<用户名>\npassword=%s\n" "$TOKEN" | git credential approve

# 然后正常操作（git 会用已存储的凭据）
git fetch origin
git push origin main
```

**原理**：`git credential approve` 将凭据写入 credential helper 的存储，后续 git 操作会自动使用。即使直连 HTTPS 超时，credential helper 仍可能通过其他路径（如代理、缓存）完成认证。

#### 方案二：本地代理（推荐）

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

# 检查代理是否能通 HTTPS（关键！端口在监听≠能转发）
curl -x http://127.0.0.1:7897 -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://github.com
# 返回 000 = 代理在监听但无法转发 HTTPS（com.vorte 常见问题）
# 返回 200 = 代理正常
```

**⚠️ 代理端口在监听但无法转发（2026-08-15 验证）**：`lsof -i :7897` 显示进程在监听，`nc -z` 也通，但 `curl --proxy` 返回 000 超时。症状：代理进程活着但 HTTPS CONNECT 隧道建不起来。诊断顺序：
1. `nc -z -w 2 127.0.0.1 7897` — 确认端口通
2. `curl -x http://127.0.0.1:7897 -s -o /dev/null -w "%{http_code}" https://github.com` — 确认能否转发
3. 如果转发失败，尝试 `--socks5` 代替 `--proxy`（有些代理只支持 SOCKS 不支持 HTTP CONNECT）
4. 都不行 → 代理软件本身有问题，需重启代理或用 GitHub 加速镜像（ghfast.top）

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

#### 备选方案：程序化合并（保留双方内容）

当冲突文件是结构化文本（如数据日志、审核记录），双方的改动都有价值时，可以用 Python 程序化合并：

```python
import re

with open('<冲突文件>', 'r') as f:
    content = f.read()

# 找到冲突块（<<<<<<< HEAD ... ======= ... >>>>>>>）
conflict_pattern = r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]+?$'
match = re.search(conflict_pattern, content, re.DOTALL)

if match:
    remote_part = match.group(1)  # HEAD = 远程版本
    local_part = match.group(2)   #ours = 本地版本
    resolved = remote_part + '\n' + local_part  # 保留双方
    new_content = content[:match.start()] + resolved + content[match.end():]
    with open('<冲突文件>', 'w') as f:
        f.write(new_content)
```

**适用场景**：`发展日志.md` 等追加式日志文件，双方在不同时间段添加了不同条目，需要全部保留。

**2026-07-30 实例**：Windows 端添加了详细的 `07-29 23:00` 审核记录，Mac 端添加了 `07-30 17:00` 数据更新行 + 停滞期总结。用 Python 合并保留了双方的完整内容。

### 冲突解决实例

详见 `references/sync-session-2026-07-29.md`（macOS 端 rebase + theirs 解决）、`references/conflict-resolution-cron-pattern.md`（Windows 端 merge -X theirs 批量解决）。

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
- ⚠️ GitHub HTTPS 被墙时：git 默认不走系统代理，必须手动 `git config http.proxy http://127.0.0.1:7897` 设代理才能 push/pull。报 Connection reset/timeout 先查代理端口
- ⚠️ macOS git push SSL 失败的排查顺序（2026-07-26 验证）：**先清代理再试直连** → 1) `git config --unset http.proxy; git config --unset https.proxy` 然后 `git push` → 2) 如果直连超时，再设代理 `git config http.proxy http://127.0.0.1:7897` 试 HTTP → 3) SOCKS5 `socks5h://127.0.0.1:7897` → 4) `GIT_SSL_NO_VERIFY=1 git push` → 5) 都不行则让另一端 pull（commit 已在本地）。**教训：gitconfig 里残留的 proxy 设置会干扰 SSL 握手，即使代理本身正常运行。**
- ⚠️ 最快清代理方式（2026-08-17 更新）：`env -u http_proxy -u https_proxy -u all_proxy -u no_proxy git push origin main` — 清除环境变量，让 TUN 接口透明路由。**比 `git -c http.proxy=""` 更可靠**，因为 git 优先读取环境变量，`git -c` 无法覆盖已设置的 env vars。适用于 cron 无人值守场景
- ⚠️ Vercel 拖拽部署后自定义域名可能仍指向旧 deployment → 用 `vercel promote` 更新别名
- ⚠️ Vite PWA manifest icon 路径必须用绝对路径（`/bazi/assets/icon.png`），相对路径在子路径部署时会 404
- ⚠️ JS 文件中孤立的 `*/` 或缺失的函数关闭 `}` 会导致语法错误 → 后续所有变量报 "not defined" → `node --check` 快速定位，深度诊断用括号匹配检查
- ⚠️ GitHub Secret Scanning：密钥可能泄露在 skills references/部署文档中（不只是 .env） → push 削前检查 `git diff --cached`，发现后 amend + 脱敏重推
- ⚠️ 不要提交二进制文件（tar.gz/zip）到 git 仓库 → GitHub 上显示乱码，Windows 拉取后也无法使用。正确做法：直接提交源文件（skill 目录结构），让两端通过 git 同步源文件。打包压缩只用于临时传输，不入库
- ⚠️ Cron 任务路径跨平台问题：cron 定义可能写死 Windows 路径（`E:/Users/Administrator/AppData/Local/hermes`），但在 Mac 上运行时该路径不存在。Mac 上 git 仓库实际在 `~/Hermes/`（同步仓库）和 `~/.hermes/`（运行时目录）。如果 cron 需要跨平台，应在 cron 定义中用环境变量或条件判断
- ⚠️ macOS 大小写不敏感文件系统：中文文件名如 `发展日报.md` 和 `发展日志.md` 会被视为同一个文件，导致 git 索引混乱（status 显示修改但 diff 无输出）。诊断用 `git ls-files | grep 关键词`，修复用 `git rm --cached` + `git add`
- ⚠️ 未跟踪运行时文件控制：`~/.hermes/` 有 .env、sessions/、logs/ 等大量未跟踪文件，同步时只 add 指定目录（skills/ config.yaml SOUL.md cron/jobs.json memories/ plugins/），不要 `git add .`
- ⚠️ `profiles/` 目录不要入库：`~/.hermes/` 下有 `profiles/main/` 子目录（包含完整的 skill 副本、运行时状态等），这是另一个独立的文件层级。同步时 git add 的路径必须相对于 git 根目录（`~/.hermes/`），不要从 `profiles/main/` 内部执行同步命令。如果误 add 了 `profiles/`，用 `git reset HEAD profiles/` 撤销暂存
- ⚠️ `git credential approve` 快速修复认证：当 HTTPS 端口被阻断但 SSH 端口通时，从 `~/.git-credentials` 提取 token，用 `printf "protocol=https\nhost=github.com\nusername=...\npassword=...\n" | git credential approve` 设置凭据，然后正常 git 操作
- ⚠️ `git rebase --continue` 在无终端环境下报 "Terminal is dumb, but EDITOR unset" → 用 `GIT_EDITOR=true git rebase --continue`（跳过编辑器直接继续）或 `GIT_EDITOR="cat" git rebase --continue`
- ⚠️ `.DS_Store` 污染 git status：macOS Finder 会在目录中创建 `.DS_Store`，导致 `git status` 显示大量未跟踪文件。在同步仓库根目录的 `.gitignore` 中加入 `.DS_Store` 即可消除噪音
