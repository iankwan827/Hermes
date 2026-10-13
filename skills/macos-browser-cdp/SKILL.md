---
name: macos-browser-cdp
description: "macOS 上通过 CDP 控制 Chrome 浏览器。启动 Chrome CDP 模式、配置 Hermes 连接、自动化网页操作。触发词：浏览器、Chrome、CDP、网页操作、自动搜索"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [browser, cdp, chrome, macos, automation]
---

# macOS 浏览器 CDP 控制

通过 Chrome DevTools Protocol (CDP) 让 Hermes 控制本机 Chrome，实现网页自动化。

## 前提条件

- Hermes 已安装，`browser` 和 `terminal` toolset 已启用
- macOS 上已安装 Google Chrome（`/Applications/Google Chrome.app`）
- `agent-browser` CLI 已安装（`npm install -g agent-browser`）

## 启动流程

### 1. 确认 toolset 已启用

```bash
hermes tools enable browser
hermes tools enable terminal
```

### 2. 后台启动 Chrome CDP 模式

```bash
# 先杀掉已有 Chrome（避免 singleton 行为忽略端口参数）
killall "Google Chrome" 2>/dev/null
sleep 3

# 必须用 terminal(background=true) 启动，不能用 &
# 用临时 --user-data-dir 绕过锁文件，确保端口参数生效
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp-profile \
  --no-first-run \
  --no-default-browser-check
```

参数说明：
- `--remote-debugging-port=9222` — 开放 CDP 调试端口
- `--user-data-dir=/tmp/chrome-cdp-profile` — 临时目录，绕过 macOS Chrome 锁文件（关键！）
- `--no-first-run --no-default-browser-check` — 跳过首次启动向导

### 3. 验证 CDP 连接

```bash
curl -s http://127.0.0.1:9222/json/version
```

返回 JSON 含 `"Browser": "Chrome/..."` 即表示 CDP 就绪。

### 4. 配置 Hermes 连接 CDP

```bash
hermes config set browser.cdp_url "ws://127.0.0.1:9222"
```

### 5. 验证浏览器控制

调用 `browser_navigate` 访问任意 URL，返回 `success: true` 即配置成功。

## 使用方式

配置完成后，直接用浏览器工具操作：

```
browser_navigate → 打开网页
browser_snapshot → 读取页面内容
browser_click    → 点击元素
browser_type     → 输入文字
browser_scroll   → 滚动页面
browser_vision   → 截图分析
```

## 辅助文件

- `references/chrome-security-policy.md` — Chrome CDP 安全策略详解、调试技巧、常见错误
- `scripts/start_chrome_cdp.sh` — 自动化启动脚本，支持 `--copy-profile` 选项保留登录态

## 常见场景

### 自动搜索

```
用户："用Chrome在小红书搜：无线蓝牙耳机推荐"
步骤：
1. browser_navigate("https://www.xiaohongshu.com")
2. browser_snapshot() 找搜索框
3. browser_type(搜索框ref, "无线蓝牙耳机推荐")
4. browser_press("Enter")
5. browser_snapshot() 读取搜索结果
```

### 读取登录态页面

用户先在 Chrome 里手动登录目标网站，Hermes 通过 CDP 连接同一个 Chrome 实例，自动继承 cookies 和登录状态。

## 实战案例：抖音视频下载

用 CDP 直接下载抖音视频，不需要 opencli。

### 完整流程

```
1. browser_navigate → 打开视频页面
2. browser_console → JS提取视频直链
3. terminal curl → 下载视频文件
```

### 第一步：打开视频页面

```python
# 从分享链接获取视频ID
# 分享链接格式：https://v.douyin.com/XXXXXXX/
browser_navigate("https://www.douyin.com/video/7657076323323596058")
```

### 第二步：提取视频直链

```python
browser_console("""
(async () => {
  const awemeId = window.location.pathname.split('/').pop();
  const resp = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + awemeId + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=MacIntel&browser_name=Edge&browser_version=146.0.0.0', {credentials:'include'});
  const data = await resp.json();
  const aweme = data.aweme_detail;
  if (!aweme) return JSON.stringify({error: data.filter_detail?.filter_reason || 'unknown'});
  return JSON.stringify({desc: aweme.desc.slice(0,60), aweme_id: aweme.aweme_id, video_url: (aweme.video.play_addr.url_list || [])[0] || 'no_url'});
})()
""")
```

