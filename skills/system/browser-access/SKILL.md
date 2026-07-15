---
name: browser-access
description: |
  浏览器访问统一方案。首选Hermes browser工具（CDP连接Chrome），失败则回退OpenCLI。
  所有需要操作网页的任务（搜热点、查数据、下载视频等）都应参考此skill选择工具。
  触发方式：任何涉及浏览器/网页操作的任务自动加载。
tags: [browser, cdp, opencli, web]
version: 1.0.0
created: 2026-07-03
platforms: [windows]
---

# 浏览器访问统一方案

## 核心原则

**所有网页操作任务，第一步永远是尝试Hermes browser工具（CDP）。失败才回退OpenCLI。**

## 方案A（首选）：Hermes Browser工具 + CDP

### 前置条件

1. Chrome以调试模式运行，端口9222
2. Config已设置：`hermes config set browser.cdp_url "ws://127.0.0.1:9222"`
3. `.env`中`CAMOFOX_URL`已注释掉

### 启动Chrome（如未运行）

**Chrome快捷方式已配置`--remote-debugging-port=9222`**，从开始菜单启动即可。定时任务不需要杀Chrome重启。

```bash
# 1. 先检查CDP端口是否通
curl -s http://localhost:9222/json/version

# 2. 如果通了，直接用browser工具，不用管Chrome
# 3. 如果不通，Chrome可能没启动或被关了，启动它：
#    ⚠️ 不要指定--user-data-dir！让Chrome自动用默认目录（保留Google账号登录态）
"/c/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 &

# 4. 验证端口（必须看到JSON输出）
sleep 8 && curl -s http://localhost:9222/json/version
```

**⚠️ 关键**：不要指定`--user-data-dir`参数！Chrome会自动使用用户默认目录（可能是C盘或E盘），保留所有登录态（Google账号、抖音等）。如果指定了错误的路径，会创建一个干净的Chrome，丢失所有登录。

**⚠️ 前提**：Chrome快捷方式已配置CDP参数（`C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk`）。如果快捷方式被Chrome更新覆盖，需要重新添加参数。
- ❌ 杀掉正在运行的Chrome再重启（会导致用户看到新Chrome窗口，丢失Google账号登录态）
- ❌ 启动第二个Chrome实例（Chrome是单实例应用，新实例会合并到旧会话，CDP参数被忽略）

**⚠️ 如果Chrome已经在跑但端口不通**：
- 告知用户：需要关掉所有Chrome窗口，从开始菜单重新启动
- 不要偷偷杀Chrome，用户会看到新窗口

**⚠️ 前提**：Chrome快捷方式已配置CDP参数（`C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk`）。如果快捷方式被Chrome更新覆盖，需要重新添加参数。

### 工具对照表

| 操作 | Hermes工具 | 说明 |
|------|-----------|------|
| 打开页面 | `browser_navigate(url="URL")` | 返回页面快照 |
| 执行JS | `browser_console(expression="js")` | 等同于eval |
| 截图 | `browser_vision()` | 视觉检查 |
| 点击元素 | `browser_click(ref="@eN")` | 用snapshot中的ref |
| 输入文字 | `browser_type(ref="@eN", text="...")` | 清空后输入 |
| 获取快照 | `browser_snapshot()` | 页面结构+交互元素 |
| 滚动 | `browser_scroll(direction="down")` | 上下滚动 |
| 返回 | `browser_back()` | 后退 |
| 按键 | `browser_press(key="Enter")` | 键盘操作 |
| 获取图片 | `browser_get_images()` | 页面所有图片 |

### 标准操作流程

```bash
# 1. 打开页面
browser_navigate(url="https://目标URL")

# 2. 等待加载后提取数据
browser_console(expression="document.body.innerText")

# 3. 如果需要点击按钮
browser_snapshot()  # 获取ref ID
browser_click(ref="@eN")  # 点击对应元素
```

### ⚠️ 关键注意事项

