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

```bash
# 1. 先杀掉已有Chrome（必须用PowerShell）
powershell.exe -NoProfile -Command "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"
sleep 3

# 2. 用独立用户目录启动（避免lockfile冲突）
mkdir -p "D:/chrome-cdp"
"/c/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:/chrome-cdp" --no-first-run --restore-last-session &

# 3. 验证端口（必须看到JSON输出）
sleep 8 && curl -s http://localhost:9222/json/version
```

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
5. **必须用独立`--user-data-dir`**：否则lockfile冲突导致端口不开

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