返回格式：
```json
{"desc":"视频标题","aweme_id":"123456","video_url":"https://..."}
```

**⚠️ 如果返回 `error: "core_dep"`**：抖音未登录，需要先登录抖音账号。

### 第三步：下载视频

```bash
mkdir -p ~/Movies/素材/视频

curl -s -o ~/Movies/素材/视频/<文件名>.mp4 \
  -w "\nHTTP:%{http_code} SIZE:%{size_download}" \
  -L "<video_url>" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  -H "Referer: https://www.douyin.com/"
```

### 从分享链接获取视频ID

抖音分享链接格式：`https://v.douyin.com/XXXXXXX/`

获取真实URL：
```bash
curl -sL -o /dev/null -w '%{url_effective}' 'https://v.douyin.com/XXXXXXX/' -H 'User-Agent: Mozilla/5.0'
```

返回格式：`https://www.douyin.com/video/7657076323323596058?...`
从URL中提取video_id：`7657076323323596058`

### 注意事项

1. **视频直链有时效性**：获取后尽快下载，URL几分钟内有效
2. **间隔防验证**：每打开一个页面后等待3-5秒再操作
3. **登录态**：需要已登录抖音账号（复制profile后自动继承）
4. **输出路径**：`~/Movies/素材/视频/`

## Pitfalls

### 自己搞定，不要让用户跑终端命令

用户原话："你自己可以关掉chrome，然后打开终端，输入命令不就好了"。当需要启动 Chrome CDP 时，直接用 `terminal()` 执行，不要让用户手动操作。用户看到 Chrome 反复关闭又打开会很烦躁——这通常是因为没杀干净旧进程就启动新的。

### 诊断顺序：先查浏览器状态，再查网页

当 `browser_navigate` 超时时，**不要直接重试**。先判断是"浏览器没打开"还是"网页加载慢"：

```bash
# 1. 检查 CDP 端口是否在监听
curl -s http://127.0.0.1:9222/json/version

# 2. 如果没响应 → 浏览器没启动或 CDP 没开，回到步骤 2 启动 Chrome
# 3. 如果有响应 → 浏览器正常，是网页问题，检查 URL 或网络
```

用户原话："你要分清楚是浏览器没打开还是网页超时了"。这是最常见的误判——把 backend 没启动当成网页超时，反复重试浪费时间。

### 用户已有 Chrome 在运行（最常见场景）

**先检查用户的 Chrome 是否已经有 CDP：**
```bash
curl -s http://127.0.0.1:9222/json/version
```
如果有响应，直接配置 `browser.cdp_url`，不要重新启动。

**如果用户的 Chrome 没有 CDP（最常遇到的坑）：**

macOS 的 Chrome 有两个关键限制：
1. **Singleton 行为**：Chrome 已经在运行时，新实例只是开新窗口，`--remote-debugging-port` 参数被忽略
2. **安全策略**：Chrome **拒绝在默认 profile 目录上启用远程调试**，会报错 `DevTools remote debugging requires a non-default data directory`

**正确流程（四步搞定）：**

```bash
# 1. 杀掉所有 Chrome
killall "Google Chrome" 2>/dev/null
pkill -9 -f "chrome_crashpad" 2>/dev/null
sleep 3

# 2. 复制用户 profile 到临时目录（保留登录态）
#    必须用 rsync -a，cp -R 会丢失 cookies 等登录态
rsync -a "$HOME/Library/Application Support/Google/Chrome/" /tmp/chrome-cdp-profile/

# 3. 用临时目录启动 Chrome
open -a "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp-profile \
  --no-first-run

# 4. 验证（必须等 5 秒让 Chrome 完全启动）
sleep 5 && curl -s http://127.0.0.1:9222/json/version
```