1. **config必须用`ws://`不是`http://`**：`ws://127.0.0.1:9222`
2. **改完config必须`/reset`**：当前session不生效
3. **Chrome一旦跑起来不要杀**：不要因为某次调用失败就杀Chrome重来
4. **browser_console返回JSON**：需要解析返回值，不是直接文本
5. **Chrome快捷方式已配置CDP参数**：从开始菜单启动即可，不用手动加参数
6. **定时任务不要杀Chrome**：直接检查端口，通了就用，不通再启动
7. **如果Chrome更新覆盖了快捷方式**：需要重新添加`--remote-debugging-port=9222`参数

### ⚠️⚠️⚠️ Chrome单实例行为（血的教训，2026-07-03）

**Chrome是单实例应用。** 如果Chrome已经在运行，再启动一个带`--remote-debugging-port=9222`的Chrome，它**不会创建新进程**，而是打开一个新窗口到已有的Chrome会话。已有的会话没有CDP参数，所以端口9222永远不会开。

**症状**：
- Chrome进程在跑，`--remote-debugging-port=9222`参数也在命令行里
- 但`curl localhost:9222`无响应
- 用户看到一个新Chrome窗口，但不是他平时用的那个

**根本原因**：Chrome检测到已有会话，把新窗口合并到旧会话，CDP参数被忽略。

**正确做法**：Chrome必须从一开始就带CDP参数启动。如果Chrome已经在跑，不能通过启动新实例来开启CDP。

**定时任务的正确流程**：
1. 检查端口9222是否通
2. 通了 → 直接用browser工具
3. 不通 → Chrome可能没启动或没带CDP参数
4. **不要杀Chrome重启**（会导致用户看到新Chrome窗口）
5. 告知用户：需要关掉Chrome，从开始菜单重新启动（快捷方式已配置CDP参数）

**用户原话**："我平常用的chrome是登录了我的谷歌账号的，那你打开那个是没有账号登录的"

## 方案B（备选）：OpenCLI浏览器桥

**当Hermes browser工具不可用时回退。** 需要OpenCLI daemon + Browser Bridge扩展。

### 前置条件

1. Chrome在运行（用默认用户目录，保持登录态）
2. OpenCLI Browser Bridge扩展已安装并连接
3. Daemon正在运行

### 检查连接状态

```bash
# ⚡ 用daemon status（<2秒），不要用doctor（可能超时30s+）
opencli daemon status
# 应显示：Extension: connected

# 如果断开
opencli daemon restart
sleep 5
opencli daemon status
```

### 工具对照表

| 操作 | OpenCLI命令 | 说明 |
|------|-----------|------|
| 打开页面 | `opencli browser douyin open "URL"` | 打开页面 |
| 执行JS | `opencli browser douyin eval "js"` | eval提取 |
| 截图 | `opencli browser douyin screenshot "path"` | 截图保存 |
| 点击元素 | `opencli browser douyin click "[N]"` | 用编号点击 |
| 查找元素 | `opencli browser douyin find --text "文本"` | 查找DOM |
| 页面状态 | `opencli browser douyin state` | 查看状态 |

### 标准操作流程

```bash
# 1. 打开页面
opencli browser douyin open "https://目标URL"
sleep 5

# 2. 提取数据
opencli browser douyin eval "document.body.innerText"

# 3. 点击按钮（先find再click）
opencli browser douyin find --text "按钮文本"
opencli browser douyin click "[N]"
```

### ⚠️ OpenCLI注意事项

1. **session名必须用`douyin`**
2. **每次操作间加`sleep 5-8`**，模拟人操作
3. **`find`必须用`--text`/`--css` flag**，不能用位置参数
4. **`--background`标志不存在**，直接用前台模式
5. **Chrome必须用默认用户目录**（保持登录态），不是`D:/chrome-cdp`

## 选择决策树

```
需要操作网页？
├── 检查Chrome CDP端口9222是否通
│   ├── 通 → 用Hermes browser工具（方案A）
│   └── 不通 → 启动Chrome带CDP → 重试方案A
│       └── 启动失败 → 回退方案B（OpenCLI）
└── 检查OpenCLI daemon状态
    ├── connected → 用OpenCLI（方案B）
    └── disconnected → 重启daemon → 重试方案B
        └── 仍失败 → 报告错误，等待用户介入
```

## 搜索热点/新闻的通用方法