**关键点：**
- `--user-data-dir=/tmp/chrome-cdp-profile` 是**必须的**——Chrome 安全策略不允许在默认目录启用 CDP
- 复制 profile 可以保留用户的登录态、书签、扩展
- 用 `open -a` 启动 GUI 应用，不要用 `terminal(background=true)` + `&`（会被终端会话结束时杀掉）
- 杀 Chrome 时不要用 `killall python`（会误杀 Hermes 自己）
- 复制 profile 需要时间（~30秒），用 `timeout=120` 确保不超时
- **必须用 `rsync -a` 复制 profile，`cp -R` 会丢失 cookies 等登录态**

**为什么不能直接用用户默认目录启动：**
```bash
# ❌ 这样做会失败！Chrome 报错：DevTools remote debugging requires a non-default data directory
open -a "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir="$HOME/Library/Application Support/Google/Chrome"
```

### `/browser connect` 是 CLI 命令

`/browser connect` 只能在 Hermes CLI 终端里用，不能在飞书/Telegram 等 gateway 平台调用。Gateway 平台需要提前配好 `browser.cdp_url`。

### Safari 不支持

Safari 使用 WebKit 引擎，不支持 CDP 协议。Hermes 只能控制 Chrome 系浏览器（Chrome、Brave、Edge、Chromium）。

### 配置生效

`browser.cdp_url` 写入 config 后，当前 session 可能需要 `/reset` 或 gateway restart 才生效。如果 `browser_navigate` 超时，检查 CDP URL 是否正确、Chrome 是否在运行。

### 端口 9222 被占用

```bash
lsof -i :9222 | grep LISTEN
# 找到 PID 后 kill
kill <PID>
```

### Chrome 崩溃或 CDP 断开

重新执行步骤 2 启动 Chrome，确认 `curl http://127.0.0.1:9222/json/version` 返回正常后继续操作。

### opencli browser 是替代方案

如果 CDP 连接有问题，可以用 `opencli browser` 命令：
```bash
opencli browser open <url>     # 打开URL
opencli browser eval "<js>"    # 执行JS
opencli browser screenshot     # 截图
opencli browser network        # 查看网络请求
```
opencli browser 会复用本机 Chrome 的登录态，适合需要登录态的操作（如抖音视频下载）。

### 不要随便 kill Chrome

用户已经登录的网站（如飞书）的 session 保存在 Chrome 进程里。如果 kill Chrome 再重启，登录态会丢失，需要重新扫码登录。只有在 CDP 端口确实被占用时才 kill，否则直接用现有的 Chrome 实例。

### 中文信息搜索：必须用浏览器，不要用 curl（铁律）

**用户原话：「你应该用打开浏览器模仿操作去打开网页的吗，我们有这个skill」**

curl/terminal 方式查询中文信息几乎必然失败：
- **百度搜索结果页**：返回的是 JavaScript 代码，不是可读文本，grep/sed 提取不到内容
- **中国政府网站**（人社局、统计局、政务平台）：检测到自动化请求直接返回空或重定向
- **知乎、小红书、搜狐、头条、爱企查**：反爬机制拦截非浏览器请求

**正确流程（搜索中文信息的标准做法）：**

```
1. 检查 CDP 是否在运行: curl -s http://127.0.0.1:9222/json/version
2. 如果没运行 → 启动 Chrome CDP（按启动流程）
3. browser_navigate("https://www.baidu.com/s?wd=搜索关键词")
4. browser_snapshot() → 找到搜索结果链接
5. browser_click(ref) → 点击进入详情页
6. browser_snapshot(full=true) → 读取完整内容
```

**⚠️ 已知会拦截 curl 的网站（2026-07 验证）：**
- 百度搜索（返回 JS 代码）
- 肇庆市人社局 hrss.zhaoqing.gov.cn（连接重置）
- 爱企查 aiqicha.com（拦截）
- 知乎 zhihu.com（需要 JS 渲染）
- 小红书 xiaohongshu.com（需要 JS 渲染）
- 搜狐 sohu.com（404 或拦截）
- 头条 toutiao.com（需要 JS 渲染）
- 广东省人社厅 hrss.gd.gov.cn（页面不存在或拦截）

**百度搜索是可靠的入口**：搜索结果页可以正常加载，点击结果后跳转到目标网站的成功率更高。