**首选：Hermes browser工具**
```bash
browser_navigate(url="https://www.toutiao.com/search?keyword=关键词")
browser_console(expression="document.body.innerText")
```

**备选：OpenCLI**
```bash
opencli browser douyin open "https://www.toutiao.com/search?keyword=关键词"
sleep 5
opencli browser douyin eval "document.body.innerText"
```

**支持的平台URL模板：**

| 平台 | URL |
|------|-----|
| 今日头条 | `https://www.toutiao.com/search?keyword=XXX` |
| 微博 | `https://s.weibo.com/weibo?q=XXX` |
| 小红书 | `https://www.xiaohongshu.com/search_result?keyword=XXX` |
| 知乎 | `https://www.zhihu.com/search?type=content&q=XXX` |
| 百度 | `https://www.baidu.com/s?wd=XXX` |
| 抖音 | `https://www.douyin.com/search/XXX` |

## Pitfalls

### Chrome单实例行为导致CDP端口不开
- **症状**：Chrome进程在跑，`--remote-debugging-port=9222`在命令行里，但`curl localhost:9222`无响应
- **原因**：Chrome是单实例应用。如果Chrome已经在运行，启动新实例会合并到旧会话，CDP参数被忽略
- **解决**：必须关掉所有Chrome窗口，从开始菜单重新启动（快捷方式已配置CDP参数）
- **绝对不要**：杀掉Chrome再重启（会导致用户看到新Chrome窗口，丢失Google账号登录态）

### Chrome没有Google账号登录
- **症状**：打开Chrome发现没有登录Google账号，书签、密码都没了
- **原因**：启动Chrome时指定了错误的`--user-data-dir`路径（如C盘，但实际在E盘）
- **解决**：不要指定`--user-data-dir`，让Chrome自动用默认目录
- **⚠️ 关键**：Chrome会自动检测用户的默认数据目录，不需要手动指定

### Chrome快捷方式被更新覆盖
- **症状**：定时任务又开始杀Chrome重启
- **原因**：Chrome更新可能覆盖快捷方式，丢失`--remote-debugging-port=9222`参数
- **解决**：重新添加参数到快捷方式
- **检查方法**：`powershell.exe -NoProfile -Command "(New-Object -ComObject WScript.Shell).CreateShortcut('C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk').Arguments"`

### Chrome反复闪烁问题
- **原因**：某次调用失败就杀Chrome重来
- **解决**：不要杀Chrome，先检查其他原因（config没刷新、URL写错）

### CDP连接失败
- **症状**：`browser_navigate`超时或报错
- **排查**：`curl -s http://localhost:9222/json/version`
- **解决**：检查Chrome是否带`--remote-debugging-port=9222`启动

### OpenCLI "Browser Bridge extension not connected"
- **快速修复**：`opencli daemon restart` → `sleep 5` → `opencli daemon status`
- **如果Chrome没开**：先启动Chrome，等10-15秒让扩展连接

### CAMOFOX_URL陷阱
- `.env`中`CAMOFOX_URL`指向不存在的Camofox会导致browser工具失败
- 解决：注释掉`.env`中的`CAMOFOX_URL`行，然后`/reset`

### PYTHONHOME冲突
- 用yt-dlp/Whisper时可能遇到
- 解决：命令前加`unset PYTHONHOME`

### eval返回JSON而非文本
- `browser_console`返回的是JSON序列化结果
- 需要解析返回值中的`result`字段

### vision_analyze在Xiaomi上的问题
- mimo-v2.5拒绝tool message中的图片格式
- **绝对不要用截图+vision_analyze方案**，直接用eval提取文本

### PWA/Manifest路径问题（子路径部署）
- **症状**：浏览器报 `icon.png 404` + `Error while trying to use the following icon from the Manifest`
- **原因**：站点部署在子路径（如 `/bazi/`）时，manifest.json 里的 icon src 写成了 `/assets/icon.png` 而不是 `/bazi/assets/icon.png`
- **排查**：检查 manifest.json 中所有 `src` 路径是否包含完整的子路径前缀
- **注意**：可能有多个 manifest.json（根目录 + public/），确认 HTML 引用的是哪个
- **修复**：改 manifest 路径后重新部署（Vercel 等平台需 push 代码或重新上传）
