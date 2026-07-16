---
name: douyin-data-check
description: "抖音数据查看 + 热点/新闻搜索。用OpenCLI复用Chrome登录态操作网站（创作者中心/头条/微博/小红书/知乎），eval提取文本数据。"
tags: ["douyin", "data", "analytics", "opencli"]
triggers:
  - "看看数据"
  - "抖音数据"
  - "查看播放量"
  - "视频数据"
  - "看看热点"
  - "今天热点"
  - "搜热点"
  - "热搜"
  - "搜新闻"
  - "看看新闻"
  - "搜小红书"
  - "搜微博"
  - "看看知乎"
---

# 抖音数据查看 Skill

## ⚠️ 核心工具：Hermes Browser Tools（首选）或 OpenCLI

**首选方案：Hermes内置browser工具（通过CDP连接现有Chrome）。** 不需要OpenCLI daemon，直接用browser_navigate/browser_console操作浏览器，复用登录态。

**备选方案：OpenCLI** — 当browser工具不可用时回退。

### Hermes Browser 工具配置（2026-07-03验证，Mac已跑通）

**前置条件**：Chrome必须以远程调试模式启动，Hermes通过CDP协议连接。

**Config设置**（必须用`ws://`协议，不是`http://`）：
```bash
hermes config set browser.cdp_url "ws://127.0.0.1:9222"
```

**⚠️⚠️⚠️ Windows Chrome CDP启动的正确方式（2026-07-03血的教训，2026-07-12更新）**

**首选方案：OpenCLI daemon restart（最可靠）**。手动启动Chrome带`--remote-debugging-port=9222`在很多Windows机器上会因lockfile问题静默失败（Chrome进程启动了但端口不开）。最可靠的方法是让OpenCLI自己管理Chrome：

```bash
# 1. 先杀掉所有Chrome（必须用PowerShell，bash的taskkill /F有时杀不干净）
powershell.exe -NoProfile -Command "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"
sleep 3

# 2. 重启OpenCLI daemon（它会自动启动Chrome并连接）
opencli daemon restart
sleep 8

# 3. 验证连接（必须看到Extension: connected）
opencli daemon status
```

**备选方案：手动启动Chrome带CDP（仅在daemon restart失败时使用）**

**必须用独立`--user-data-dir`**，否则Chrome lockfile冲突导致端口9222永远不开：

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --no-first-run --restore-last-session --user-data-dir="C:/Users/Administrator/AppData/Local/Google/Chrome/User Data Copy" &
sleep 10 && curl -s http://localhost:9222/json/version
```

**⚠️ 常见失败原因**：如果用默认用户目录（`AppData/Local/Google/Chrome/User Data`），Chrome的lockfile会阻止第二个实例绑定调试端口。症状：Chrome进程在跑，`--remote-debugging-port=9222`参数也在，但`curl localhost:9222`无响应。

**⚠️ 不要用bash的`taskkill /F`**：MSYS环境下`taskkill /F /IM chrome.exe`经常杀不干净（PowerShell编码问题）。必须用`powershell.exe -NoProfile -Command "Get-Process chrome | Stop-Process -Force"`。

**⚠️ Config必须用`ws://`不是`http://`**：`browser.cdp_url`的值必须是`ws://127.0.0.1:9222`，不是`http://localhost:9222`。用`http://`会导致连接失败。

**⚠️ CAMOFOX_URL陷阱**：如果`.env`中设置了`CAMOFOX_URL=http://localhost:9377`但Camofox未安装，browser工具会尝试连接Camofox而失败。解决：注释掉`.env`中的`CAMOFOX_URL`行。

**⚠️ 改完config必须`/reset`**：`browser.cdp_url`和`.env`改动在当前session不生效，必须`/reset`开新session。

**Hermes Browser工具对照表**：

| OpenCLI命令 | Hermes工具 | 说明 |
|------------|-----------|------|
| `opencli browser douyin open "URL"` | `browser_navigate(url="URL")` | 打开页面 |
| `opencli browser douyin eval "js"` | `browser_console(expression="js")` | 执行JavaScript |
| `opencli browser douyin screenshot "path"` | `browser_vision()` | 截图 |
| `opencli browser douyin click "[N]"` | `browser_click(ref="@eN")` | 点击元素 |
| `opencli browser douyin find --text "text"` | `browser_snapshot()` | 获取页面快照 |

**⚠️ 注意**：browser_console执行JS后返回的是JSON序列化结果，不是直接的文本。需要解析返回值。

## ⚠️⚠️⚠️ 核心原则：Hermes Browser是默认工具，OpenCLI是备选

**任何需要访问网页的任务，第一步永远是检查Hermes browser工具是否可用（CDP连接）。** 如果不可用，再回退到OpenCLI。

用户原话："老老实实说你是不是忘记怎么用opencli了，我发现gateway每天都会用这个来查数据，你这个cli却老忘记怎么用"

**正确流程**：
1. `opencli daemon status` → 检查连接状态
2. 如果断开 → `opencli daemon restart` → 等待5秒 → 再检查
3. 如果Chrome没开 → 启动Chrome → 等待10-15秒
4. 连接成功后才开始操作

**不要做的事**：
- ❌ 一上来就用curl/API搜索新闻
- ❌ 忘记OpenCLI直接用其他方法
- ❌ 搜热点时没想到用OpenCLI打开网页

**⚠️⚠️⚠️ 工作流铁律：Chrome一旦跑起来就不要杀它**

用户明确说过："你能不能报到一下进度呢，别自己乱来"、"你就是个傻逼，我一直看着浏览器开了又关"。

**正确流程**：
1. 启动Chrome带调试端口（用background模式）
2. 等8秒验证端口通了
3. 直接用browser_navigate/browser_console操作
4. **不要因为某次调用失败就杀Chrome重来** — 先检查是不是其他原因（config没刷新、URL写错等）

**错误流程**（用户看到Chrome反复闪烁，非常烦）：
- ❌ 测试失败 → 杀Chrome → 重启Chrome → 再测试 → 再失败 → 再杀...
- ❌ 没验证端口就急着用browser工具
- ❌ 忘了`/reset`导致config没生效，然后怪Chrome没开

**OpenCLI的用途远不止查抖音数据**：
- 搜热点：打开头条/微博搜索页，eval提取文本
- 查公司信息：打开企查查/天眼查
- 找对标账号：打开抖音搜索页
- 任何需要浏览器的操作都可以用OpenCLI

## ⚠️⚠️⚠️ 提取数据方式（用户明确偏好）

**对于定时任务（cron job）和常规数据查看，直接用eval提取文本，不要用vision_analyze。**

```bash
# 正确：直接eval
opencli browser douyin eval "document.body.innerText"

# 不要这样做：
# opencli browser douyin screenshot "xxx.png"
# vision_analyze(image_url="xxx.png", question="...")
```

**原因**：
1. eval是100%可靠的方法，返回结构化文本可直接解析
2. vision_analyze可能失败（PackyAPI 503等）
3. 截图+vision流程慢且不稳定
4. 用户明确要求"不要用vision_analyze，直接用eval"

**唯一使用vision_analyze的场景**：需要视觉验证页面布局时（如确认截图中显示的内容）。

## ⚡⚡⚡ Cron Job 快速参考（定时任务专用）

**定时任务（cron job）没有用户交互，时间有限。必须用最可靠的方法。**

**两步走方案（2026-06-16验证）：**

```bash
# 1. 先读发展日志
# skill_view(name='douyin-data-check', file_path='references/发展日志.md')

# 2. 打开数据中心内容分析页，切换到投稿列表
opencli browser douyin open "https://creator.douyin.com/creator-micro/data-center/content"
sleep 8
opencli browser douyin eval "var el = Array.from(document.querySelectorAll('label')).find(e => e.textContent.trim() === '投稿列表' && e.offsetParent !== null); el?.click(); el ? 'clicked' : 'not found'"
sleep 5

# 3. 提取全部视频列表数据（播放量、完播率、5s完播率、2s跳出率等）
opencli browser douyin eval "document.body.innerText"

# 4. 如果需要最新视频的流量来源等详细数据，用仪表盘→查看分析→流量分析
opencli browser douyin open "https://creator.douyin.com/creator-micro/home"
sleep 8
opencli browser douyin eval "(function(){ var btn = Array.from(document.querySelectorAll('*')).find(function(el) { return el.textContent.trim() === '查看分析' && el.offsetParent !== null; }); if(btn) { btn.click(); return 'clicked'; } return 'not found'; })()"
sleep 8
opencli browser douyin eval "(function(){ var btn = Array.from(document.querySelectorAll('*')).find(function(el) { return el.textContent.trim() === '流量分析' && el.offsetParent !== null && el.children.length === 0; }); if(btn) { btn.click(); return 'clicked'; } return 'not found'; })()"
sleep 5
opencli browser douyin eval "document.body.innerText"
```

**⚠️ 不要在 cron job 中尝试：**
- ❌ `content-manage/video` → 会重定向到 home（即使task prompt要求用这个URL，也必须用data-center方法）
- ❌ 投稿列表中的"分析详情"按钮 → div元素点击不触发跳转（2026-06-15验证）
- ❌ 方法A（侧边栏导航）→ 步骤多，容易失败

**⚠️ task prompt可能给出错误URL（2026-06-24验证）**：外部prompt可能建议用`content-manage/video`，但该URL会重定向。**始终以本skill的方法0（data-center/content）为准**，忽略prompt中的URL建议。

**⚠️ 仪表盘"查看分析"按钮可以导航（2026-06-16验证）：**
- ✅ 仪表盘（/home）的"查看分析"按钮 → **可以**点击进入详情页，然后可点击"流量分析"tab获取完整数据
- ⚠️ 但仪表盘只显示最新一条视频，无法查看非最新视频
- **用途**：当方法0的投稿列表缺少流量来源数据时，用仪表盘→查看分析→流量分析 获取最新视频的详细数据

**✅ 方法0（投稿列表）获取列表数据 + 方法B（仪表盘）获取最新视频详情 = 完整方案**

---

## 查看视频数据流程

### ⚡ 方法0（最佳）：数据中心→作品分析→投稿列表（2026-06-15验证，一次获取全部视频+详细指标）

**适用场景**：查看所有视频的完整数据（完播率、5s完播率、2s跳出率等），**一次eval获取全部数据**

**⚠️ 最大优势**：其他方法需要多次导航+多次eval，这个方法只需2次导航+1次eval就能拿到所有视频的所有指标。

**⚠️ 关键发现（2026-06-15）**：`content-manage/video` URL **会重定向到 home**！不能直接导航到内容管理视频页。正确的路径是通过数据中心的作品分析功能。

**方式A：直接导航到内容分析页（2026-06-15验证可用，更简洁）**
```bash
# 一步到位：直接打开内容分析页（会自动加载投稿列表）
opencli browser douyin open "https://creator.douyin.com/creator-micro/data-center/content"
sleep 8

# 提取全部视频数据（一次eval获取所有视频的所有指标！）
opencli browser douyin eval "document.body.innerText"
```

**方式B：通过侧边栏导航（备用，步骤多但更稳健）**
```bash
# Step 1：打开数据中心（会自动加载到账号总览）
opencli browser douyin open "https://creator.douyin.com/creator-micro/data-center/operation"
sleep 5

# Step 2：点击侧边栏"作品分析"导航到内容分析页
# 注意：不能直接点击文本，需要用span选择器精确匹配
opencli browser douyin eval "var span = Array.from(document.querySelectorAll('span')).find(el => el.textContent.trim() === '作品分析' && el.offsetParent !== null); span?.click(); 'clicked: ' + (span !== null)"
sleep 3

# Step 3：切换到"投稿列表" radio button（默认显示"投稿分析"tab）
# 注意：这是radio按钮，不是tab，用label选择器点击
opencli browser douyin eval "var el = Array.from(document.querySelectorAll('label')).find(e => e.textContent.trim() === '投稿列表' && e.offsetParent !== null); el?.click(); el ? 'clicked' : 'not found'"
sleep 3

# Step 4：提取全部视频数据（一次eval获取所有视频的所有指标！）
opencli browser douyin eval "document.body.innerText"
```

**⚠️ 表格行渲染（2026-07-16更新）**：投稿列表表格的渲染行为随页面版本变化。2026-07-16实测：仅显示10条视频（V19-V28），而非全部23条。2026-07-15曾显示全部25条。**可能是页面版本回退或表格有分页/虚拟滚动**。早期版本（2026-06-26至2026-07-08）也有类似限制。

**验证方法**：
```bash
# 检查实际渲染行数
opencli browser douyin eval "(function(){ var rows = document.querySelectorAll('table tbody tr'); var count = 0; for (var i = 0; i < rows.length; i++) { if (rows[i].querySelectorAll('td').length >= 5) count++; } return 'Video rows: ' + count; })()"
```

**如果行数不足（仍受虚拟滚动限制）**：
1. 对于cron job（只关注新视频+近期变化）：前10-20行足够——新视频在最前面
2. 如果需要全部视频数据：使用侧边栏→作品管理（方法A），该页面不使用虚拟滚动
3. 不要尝试通过JavaScript强制加载更多行：虚拟滚动是React组件层面的控制

```bash
# Step 4：提取视频列表数据
opencli browser douyin eval "document.body.innerText"
```

**🔴 评论/分享互换：14次审计遗留的根因（2026-06-30总结）**

这个错误已经连续14次审计被发现但从未在数据采集阶段修复。根因：**表格数据正确，但诊断文本写反了。**

**错误模式**：表格显示 comments=0, shares=2（正确），但诊断文本写成"评论2，分享0"（错误）。

**原因**：诊断文本是手写的，容易凭直觉把顺序搞反（发展日志列顺序是"点赞→评论→分享"，但数据源列顺序是"点赞→分享→评论"）。

**修复方法**：写诊断文本时，**逐字对照表格行**：
```
表格行: V23 | ... | 4 | 0 | 2 | 1 | 已完成 |
                          ↑  ↑  ↑  ↑
                        点赞 评论 分享 收藏

诊断文本: 点赞4，评论0（对应cells[10]），分享2（对应cells[9]），收藏1
```

**⚠️ 强制验证步骤**：写完诊断文本后，对比诊断中的评论数/分享数与表格行中的对应值。如果表格说"评论0、分享2"但诊断说"评论2、分享0"，就是互换错误。

**🔴🔴🔴 强制验证步骤（每次写入前必须执行）**

**写入发展日志前，必须逐字对照页面数据和日志列顺序：**

```
页面列顺序（cells索引）:  点赞[8] → 分享[9] → 评论[10] → 收藏[11]
日志列顺序:              点赞 → 评论 → 分享 → 收藏

⚠️ 评论和分享的顺序是反的！
```

**逐条验证方法**：
```bash
# 1. 提取页面数据
opencli browser douyin eval "(function(){ var rows = document.querySelectorAll('table tbody tr'); var r = []; for (var i = 0; i < rows.length; i++) { var c = rows[i].querySelectorAll('td'); if (c.length >= 5) { r.push('ROW' + i + ': 点赞=' + c[8].textContent.trim() + ' 分享=' + c[9].textContent.trim() + ' 评论=' + c[10].textContent.trim() + ' 收藏=' + c[11].textContent.trim()); } } return r.join('\\n'); })()"

# 2. 写入日志时，必须确认：
# 页面"点赞=X 分享=Y 评论=Z 收藏=W"
# → 日志写"点赞=X 评论=Z 分享=Y 收藏=W"
# 即：日志评论=页面评论，日志分享=页面分享，不要交换！
```

**2026-07-14教训（回归式修复，2026-07-15发现）**：即使有上述文档，agent仍然在batch更新时把V23/V21的评论和分享搞反了。根因：写patch时凭直觉认为"评论应该在分享前面"，没有逐条对照页面数据。**每次写入前必须用上述方法逐条验证。**

**⚠️ 表格列顺序映射（防止评论/分享互换，2026-07-06更新）**：数据中心投稿列表的表格有**15列**（不是16列），列顺序与发展日志**不同**，必须按以下映射转换：

**⚠️ 实际列索引（2026-07-06实测验证）**：
```
cells[0]:  作品名称（标题）
cells[1]:  审核状态（"通过"）
cells[2]:  播放量 ← ⚠️ 不是cells[3]！
cells[3]:  完播率
cells[4]:  5s完播率
cells[5]:  封面点击率（通常为"-"）
cells[6]:  2s跳出率
cells[7]:  平均播放时长
cells[8]:  点赞量
cells[9]:  分享量
cells[10]: 评论量
cells[11]: 收藏量
cells[12]: 主页访问量
cells[13]: 粉丝增量
cells[14]: 操作（"分析详情"）
```

**⚠️ 重要**：发布日期不在表格cells中！日期显示在innerText文本里但不是独立的td元素。提取日期需要从innerText解析。

| 数据中心列顺序 | 发展日志列顺序 |
|---------------|---------------|
| 点赞量 (cells[8]) | 点赞 |
| 分享量 (cells[9]) | 分享 |
| 评论量 (cells[10]) | 评论 |
| 收藏量 (cells[11]) | 收藏 |

**⚠️ 关键**：数据中心是"点赞→分享→评论→收藏"，发展日志是"点赞→评论→分享→收藏"。评论和分享的顺序是**反的**！这是12次审核都发现评论/分享互换的根本原因。

```javascript
// ✅ 正确的eval提取代码（已验证2026-07-06）
// 先用这个验证列索引：
// opencli browser douyin eval "(function(){ var rows = document.querySelectorAll('table tbody tr'); var r = []; for (var i = 0; i < rows.length; i++) { var c = rows[i].querySelectorAll('td'); if (c.length >= 5) { var a = []; for (var j = 0; j < Math.min(c.length, 16); j++) { a.push(j + ':' + c[j].textContent.trim().substring(0, 20)); } r.push('ROW' + i + ' [' + c.length + ' cells]: ' + a.join(' | ')); } } return r.join('\\n'); })()"

// 正确提取数据：
data.push({
  plays: cells[2].textContent.trim(),     // 播放量（⚠️ 不是cells[3]！）
  completion: cells[3].textContent.trim(), // 完播率
  fiveSec: cells[4].textContent.trim(),    // 5s完播率
  twoSec: cells[6].textContent.trim(),     // 2s跳出率（⚠️ 不是cells[7]！）
  avgDur: cells[7].textContent.trim(),     // 平均播放时长
  likes: cells[8].textContent.trim(),      // 点赞量
  shares: cells[9].textContent.trim(),     // 分享量
  comments: cells[10].textContent.trim(),  // 评论量
  fav: cells[11].textContent.trim()        // 收藏量
})

// ✅ 正确的映射到发展日志
// likes → 点赞
// comments → 评论（注意：不是shares！）
// shares → 分享（注意：不是comments！）
// fav → 收藏
```

**⚠️ 首次提取前必须验证列索引**：不同页面版本的列数可能不同（15列vs16列）。在写提取代码前，先用上方的验证代码确认实际列索引。本次session（2026-07-06）实测：15列，plays=cells[2]，不是cells[3]。

**返回的数据结构**（直接包含所有指标，无需二次点击）：
```
作品名称 | 发布时间    审核状态  播放量  完播率  5s完播率  封面点击率  2s跳出率  平均播放时长  点赞量  分享量  评论量  收藏量  主页访问量  粉丝增量  操作

做自己的代价，你承受得起吗？... 2026-06-14 16:51  1min视频  通过  334  5.51%  38.21%  -  27.86%  8秒  3  0  0  0  0  0  分析详情
80后对自己的人生开发还不足1%... 2026-06-13 16:47  1-3min视频  通过  1451  1.12%  44.7%  -  14.65%  14秒  6  0  1  1  0  0  分析详情
...
```

**⚠️ "分析详情"按钮在OpenCLI中无法跳转**：投稿列表中的"分析详情"按钮是div元素，点击后不会导航到新页面。但表格本身已包含所有关键指标，无需点击。

**⚠️ 页面还包含"投稿概览"汇总数据**：
- 周期内投稿量、条均点击率、条均5s完播率、条均2s跳出率
- 条均播放时长、播放量中位数、条均点赞数、条均评论量、条均分享量
- 投稿表现图表（播放量均值、最高、最低）

**⚠️ 数据中心汇总值可能与手动计算不一致（2026-07-15发现）**：数据中心显示的"均值"可能排除了"仅自己可见"状态的视频（如V28），导致汇总值高于手动计算的全量均值。例如：数据中心显示均值1,395.56，但包含V28的全量均值为1,342。**规则**：以手动计算的全量均值为准，不要直接引用数据中心的汇总值做诊断判断。

**⚠️ 侧边栏导航的坑**：
- "作品分析"在侧边栏中是span元素，不是a标签，不能用find --text点击
- 必须用 `document.querySelectorAll('span')` 精确匹配文本
- 点击后URL变为 `/data-center/content`

### ⚡ 方法A：从内容管理页查看所有视频详情（推荐，2026-06-09验证可用）

**适用场景**：查看所有视频的详细数据（完播率、2s跳出率等），尤其是需要检查非最新视频时

**⚠️ 重要更新（2026-06-09验证）**：内容管理页（`/content-manage/video`）的"查看分析"按钮**可以**通过eval找到并点击！之前的结论"按钮不可用"可能是页面加载时序问题（eval时页面尚未完全渲染）。实测通过`Array.from(document.querySelectorAll('*')).filter(el => el.textContent.trim() === '查看分析' && el.offsetParent !== null)`可以找到所有5个"查看分析"按钮，点击第N个即可进入第N个视频的详情页。

**正确流程**（⚠️ 2026-06-12血的教训：不要用"近期作品"tab，只显示7天！必须用侧边栏→作品管理）：

### ⚠️ 最佳方法：侧边栏导航到作品管理（2026-06-12验证）

**⚠️ 用户明确纠正：不要用"近期作品"tab，它只显示最近7天的视频！用"内容管理→作品管理"才能看到全部视频。**

**正确流程**（⚠️ 2026-06-12实测：作品管理页没有"查看分析"按钮！必须回到内容管理概览页点击）：
1. 导航到 `https://creator.douyin.com/creator-micro/content-manage/video`
2. 点击侧边栏"内容管理"展开子菜单
3. 点击"作品管理"进入视频列表（显示全部视频，不受7天限制）
4. 提取所有视频的基础数据（播放、点赞、评论、分享）
5. **⚠️ 作品管理页没有"查看分析"按钮！** 只有"编辑作品""设置权限"等按钮
6. **要查看详细数据，必须回到内容管理概览页**（重新 `open` 该URL），点击"最新作品"区域的"查看分析"按钮
7. 提取详情页数据
8. 点击"流量分析"tab获取完整数据

```bash
# Step 1：打开内容管理页
opencli browser douyin open "https://creator.douyin.com/creator-micro/content-manage/video"
sleep 8

# Step 2：点击侧边栏"内容管理"展开子菜单
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '内容管理' && el.offsetParent !== null && el.children.length === 0).click()"
sleep 2

# Step 3：点击"作品管理"进入完整视频列表（⚠️ 这里才有全部视频！）
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '作品管理' && el.offsetParent !== null && el.children.length === 0).click()"
sleep 3

# Step 4：提取所有视频的基础数据（显示"共 N 个作品"）
# ⚠️ 作品管理页只有基础数据（播放/点赞/评论/分享），没有完播率等详细指标
opencli browser douyin eval "document.body.innerText"

# Step 5：回到内容管理概览页点击"查看分析"（⚠️ 作品管理页没有此按钮！）
opencli browser douyin open "https://creator.douyin.com/creator-micro/content-manage/video"
sleep 8

# Step 6：点击"查看分析"进入详情页（只能点击"最新作品"区域的按钮）
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).filter(el => el.textContent.trim() === '查看分析' && el.offsetParent !== null)[0].click()"
sleep 5

# Step 7：提取详情页数据（完播率、2s跳出率等）
opencli browser douyin eval "document.body.innerText"

# Step 8：点击"流量分析"tab获取详细数据
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '流量分析' && el.offsetParent !== null && el.children.length === 0).click()"
sleep 5

# Step 9：提取流量分析数据
opencli browser douyin eval "document.body.innerText"
```

**⚠️ 关键发现（2026-06-12实测）**：
- **作品管理页没有"查看分析"按钮**！该页面只有"编辑作品""设置权限""作品置顶""删除作品"按钮
- **"查看分析"按钮只存在于内容管理概览页**（"最新作品"区域）
- **这意味着：每次查看新视频的详细数据时，都需要回到概览页，只能点击"最新作品"区域的那个按钮**
- 如果要查看非最新视频的详细数据，需要在概览页找到对应的"查看分析"按钮（可能在"近期作品"区域）

**⚠️ 关键发现**：
- "近期作品"tab **只显示最近7天的视频**，更早的视频不会出现（实测：账号有12个视频，但近期作品只显示5个）
- 仪表盘（`/home`）只显示最新一条视频
- **老视频（>7天）的数据只能从发展日志（references/发展日志.md）获取**，创作者中心看不到
- 内容管理页概览可以查看**近7天内任意视频**的详情数据（通过"查看分析"按钮）
- **⚠️ 作品管理页没有"查看分析"按钮**，只有基础数据（播放/点赞/评论/分享），要获取完播率等详细指标必须回到概览页

### 方法B：从仪表盘查看最新视频详情（备用）

**适用场景**：只需要查看最新视频的详细数据

```bash
# Step 1：打开仪表盘
opencli browser douyin open "https://creator.douyin.com/creator-micro/home"
sleep 8

# Step 2：提取仪表盘数据
opencli browser douyin eval "document.body.innerText"

# Step 3：点击"查看分析"进入详情页
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '查看分析' && el.offsetParent !== null).click()"
sleep 3

# Step 4-7：同方法A的Step 5-7
```

onPreview触发的预览面板仍在跨域iframe中，无法eval访问。但"查看分析"按钮可以直接点击进入详情页。

**⚠️ 仪表盘限制**：仪表盘（`/home`）只显示最新一条视频，无法看到所有视频。如需查看所有视频的列表数据或非最新视频的详情数据，使用内容管理页（`/content-manage/video`）。

**✅ 内容管理页已验证可以查看任意视频详情**（2026-06-09验证）：点击"近期作品"tab查看所有视频列表，然后点击对应视频的"查看分析"按钮进入详情页。实测通过eval找到所有"查看分析"按钮并成功点击。

```bash
# Step 1：打开仪表盘
opencli browser douyin open "https://creator.douyin.com/creator-micro/home"
sleep 8  # 等待页面加载

# Step 2：提取仪表盘数据（包含最新视频的基础数据）
opencli browser douyin eval "document.body.innerText"

# Step 3：点击"查看分析"进入详情页
opencli browser douyin eval "
(function(){
  var btn = Array.from(document.querySelectorAll('*')).find(function(el) { 
    return el.textContent.trim() === '查看分析' && el.offsetParent !== null; 
  });
  if(btn) { btn.click(); return 'clicked'; }
  return 'not found';
})()
"
sleep 5

# Step 4：提取总览数据（播放量、点赞、完播率、2s跳出率等）
opencli browser douyin eval "document.body.innerText"

# Step 5：点击"流量分析" tab 获取详细数据
opencli browser douyin eval "
(function(){
  var btn = Array.from(document.querySelectorAll('*')).find(function(el) { 
    return el.textContent.trim() === '流量分析' && el.offsetParent !== null; 
  });
  if(btn) { btn.click(); return 'clicked'; }
  return 'not found';
})()
"
sleep 5

# Step 6：提取流量分析数据（5s完播率、平均播放时长、流量来源等）
opencli browser douyin eval "document.body.innerText"
```

**返回的文本包含**：完播率、平均播放时长、2s跳出率、5s完播率、平均播放占比、点赞率、评论率、分享率、流量来源（推荐页/朋友页/搜索等）

### 完整方法：查看所有视频数据（列表页+详情页）

**适用场景**：需要查看所有视频的列表数据和详情数据，或需要对比多个视频

**⚠️ 内容管理页"查看分析"按钮已验证可用（2026-06-09）**。通过eval可以找到所有"查看分析"按钮并点击进入详情页。

onPreview触发的预览面板仍在跨域iframe中，无法eval访问。

⚠️ **注意**：此部分与上方"方法A"流程相同，都必须用侧边栏→作品管理路径，不要用"近期作品"tab。

### Step 2：截图
```bash
opencli browser douyin screenshot "D:/hermes-agent/douyin_data.png"
```
**⚠️ vision_analyze已不可用（2026-06-22确认）**：mimo-v2.5的Xiaomi API拒绝tool message中的图片格式（报`400: Param Incorrect: text is not set`）。这是服务端breaking change，不是临时故障。**绝对不要用截图+vision_analyze方案**，直接用eval提取文本。

```bash
# ✅ 唯一可靠方法：eval提取文本
opencli browser douyin eval "document.body.innerText"

# ❌ 不要这样做（会报400错误）：
# opencli browser douyin screenshot "xxx.png"
# vision_analyze(image_url="xxx.png", question="...")
```

## ⚠️ 小样本数据解读（播放量<50）

**当视频播放量极低（<50）时，所有比率指标都不具统计意义。** 1/17=5.88%的点赞率看起来"优秀"，但只是1个人点了赞，不代表内容质量。

规则：
- 播放量<50 → 所有比率指标标注"样本太小，不具统计意义"
- 播放量50-200 → 比率指标可参考但需谨慎解读
- 播放量>200 → 比率指标基本可靠
- **诊断时优先看绝对值**（点赞数、评论数）而非比率
- **首次检查（2-5h）的数据尤其不可靠**：播放量可能只有10-30，所有比率都是噪音

**案例**：V18首次检查（5.5h）播放17，点赞率5.88%看似"优秀"但仅1/17。正确诊断：样本太小，无法判断内容质量。

---

## 数据分析标准（2025年更新，参考 `references/抖音推流算法.md`）

| 指标 | 合格 | 优秀 | 说明 |
|------|------|------|------|
| 完播率 | >15% | >30% | 2025年权重已下降，不再是第一指标 |
| 5秒完播率 | ≥50% | >70% | 开头是否抓人，冷启动基础门槛（≥50%视为达标，从"5s完播率<50%"分组中移除） |
| 2秒跳出率 | <30% | <15% | 开头是否抓人 |
| 收藏率 | >2% | >5% | 2025年权重最高！代表"长尾价值" |
| 点赞率 | >3% | >8% | 点赞/播放（权重最低，成本最低） |
| 评论率 | >0.5% | >2% | 评论/播放（带关键词的评论权重更高） |
| 分享率 | >0.3% | >1% | 分享/播放 |
| 平均播放时长 | >30秒 | >60秒 | 视频总时长的占比更重要 |

## ⚠️ 数据分析的重要前提：排除小号互动数据

**用户会用小号（alternate accounts）在视频发布后手动评论来触发算法二次推流。**

规则：
- 24小时内的评论 = 真实观众评论，可作为数据分析依据
- 24小时后的评论 = 可能包含用户小号的互动数据，分析时需注意
- 分析真实互动率时，应以24小时内的数据为准
- 如果发现某视频评论数突然增加但点赞/分享没有同步增长，很可能是小号互动
- 小号评论之间的回复互动不算真实互动率

**原因**：用户发现小号评论可以触发算法重新评估并给予二次推流（详见"运营技巧"章节）。这些评论是运营手段，不是内容质量的反映。

## 运营技巧：小号互动触发二次推流（用户实测验证）

### 原理
当视频推流停止后（播放量停滞），算法不再主动推送。此时如果出现新的互动信号（评论），算法会重新评估该视频的热度，可能给予额外的推送机会。

### 用户实测案例
- 视频1（周末头疼）：发布一晚上只有3个播放，推流完全停止。用户用小号评论了几条，立刻开始推流，最终播放量达到1520+
- 视频9（面试潜规则）：发布后推流停在393，小号评论+大号回复后，播放量涨到1640

### 关键发现
1. 算法对互动的"活跃度变化"敏感，不只是看绝对值
2. 短时间内评论数突然增加（互动速率变化）可以触发算法重新评估
3. 评论之间的回复互动权重更高
4. 这个方法在视频推流停止后依然有效

### ⚠️ 1条评论 = 1500播放量天花板（2026-06-11用户实测）
**核心发现**：用1个小号评论1条，视频播放量上限约1500。要突破1500到2000+，需要更多小号制造更多评论互动。

用户实测数据：
- 1条评论 → 播放量天花板约1500
- 要到2000+ → 需要注册多个小号（建议5-6个）
- 每个小号评论1条 + 大号回复 → 制造多条互动

**操作方法**：
1. 注册5-6个小号
2. 推流停了之后，逐个用小号评论
3. 大号逐个回复
4. 观察播放量变化，找到最小触发量

**注意**：具体需要几条评论能突破到2000，因视频而异（跟完播率、点赞率有关）。用户需要自己测2-3条视频取平均值。

### 操作流程
1. 发布视频后观察6-8小时
2. 如果推流停止（播放量停滞），用小号去评论
3. 评论之间可以互相回复，制造互动
4. 观察是否触发二次推流

### 注意事项
- 不要太频繁使用，可能被算法识别为异常互动模式
- 评论内容要自然，不要千篇一律
- 同一IP/设备的多条评论可能被降权
- 这是运营手段，不能替代内容质量
- 用户只有1个小号时，播放量上限约1500，需要多个小号才能突破

## ⚠️ "查看分析"按钮索引映射陷阱（2026-06-12验证）

**页面上会有重复的"查看分析"按钮！** "最新作品"区域和"近期作品"区域都会显示同一个视频的"查看分析"按钮，导致索引错位。

**实际按钮映射（2026-06-12实测）**：
```
索引0: "最新作品"区域的按钮（最新视频）
索引1: "近期作品"区域的第一个视频（与索引0相同）
索引2: "近期作品"区域的第二个视频
索引3: "近期作品"区域的第三个视频
...
```

**如何确认按钮对应哪个视频**：
```bash
# 提取每个按钮的父元素文本，确认对应关系
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).filter(el => el.textContent.trim() === '查看分析' && el.offsetParent !== null).map((el, i) => { let parent = el.closest('[class*=\"video-card\"]') || el.parentElement.parentElement; let title = parent ? parent.textContent.substring(0, 50) : 'unknown'; return i + ': ' + title; }).join('\\n')"
```

**正确操作**：如果要点击"近期作品"列表中的第N个视频，实际索引是 N+1（因为索引0是"最新作品"区域的按钮）。

**坑**：如果直接用索引0点击，会进入"最新作品"区域的视频详情页，而不是"近期作品"列表中的第一个视频。

---

## ⚠️ "查看分析"按钮是 <div> 不是 <span>

**实测验证（2026-06-10）**：内容管理页的"查看分析"按钮实际是 `<div>` 元素。用 `document.querySelectorAll('span')` 会找不到按钮（返回空数组）。**必须用 `document.querySelectorAll('*')` 才能可靠找到。**

```bash
# ✅ 正确：用 * 选择器
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).filter(el => el.textContent.trim() === '查看分析' && el.offsetParent !== null)[0].click()"

# ❌ 错误：用 span 选择器会找不到
# opencli browser douyin eval "Array.from(document.querySelectorAll('span')).filter(el => el.textContent.trim() === '查看分析' && el.offsetParent !== null)[0].click()"
```

## ⚠️ 必须点"流量分析" tab 看详细数据（血的教训）

总览页只显示基础数据，**流量分析页有更关键的指标**：

### 如何进入流量分析页

**⚠️ 重要更新（2026-06-09修正，2026-06-19再次验证）**：
1. 详情页内容加载在跨域iframe中（`https://www.douyin.com/creatorvideo/{id}`），但可以通过eval提取`document.body.innerText`获取数据
2. **内容管理页（`/content-manage/video`）的"查看分析"按钮已验证可用**：2026-06-09和2026-06-19两次实测通过eval找到并点击成功，可以查看任意视频的详情数据
3. **正确方法**：在内容管理页点击"近期作品"tab查看所有视频，然后点击对应视频的"查看分析"按钮进入详情页
4. **⚠️ URL重定向行为已变化（2026-06-19发现）**：skill中记录`content-manage/video`会重定向到home（2026-06-15验证），但2026-06-19实测该URL可以正常加载内容管理页。重定向可能只在特定条件下发生（如会话过期、页面缓存等）。**建议优先使用该URL，如果重定向则回退到data-center/content**

**方法1（推荐）：侧边栏→作品管理（基础数据） → 回到概览页 → 查看分析 → 流量分析**（可查看全部视频）
```bash
# 1. 打开内容管理页
opencli browser douyin open "https://creator.douyin.com/creator-micro/content-manage/video"
sleep 8

# 2. 点击侧边栏"内容管理"展开子菜单
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '内容管理' && el.offsetParent !== null && el.children.length === 0).click()"
sleep 2

# 3. 点击"作品管理"进入完整视频列表（⚠️ 这里才有全部视频！但没有"查看分析"按钮）
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '作品管理' && el.offsetParent !== null && el.children.length === 0).click()"
sleep 3

# 4. 提取基础数据（播放/点赞/评论/分享）
opencli browser douyin eval "document.body.innerText"

# 5. 回到内容管理概览页（⚠️ 必须重新打开！作品管理页没有"查看分析"按钮）
opencli browser douyin open "https://creator.douyin.com/creator-micro/content-manage/video"
sleep 8

# 6. 点击"查看分析"进入详情页（只能点"最新作品"区域的按钮）
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).filter(el => el.textContent.trim() === '查看分析' && el.offsetParent !== null)[0].click()"
sleep 5

# 7. 点击"流量分析" tab
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '流量分析' && el.offsetParent !== null && el.children.length === 0).click()"
sleep 5

# 8. 提取流量分析数据
opencli browser douyin eval "document.body.innerText"

# ⚠️ 9. 如果需要查看下一个视频，重新打开内容管理页（页面会重置为"最新作品"视图）
opencli browser douyin open "https://creator.douyin.com/creator-micro/content-manage/video"
sleep 5
# 然后重新点击"近期作品"tab（回到步骤2）
```

**方法2：仪表盘 → 查看分析 → 流量分析**（仅限最新视频）
```bash
# 1. 打开仪表盘
opencli browser douyin open "https://creator.douyin.com/creator-micro/home"
sleep 8

# 2. 点击"查看分析"
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '查看分析' && el.offsetParent !== null).click()"
sleep 5

# 3-5. 同方法1的Step 4-5
```

- ✅ 内容管理页的"查看分析"按钮已验证可用（2026-06-09），可以查看任意视频的详情数据
- ✅ 仪表盘的"查看分析"按钮也可以点击进入详情页（仅限最新视频）
- onPreview触发的预览面板仍在跨域iframe中，无法eval访问

### 流量分析页的关键指标

**⚠️ `children.length === 0` 过滤器的使用场景（2026-06-30明确）**：

| 按钮 | 是否需要 `children.length === 0` | 原因 |
|------|----------------------------------|------|
| "流量分析" tab | ✅ 必须加 | HTML/BODY等父容器的textContent也包含"流量分析"，会误匹配 |
| "查看分析"按钮（仪表盘） | ❌ 不要加 | 按钮是`<div>`且有子元素（文字+图标），加了会找不到 |
| "查看分析"按钮（内容管理页） | ❌ 不要加 | 同上 |
| "分析详情"按钮（数据中心） | ❌ 不要加 | 同上，且该按钮不触发跳转 |

**点击"流量分析"tab的坑（2026-06-10验证）**：`Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '流量分析' && el.offsetParent !== null)` 会匹配到 HTML/BODY 等父容器（因为它们的 textContent 也包含"流量分析"），导致返回 undefined。**必须加 `el.children.length === 0` 过滤叶子节点**：
```javascript
// ✅ 正确：过滤叶子节点
Array.from(document.querySelectorAll('*')).find(el => 
  el.textContent.trim() === '流量分析' && el.offsetParent !== null && el.children.length === 0
)

// ❌ 错误：会匹配到 HTML/BODY 父容器，返回 undefined
Array.from(document.querySelectorAll('*')).find(el => 
  el.textContent.trim() === '流量分析' && el.offsetParent !== null
)
```
**备用方案**：直接用 semi-tabs-tab 类名定位：`document.querySelector('div.semi-tabs-tab:nth-of-type(2)').click()`

| 指标 | 说明 | 判断标准 |
|------|------|----------|
| **推荐页流量占比** | 算法推了多少流量 | >80%说明算法在推 |
| **平均播放时长** | 用户平均看多久 | 越长越好，但要看视频总时长 |
| **5秒完播率** | 看了5秒的人占比 | >50%说明开头抓人 |
| **平均播放占比** | 平均看了视频的百分之几 | >30%算合格 |

### ⚠️ 留存分析曲线图（血的教训）

**留存分析曲线图可以帮你定位文案在第几秒出问题。**

**如何获取留存分析数据**：
1. 在视频详情页，点击"留存分析" tab
2. 截图留存分析曲线图
3. 用analyze-image skill分析曲线图，定位问题时间点

```bash
# Step 1：点击"留存分析" tab
opencli browser douyin eval "
(function(){
  var btn = Array.from(document.querySelectorAll('*')).find(function(el) { 
    return el.textContent.trim() === '留存分析' && el.offsetParent !== null; 
  });
  if(btn) { btn.click(); return 'clicked'; }
  return 'not found';
})()
"
sleep 5

# Step 2：截图留存分析曲线图
opencli browser douyin screenshot "D:/hermes-agent/retention_analysis.png"

# Step 3：用analyze-image分析曲线图
UV_PYTHON="E:\\Users\\Administrator\\AppData\\Roaming\\uv\\python\\cpython-3.11-windows-x86_64-none\\python.exe"
"$UV_PYTHON" "E:/Users/Administrator/AppData/Local/hermes/skills/analyze-image/scripts/analyze_image.py" "D:/hermes-agent/retention_analysis.png" "请分析这张抖音留存分析曲线图。告诉我：1）曲线的整体趋势 2）在第几秒开始下降 3）下降最陡的是哪几秒 4）有什么异常点（低谷）5）对应到视频文案可能是哪几秒出了问题"
```

**留存分析曲线图的关键指标**：

| 指标 | 说明 | 判断标准 |
|------|------|----------|
| **5秒完播率** | 前5秒留住多少人 | >50%说明开头抓人 |
| **低谷点** | 曲线明显下降的位置 | 对应文案的哪个时间点 |
| **曲线斜率** | 下降的速度 | 越陡说明流失越快 |

**如何定位文案问题**：
1. 找到曲线的低谷点（下降最陡的位置）
2. 计算低谷点对应的时间（秒）
3. 对照文案，看那个时间点在讲什么
4. 分析为什么那个时间点观众流失

**案例**：
- 低谷1在13-15秒 → 对应文案"你忍咗"那段 → 可能节奏拖了
- 低谷2在35秒 → 对应文案"我睇报纸睇一眼"附近 → 可能内容重复

**⚠️ 每次查看数据时，如果视频有留存分析数据，都要截图并分析。** 这是优化文案的关键依据。

### 流量来源解读

| 来源 | 含义 | 健康占比 |
|------|------|----------|
| 推荐页 | 算法推送 | >70%（越高说明算法越推） |
| 个人主页 | 主动点进来看 | 5-15% |
| 朋友页 | 朋友分享 | 3-10% |
| 搜索 | 用户搜索来的 | 2-5% |

### 播放量卡在1000-2000区间的诊断

账号所有视频播放都在1500-2000区间 = 卡在初级池（1000-5000）出不去。

典型表现：
- ✅ 5秒完播率>50%（开头抓人）
- ✅ 2秒跳出率<30%（开头合格）
- ❌ 总完播率<10%（中间大量流失）
- ❌ 点赞率<1%（缺乏情绪共鸣）
- ❌ 评论率<0.3%（零互动）
- ❌ 分享率<0.1%（无传播力）

算法信号：开头还行→但没人看完→没人互动→不值得推给更多人

突破方向（按优先级）：
1. 提高完播率（缩短时长+中间加钩子）
2. 提高收藏率（加干货/知识元素，2025年权重最高）
3. 提高互动率（争议结尾+小号互动触发二次推流）

### 典型问题诊断

**案例：1分42秒视频，平均播放8秒**
- 问题：用户只看了8秒就划走
- 原因：开头没钩住人，前8秒就流失
- 解决：优化开头3秒，加更强的钩子

**案例：推荐页90%但播放量只有67**
- 问题：算法推了但没人看
- 原因：内容没接住流量，完播率太低
- 解决：提高完播率，让算法继续推

## 问题诊断

| 数据表现 | 问题 | 改进方向 |
|----------|------|---------|
| 完播率<10% | 视频太长或中间拖沓 | 砍到1分半以内，每15秒一个留人点 |
| 2秒跳出率>30% | 开头不够抓人 | 用爆款标题库模式，3秒内给钩子 |
| 5秒完播率>50%但总完播率<10% | **开头OK但中间留不住人** | 15-20秒处必须有一个新的钩子（反转/金句/悬念），防止观众看完开头就走 |
| 完播率>5%但5秒完播率<50% | **内容好但开头钩子不够** | 内容不动，只优化前5秒的钩子（视频6验证：完播率6.60%全号最高，但5s完播率44.48%，"5秒→看完"转化率是视频5的4倍） |
| 点赞率<1% | 内容没有共鸣 | 加金句、加情绪点 |
| 评论率<0.3% | 没有互动引导 | 视频结尾抛问题，引导评论 |
| 播放量停在500以下 | 没过第一轮推荐 | 优化开头+封面 |
| **播放量远低于同期其他视频** | **选题与账号定位不匹配** | **选题必须与账号定位强相关（如粤语栋笃笑就选粤语吐槽类话题），避免泛热度话题** |
| **播放量低于预期但时长已优化** | **发布时间不在流量高峰** | **必须在晚上7-10点发布，下午时段（14-17点）发布效果差** |
| **点赞率正常但评论/分享极低** | **内容缺乏互动钩子和传播点** | **结尾抛争议性问题，内容加入可分享的观点金句** |
| **分享量高但点赞率极低（<0.5%）** | **内容有传播力但缺乏情绪共鸣** | **分享来自话题热度而非内容共鸣，需要加强金句密度和情绪爆发点（愤怒/好笑/认同感），让观众想点赞而不只是转发** |
| 播放量大幅增加但完播率下降 | **推荐给了更多非核心用户** | **算法在放量但内容留不住新用户，需要加强中间内容的吸引力** |
| 播放量暴涨但点赞率/评论率暴跌 | **互动率被推荐放量稀释（正常现象）** | **6h时互动率高是因为早期观众精准，24h放量后互动率被稀释是正常的。不要误判为内容变差。看绝对值（点赞数、评论数）而非比率** |
### 2s跳出率>40%但5秒完播率≥50%** | **标题/封面不吸引人，但内容钩子OK** | **开头文案的钩子没问题（5s完播率过半），但标题/封面不够抓眼球导致2秒跳出率极高。优化标题悬念感（对比：视频6「金价暴跌不是经济问题，你被骗了」vs 视频7「其实一点都不系」，前者有悬念后者太平淡）** |

**⚠️ 2s跳出率和5s完播率是独立指标（2026-06-14纠正）：** 不要把两者混淆。2s跳出率=2秒内离开的比例（如16.24%），5s完播率=看到5秒的比例（如42.68%）。两者是独立的，不能用一个推导另一个。例如：2s跳出率16.24%说明前2秒OK，5s完播率42.68%说明前5秒留住了42.68%的人。如果2s跳出率低但5s完播率也低，说明问题在2-5秒之间；如果两者都OK但完播率低，说明问题在5秒之后。
| **推荐页占比<60%且朋友页>30%** | **算法不推，流量靠朋友分享** | **内容在小圈子传播但没有被算法放大。可能是话题不够热、标题不够吸引、或账号权重不够。需要更强的标题钩子和更好的发布时间** |
| **推荐页>90%但播放量<500** | **算法推了但内容完全接不住** | **内容与账号定位严重偏离（如游戏账号发游戏内容），算法推荐给了非核心用户，完播率和互动率极低导致快速停止推流。必须回归账号定位选题** |

### ⚠️ 关键洞察（2026-06-06验证）
**完播率低不是时长问题，是中间节奏问题：**
- 视频1（2:43）完播率1.7%，视频4（1:39）完播率3.5%，视频5（1:52）完播率0.93%
- 即使控制在1:30-2:00，完播率仍然<5%
- 5秒完播率54-58%说明开头没问题
- 真正的问题：15-20秒处没有第二个钩子，观众看完开头就走
- **改进方向**：每30秒一个留人点（反转/金句/悬念/新信息），而不是简单砍时长

### 案例：视频4（公司跑路）2026-06-05 至 2026-06-06
**2h首次检查（06-05 23:30）**：
- 1:39视频，完播率4.75%，但5秒完播率54.00%
- 2秒跳出率17.14%（合格），平均播放21秒（总长1:39）
- **诊断**：开头抓人（5秒完播率过半），但中间没钩子，观众看完开头就走了
- **教训**：文案不能只靠开头撑，15-20秒处必须有第二个钩子（反转/金句/新信息）
- **流量来源**：推荐页99.4%，算法在推但内容留不住人
- **关键指标对比**：2秒跳出率17.14%（✅）vs 视频1的22.27%，开头明显更好

**15h检查（06-06 11:08）**：
- 播放量：400→1900（+375%），点赞：2→10，评论：0→1，分享：0→1
- 完播率：4.75%→3.51%（↓），但5秒完播率：54%→56.34%（↑）
- 平均播放时长：21秒→33秒，播放占比：21.56%→32.91%
- 点赞率：0.50%→0.53%，评论率：0%→0.05%，分享率：0%→0.05%
- 流量来源：推荐页99.5%（+5.7%）
- **诊断**：
  1. ✅ 开头更抓人了（5秒完播率提升2.3%）
  2. ⚠️ 中间流失更严重（总完播率下降1.2%，但播放量增加4.75倍）
  3. ❌ 互动指标极低（点赞率0.53%、评论率0.05%、分享率0.05%）
- **核心发现**：视频4是目前表现最好的视频，超过视频1（1380）和视频2（1708），且还在增长中
- **关键问题**：56%的人能看5秒，但只有3.5%看完全部，中间流失严重
- **24h预计**：按当前趋势，24h预计播放量2500-3000
- **改进方向**：15-20秒处必须有第二个钩子，结尾加互动引导，考虑缩短到1分钟以内

**24h最终检查（06-06 23:00，列表数据）**：
- 播放量：1934，点赞11，评论1，分享1
- ⚠️ 详情页无法访问（跨域iframe限制），完播率等详细数据缺失
- 增长趋势：400→1900→1934，增长已放缓（最后11小时仅+34）
- 结论：视频4已接近流量尾声，最终播放量约1934-2000
- 总结：视频4是目前表现最好的视频（🥇），超过视频2（1723）和视频1（1416）

### 案例：视频5（已读）2026-06-06 6h首次检查
**6h检查（06-06 23:00）**：
- 1:52视频，完播率0.93%（极低），但5秒完播率58.06%（优秀）
- 2秒跳出率27.42%（合格），平均播放13秒（总长1:52）
- 点赞率3.62%（优秀），评论率2.17%（优秀），分享率0.72%（合格）
- 涨粉+4
- 流量来源：推荐页66.4%，其他17.8%，个人主页8.4%，朋友页5.6%，搜索1.9%
- **诊断**：
  1. ✅ 开头抓人（5秒完播率58%，2秒跳出率27%）
  2. ❌ 中间严重流失（58%→0.93%），1:52的视频平均只看13秒
  3. ✅ 互动指标优秀（点赞率3.62%，评论率2.17%），说明内容有共鸣
  4. ⚠️ 推荐页占比偏低（66.4%），算法推荐力度不够
- **核心问题**：典型"开头OK但中间留不住人"，与视频4完全相同的模式
- **关键发现**：1:39和1:52的视频完播率都<5%，说明**即使控制在2分钟以内，完播率仍然很低**。问题不是时长，是中间节奏
- **与视频4对比**：视频4（公司跑路）5秒完播率56%但播放量1934，视频5（已读）5秒完播率58%但播放量仅138——视频5还在增长早期，最终播放量待观察
- **改进方向**：15-20秒处必须有第二个钩子，每30秒一个留人点

**24h最终检查（06-07 10:20）**：
- 播放量：138→1766（+1179%，爆发式增长🚀）
- 点赞量：5→14，评论量：3→3，分享量：1→2，收藏量：0→1
- 完播率：0.93%→2.28%（↑），5秒完播率：58.06%→58.88%（稳定）
- 2秒跳出率：27.42%→18.00%（↓，显著改善！）
- 平均播放时长：13秒→23秒，播放占比：11.91%→20.75%
- 点赞率：3.62%→0.79%（↓，被稀释），评论率：2.17%→0.17%（↓）
- 推荐页：66.4%→96.8%（算法全力推荐）
- **⚠️ 新模式发现：互动率被推荐放量稀释**
  - 6h时只有138播放，观众都是早期粉丝/精准用户，互动率自然高（点赞率3.62%）
  - 24h时播放1766，大量推荐流量涌入，互动率被稀释（点赞率0.79%）
  - 这是正常现象，不是内容变差了
- **结论**：视频5是目前互动表现最好的视频（点赞14、评论3），仅次于视频4的播放量

### 案例：视频7（A股暴跌）2026-06-08 6h首次检查
**6h检查（06-08 23:00）**：
- 1:31视频，完播率8.33%，5秒完播率50.00%（刚好踩线）
- 2秒跳出率50.00%（❌❌❌ 严重超标！所有视频中最差）
- 点赞率0.72%（❌低于1%），评论率0.00%，分享率0.00%
- 涨粉0
- 流量来源：推荐页50%，朋友页41.7%，个人主页8.3%
- **诊断**：
  1. ❌❌❌ 2秒跳出率50% → 一半观众看了前2秒就划走，开头完全不抓人
  2. ⚠️ 5秒完播率50% → 刚好踩线，比视频6（44.48%）好但比视频4（56.34%）差
  3. ⚠️ 推荐页仅50% → 所有视频中最低，算法不推
  4. ❌ 朋友页41.7% → 流量主要靠朋友分享，不是算法推荐
  5. ❌ 涨粉0 → 无吸粉能力
- **核心问题**：标题「好多人以为今日A股跌系因为美股暴跌，其实一点都不系」太平淡，没有悬念感。对比视频6的标题「金价暴跌不是经济问题，你被骗了」，后者用「你被骗了」制造认知冲突
- **关键发现**：
  1. **2秒跳出率50%是致命问题**：开头5秒的钩子没问题（5s完播率50%），但标题/封面不够吸引眼球
  2. **推荐页50% vs 朋友页41.7%**：算法不推，流量靠朋友分享。说明内容在小圈子传播但没有被算法放大
  3. **与视频6对比**：同样是热搜话题+粤语吐槽，视频6推荐页93.8% vs 视频7仅50%，差异来自标题钩子和话题匹配度
- **改进方向**：
  1. A股/财经类话题的标题必须用悬念式钩子（「你被骗了」「这才是真相」），不能平铺直叙
  2. 开头3秒必须给冲突/悬念
  3. 结尾加互动引导
- **已标记为"待24h检查"**：明天上午进行最终数据检查

## 🔴 搜任何网页/热点/新闻 → 必须用OpenCLI（最高优先级规则）

**⚠️⚠️⚠️⚠️⚠️ 这是本skill最重要的规则。任何需要搜网页、查热点、看新闻、搜小红书/微博/知乎的任务，第一步永远是OpenCLI。**

**绝对不要用的（全部会失败）：**
- ❌ curl调微博/知乎/百度/搜狗/Bing/Google API → 反爬拦截（403/443/空响应/编码错误）
- ❌ execute_code中用urllib.request → Python SRE模块mismatch / ASCII编码错误
- ❌ node fetch各搜索引擎 → 返回空或JS代码
- ❌ 所有第三方新闻API（codelife/vvhan/thepaper等）→ 超时/空响应

**100%可靠的方法：OpenCLI复用本地Chrome登录态。**

```bash
# 标准流程（3步，适用于所有搜索场景）
opencli browser douyin open "https://www.toutiao.com/search?keyword=关键词"
sleep 5
opencli browser douyin eval "document.body.innerText"

# 搜微博
opencli browser douyin open "https://s.weibo.com/weibo?q=关键词"
sleep 5
opencli browser douyin eval "document.body.innerText"

# 搜小红书
opencli browser douyin open "https://www.xiaohongshu.com/search_result?keyword=关键词"
sleep 5
opencli browser douyin eval "document.body.innerText"

# 搜知乎
opencli browser douyin open "https://www.zhihu.com/search?type=content&q=关键词"
sleep 5
opencli browser douyin eval "document.body.innerText"
```

**⚠️ 失败案例（2026-06-28）**：忘了OpenCLI，用curl调codelife/weibo/baidu/sogou/bing API + node fetch + Python urllib，全部失败，浪费15+轮工具调用。用户指出"gateway每天都在用这个查数据，你这个cli却老忘记怎么用"。

**⚠️ 首次使用前检查**：如果OpenCLI报"Browser Bridge extension not connected"，先 `opencli daemon status` 确认连接状态。Chrome必须在运行。

**⚠️ 搜什么平台用什么URL**：

| 平台 | URL模板 | 说明 |
|------|---------|------|
| 今日头条 | `https://www.toutiao.com/search?keyword=XXX` | 最常用，热榜+搜索 |
| 微博 | `https://s.weibo.com/weibo?q=XXX` | 微博搜索 |
| 小红书 | `https://www.xiaohongshu.com/search_result?keyword=XXX` | 需登录 |
| 知乎 | `https://www.zhihu.com/search?type=content&q=XXX` | 知乎搜索 |
| 百度 | `https://www.baidu.com/s?wd=XXX` | 百度搜索 |

## 用OpenCLI搜索热点新闻（通用方法）

**适用场景**：搜微博热搜、头条热点、抖音热搜等中文平台内容。

**最佳方法：用头条搜索页 + eval提取文本**
```bash
# 搜索关键词
opencli browser douyin open "https://www.toutiao.com/search?keyword=关键词"
sleep 5
opencli browser douyin eval "document.body.innerText"
```

**⚠️ 不要用curl/API抓中文新闻站**：微博、知乎、百度等都有反爬机制，curl返回空或403。OpenCLI复用Chrome登录态，是最可靠的方法。

**⚠️ 操作节奏：每次操作之间加 `sleep 5-8`，模拟人操作。不要连续快速调用。**

**⚠️ 搜索多个关键词时**：每次搜索之间 `sleep 8`，避免触发风控。

**搜索顺序**：先 `open` 打开搜索页 → `sleep 5` → `eval "document.body.innerText"` 提取内容。

## ⚠️ OpenCLI Chrome扩展断连修复（2026-06-28验证）

**症状**：`opencli browser douyin open` 超时或返回"Browser Bridge extension not connected"

**快速修复流程（2026-07-04验证）**：
```bash
# 1. 先用 state 检查（最快，<2秒）
opencli browser douyin state
# 如果返回 URL 和 viewport，说明连接正常，跳到步骤3

# 2. 如果 state 失败，重启 daemon（可能超时，没关系）
opencli daemon restart
sleep 5

# 3. 直接尝试 open，不要等 daemon status 显示 connected
opencli browser douyin open "https://creator.douyin.com/creator-micro/data-center/content"
sleep 8

# 4. 提取数据
opencli browser douyin eval "document.body.innerText"
```

**⚠️ 关键发现（2026-07-04）**：`daemon status` 和 `daemon restart` 都可能超时（10-15秒无响应），但 `opencli browser douyin state` 通常能在2秒内返回。如果 `state` 能返回 URL 和 viewport，说明 OpenCLI 连接正常，直接用 `open` 和 `eval` 即可。不要因为 `daemon status` 超时就以为连接断了——`state` 才是最快的诊断方式。

**如果 open 确实超时/失败**，再检查 Chrome 是否运行：
```bash
tasklist | grep -i chrome
# 如果没运行，启动Chrome（见上方"启动 Chrome 的正确命令"）
# 如果在运行，尝试打开 chrome://extensions/ 刷新Browser Bridge扩展
```

**⚠️ 注意**：`opencli doctor` 经常挂起30秒+，用 `opencli daemon status` 代替（<2秒返回）。

## OpenCLI 常用命令速查

```bash
# 打开页面（前台模式，可能超时）
opencli browser douyin open "<URL>"

# 截图
opencli browser douyin screenshot "<保存路径>"

# 查看页面状态
opencli browser douyin state

# 点击元素（用[N]编号）
opencli browser douyin click "[N]"

# 查找DOM元素（⚠️ 必须用 --text/--css 等flag，不能用位置参数）
opencli browser douyin find --text "要找的文本"
opencli browser douyin find --css "div.semi-tabs-tab"
opencli browser douyin find --role button --name "按钮文本"

# 关闭浏览器
opencli browser douyin close
```

**⚠️ `find` 命令语法（2026-06-10验证）**：`find` 必须用 `--text`/`--css`/`--role` 等flag，不能用位置参数。
```bash
# ✅ 正确
opencli browser douyin find --text "内容管理"
opencli browser douyin find --css "div[class*=video-card]"

# ❌ 错误（会报 "too many arguments"）
opencli browser douyin find "text=内容管理"
opencli browser douyin find "内容管理"
```

**⚠️ `--background` 标志不存在（v1.8.1已验证）**：`opencli browser douyin open` 不支持 `--background`，会报 `error: unknown option '--background'`。如果前台超时，直接用前台模式即可（通常都能在30秒内完成）。

**⚠️ Cron Job 环境：Chrome 未运行时的启动方法**

**作为定时任务（cron job）运行时，Chrome 默认未启动。** 必须先启动 Chrome，等待 Browser Bridge 扩展连接后才能使用 OpenCLI。

### Camofox浏览器启动（2026-06-14验证）

当OpenCLI超时或Camofox未运行时，按以下步骤启动：

```bash
# 1. 检查Camofox是否运行
curl -s http://localhost:9377/health 2>/dev/null

# 2. 如果未运行，后台启动
cd D:/hermes-agent/camofox-browser && node server.js
# 用terminal的background=true启动

# 3. 等待就绪（browserRunning必须为true）
for i in 1 2 3 4 5 6 7 8 9 10; do
  sleep 3
  result=$(curl -s http://localhost:9377/health 2>/dev/null)
  if echo "$result" | grep -q '"browserRunning":true'; then
    echo "Browser ready!"
    break
  fi
done

# 4. 验证连接后使用browser工具
```

**⚠️ 关键**：health返回`{"ok":true}`但`"browserRunning":false`时，浏览器还在初始化，不能调用browser_navigate，会超时。必须等`"browserRunning":true`。

### 启动 Chrome 的正确命令

```bash
# Step 1：后台启动 Chrome（使用已有用户数据目录，保持登录态）
# 注意：必须用 background=true，因为 Chrome 是长驻进程
terminal(command='"/c/Program Files/Google/Chrome/Application/chrome.exe" --profile-directory="Default" --restore-last-session', background=true, notify_on_complete=false)

# Step 2：等待 Chrome 完全启动和 Browser Bridge 连接（约 10-15 秒）
sleep 12

# Step 3：验证连接状态
opencli daemon status  # ⚡ 比 opencli doctor 快得多（<2s vs 可能超时30s+）
# 应显示：Extension: connected
# ⚠️ opencli doctor 经常挂起/超时（30s+无响应），用 daemon status 代替
# daemon status 返回：Daemon: running, Extension: connected, Port: XXXXX

# Step 4：验证 Chrome 在运行
tasklist | grep -i chrome
```

### 关键注意事项

1. **必须用 `--profile-directory="Default"`**：使用默认用户配置，保持抖音登录态
2. **必须用 `--restore-last-session`**：恢复上次会话，避免打开空白页
3. **等待时间很重要**：Chrome 启动后需要 10-15 秒让 Browser Bridge 扩展完全连接
4. **用 `notify_on_complete=false`**：Chrome 是长驻进程，不会自动退出，不需要完成通知
5. **验证步骤不能省**：启动后必须用 `opencli doctor` 确认连接成功

### 如果 Browser Bridge 未连接
### ⚠️ 如果 Browser Bridge 未连接
```bash
# 检查 Chrome 是否在运行
tasklist | grep -i chrome

# 如果 Chrome 在运行但扩展未连接，重启 daemon
opencli daemon restart
sleep 5
opencli daemon status  # ⚡ 用 daemon status 而非 doctor

# 如果仍未连接，可能需要重新加载扩展（见上方"扩展完全未安装时的手动安装"）
```

### ⚠️ CDP 直连备选方案（2026-07-03验证）

当 OpenCLI 完全无法连接时，可以用 Hermes 的 `browser_cdp` 工具直接操作 Chrome：

```bash
# 1. 启动Chrome带remote debugging port（⚠️ 不要指定--user-data-dir，保留登录态）
"/c/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --no-first-run --restore-last-session &ugging port（⚠️ 不要指定--user-data-dir，保留登录态）
"/c/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --no-first-run --restore-last-session &
sleep 12

# 2. 验证CDP端口
curl -s http://localhost:9222/json/version

# 3. 设置Hermes browser config
hermes config set browser.cdp_url "ws://127.0.0.1:9222"

# 4. 用browser_cdp导航和提取数据
# browser_cdp(method="Page.navigate", params={"url": "..."}, target_id="...")
# browser_cdp(method="Runtime.evaluate", params={"expression": "document.body.innerText", "returnByValue": true}, target_id="...")
```

**⚠️ CDP的限制**：如果指定了错误的`--user-data-dir`路径，会创建没有登录态的Chrome。解决：不要指定`--user-data-dir`，让Chrome自动用默认目录。

**⚠️ 默认user-data-dir的lockfile问题**：如果Chrome已经用默认profile运行，`--remote-debugging-port=9222` 会被lockfile阻止。必须用独立 `--user-data-dir`。

### 完整的 Cron Job 启动流程

```bash
# 1. 检查 Chrome 是否已在运行
if ! tasklist 2>/dev/null | grep -qi chrome; then
  echo "Chrome not running, starting..."
  # 后台启动 Chrome（使用 terminal background=true）
  sleep 12
fi

# 2. 用 state 检查 OpenCLI 连接（⚡ 最快，<2秒）
opencli browser douyin state
# 如果返回 URL 和 viewport，直接跳到步骤3
# 如果 state 失败，尝试 daemon restart（可能超时）
# opencli daemon restart && sleep 5

# 3. 打开抖音创作者中心
opencli browser douyin open "https://creator.douyin.com/creator-micro/data-center/content"
sleep 8

# 4. 提取数据
opencli browser douyin eval "document.body.innerText"
```

### ⚠️ 扩展完全未安装时的手动安装（2026-06-10验证）

如果Chrome中没有安装Browser Bridge扩展（`opencli doctor`显示`[MISSING] Extension: not connected`），需要手动下载并加载：

```bash
# Step 1: 下载最新扩展zip
cd /tmp
LATEST_URL=$(curl -sL "https://api.github.com/repos/jackwener/opencli/releases/latest" | grep -o '"browser_download_url": "[^"]*"' | grep -o 'https://[^"]*')
curl -sL "$LATEST_URL" -o opencli-extension.zip

# Step 2: 解压
unzip -o opencli-extension.zip -d opencli-extension

# Step 3: 杀掉已有Chrome进程（重要！否则--load-extension不生效）
taskkill /F /IM chrome.exe 2>/dev/null; sleep 2

# Step 4: 启动Chrome并加载扩展（用background模式）
opencli browser douyin open "https://creator.douyin.com/creator-micro/home"
# 或者如果daemon已连接但没有Chrome：
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --load-extension="/tmp/opencli-extension" \
  --no-first-run \
  --no-default-browser-check \
  --user-data-dir="/e/Users/Administrator/AppData/Local/Google/Chrome/User Data" \
  "https://creator.douyin.com/creator-micro/home" &

# Step 5: 等待扩展连接
sleep 8
opencli doctor
# 应显示 [OK] Extension: connected
```

**⚠️ 关键注意事项**：
- 必须先杀掉所有Chrome进程，再用`--load-extension`启动，否则扩展不会加载
- `--user-data-dir`指向现有Chrome用户数据目录，保持登录态
- 扩展zip从GitHub releases下载：`https://github.com/jackwener/OpenCLI/releases`
- daemon需要在扩展连接前已运行（`opencli daemon restart`）

## 导航到视频列表页

**⚠️⚠️⚠️ 最重要的坑：不要用"近期作品"tab！它只显示最近7天的视频！**

**查全部视频 → 侧边栏 内容管理 → 作品管理（唯一正确路径）**

### ⚡ 正确方法：侧边栏导航到作品管理（推荐，显示全部视频）

```bash
# Step 1：打开内容管理页
opencli browser douyin open "https://creator.douyin.com/creator-micro/content-manage/video"
sleep 8

# Step 2：点击侧边栏"内容管理"展开子菜单
opencli browser douyin find --text "内容管理"
opencli browser douyin click <ref>
sleep 2

# Step 3：点击"作品管理"进入完整视频列表（⚠️ 这里才有全部视频！）
opencli browser douyin find --text "作品管理"
opencli browser douyin click <ref>
sleep 3

# Step 4：提取所有视频数据（显示"共 N 个作品"）
opencli browser douyin eval "document.body.innerText"
```

**⚠️ 坑：content-manage/video URL 默认进入"近期作品"视图，只显示最近7天的视频！**
**⚠️ 坑：点击"近期作品" tab 也只显示最近7天！用户问旧视频时必须用"作品管理"！**
**✅ 作品管理页会显示"共 N 个作品"，包含所有视频。**

### 方法2：仪表盘快速查看（仅限最新视频）

如果只需要最新视频的详细数据，直接在仪表盘点击"查看分析"即可：
```bash
opencli browser douyin open "https://creator.douyin.com/creator-micro/home"
sleep 8
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '查看分析' && el.offsetParent !== null).click()"
sleep 5
```

**⚠️ 仪表盘只显示最新一条视频，无法看到所有视频。**

## 提取页面数据（Eval命令）— 唯一可靠方法

**⚠️⚠️⚠️ 唯一可靠方法：用 `document.body.innerText` 一次性提取所有视频数据。** 不要尝试从DOM属性获取视频ID——但可以通过React Fiber tree提取（见上方"从列表页提取视频ID"章节）。

```bash
# 唯一可靠方法：提取全部文本
opencli browser douyin eval "document.body.innerText"
```

返回的文本包含每个视频的完整数据行，可直接解析。示例输出结构：
```
#老宅被亲戚偷装光伏板女子崩溃痛哭 ...
编辑作品 / 设置权限 / 作品置置顶 / 删除作品
2026年06月03日 17:16 / 已发布
播放 1605 / 平均播放时长 25秒 / 封面点击率 0%
点赞 9 / 评论 2 / 分享 0 / 收藏 0 / 弹幕 0
```

**⚠️ vision_analyze已不可用（2026-06-22确认）**：mimo-v2.5的Xiaomi API拒绝tool message中的图片格式（报`400: Param Incorrect: text is not set`）。这是服务端breaking change，不是临时故障。**绝对不要用截图+vision_analyze方案**，直接用eval提取文本。

```bash
# ✅ 唯一可靠方法：eval提取文本
opencli browser douyin eval "document.body.innerText"

# ❌ 不要这样做（会报400错误）：
# opencli browser douyin screenshot "xxx.png"
# vision_analyze(image_url="xxx.png", question="...")
```

```bash
# 在内容管理页点击最新视频的"查看分析"
opencli browser douyin eval "Array.from(document.querySelectorAll('*')).filter(el => el.textContent.trim() === '查看分析' && el.offsetParent !== null)[0].click()"
sleep 5
opencli browser douyin eval "document.body.innerText"
```

**⚠️ 详情页内容在跨域iframe中**：iframe URL为 `https://www.douyin.com/creatorvideo/{id}`，无法通过父页面eval直接访问iframe内部DOM。但通过"查看分析"按钮跳转后，eval提取的是当前页面的`document.body.innerText`，可以获取数据。

## 从列表页提取视频ID（React Fiber方法）

**重要更新**：视频ID可以通过React Fiber tree提取！之前的结论"列表页无法获取视频ID"是错误的。

```bash
# Step 1: 找到视频卡片的React Fiber
opencli browser douyin eval "
var cards = document.querySelectorAll('[class*=\"video-card-z\"]');
var card = cards[0];
var fiberKey = Object.keys(card).find(k => k.startsWith('__reactFiber'));
var fiber = card[fiberKey];
// 向上遍历到depth 1找data prop
var current = fiber.return;
if (current && current.memoizedProps && current.memoizedProps.data) {
  var data = current.memoizedProps.data;
  JSON.stringify({awemeId: data.aweme_id, caption: data.caption ? data.caption.substring(0, 50) : null});
}
"
```

**提取所有视频ID**：
```bash
opencli browser douyin eval "
var cards = document.querySelectorAll('[class*=\"video-card-z\"]');
var results = [];
cards.forEach(card => {
  var fiberKey = Object.keys(card).find(k => k.startsWith('__reactFiber'));
  var fiber = card[fiberKey];
  var current = fiber.return;
  if (current && current.memoizedProps && current.memoizedProps.data) {
    var data = current.memoizedProps.data;
    if (data.aweme_id) {
      results.push({awemeId: data.aweme_id, caption: data.caption ? data.caption.substring(0, 60) : ''});
    }
  }
});
JSON.stringify(results);
"
```

### 视频详情页导航（有iframe限制）

详情页会加载在跨域iframe中，无法直接eval提取内容：
- 父页面URL: `https://creator.douyin.com/creator-micro/home`（仪表盘）或 `/content-manage/video`（内容管理页）
- iframe URL: `https://www.douyin.com/creatorvideo/{id}?is_myself=1` (跨域，无法访问)

**✅ 正确方法**：在仪表盘（`/home`）点击"查看分析"按钮，会跳转到详情页。详情页虽然在iframe中，但可以通过eval提取`document.body.innerText`获取数据。

**✅ 已验证可用的方法**：
- 在内容管理页（`/content-manage/video`）点击"查看分析"按钮（2026-06-09验证可用）
- 在仪表盘（`/home`）点击"查看分析"按钮（仅限最新视频）

**❌ 不可用的方法**：
- 通过React的`onPreview` prop触发预览（面板在iframe中，无法eval访问）

## OpenCLI超时问题

**`opencli browser douyin open` 命令在前台模式下可能超时（30秒限制）**。但 `--background` 标志不存在（v1.8.1已验证），直接用前台模式即可——实测页面加载通常在10秒内完成，很少超时。如果真的超时，重新执行一次即可。

**正确的内容管理页面URL**：
```bash
# ⚠️ content-manage/video 会重定向到 home！（2026-06-15验证）
# opencli browser douyin open "https://creator.douyin.com/creator-micro/content-manage/video"
# → 实际URL变成 https://creator.douyin.com/creator-micro/home

# ✅ 最佳方法：通过数据中心→作品分析→投稿列表（方法0）
opencli browser douyin open "https://creator.douyin.com/creator-micro/data-center/operation"

# ✅ 备选：直接导航到数据中心内容分析页
opencli browser douyin open "https://creator.douyin.com/creator-micro/data-center/content"
```

### ⚠️ `opencli doctor` 经常挂起/超时（2026-06-25验证）

**`opencli doctor` 命令可能挂起30秒以上无响应。** 替代方案：

```bash
# ❌ opencli doctor 经常超时
opencli doctor  # 可能挂起30s+

# ✅ 用 opencli daemon status 代替（<2秒返回）
opencli daemon status
# 返回：Daemon: running, Extension: connected, Port: XXXXX
```

**`daemon status` 返回的信息等价于 `doctor`**（都显示连接状态），但速度快10倍以上。在cron job中优先使用 `daemon status`。

**`opencli doctor` 命令可能挂起30秒以上无响应。** 替代方案：

```bash
# ❌ opencli doctor 经常超时
opencli doctor  # 可能挂起30s+

# ✅ 用 opencli daemon status 代替（<2秒返回）
opencli daemon status
# 返回：Daemon: running, Extension: connected, Port: XXXXX
```

**`daemon status` 返回的信息等价于 `doctor`**（都显示连接状态），但速度快10倍以上。在cron job中优先使用 `daemon status`。

### ⚠️ ⚠️ ⚠️ 每次查看数据前必须做的事（血的教训）

**第零步：先读发展日志（references/发展日志.md）！**

发展日志记录了所有视频的完整数据（包括已停止增长的老视频）。用户问"某个视频"或"看看数据"时，**先从发展日志找到对应视频的信息**，再去创作者中心查实时数据。不要一上来就打开浏览器瞎找。

**第一步：优先用方法0（数据中心→作品分析→投稿列表）！**

方法0一次eval就能获取所有视频的所有指标（完播率、5s完播率、2s跳出率等），是最高效的方式。只有当方法0失败时，才回退到方法A（内容管理页）。

**为什么必须先读发展日志：**
1. 创作者中心"近期作品"tab **只显示最近7天的视频**，更早的视频看不到
2. 发展日志有所有12+个视频的完整记录，包括已停止增长的老视频
3. 用户说"还有一个旧视频快破2000"——如果你先读了发展日志，就能直接定位到是哪个视频（比如视频4「公司跑路」1953播放），而不是在创作者中心翻来翻去找只有5个视频的列表
4. 发展日志还有视频的表现排名、诊断结论、历史数据对比，这些创作者中心看不到

**正确流程：**
1. `skill_view(name='douyin-data-check', file_path='references/发展日志.md')` → 读取所有视频记录
2. 根据用户描述定位到具体视频（标题/播放量/日期）
3. 如果需要实时数据，再去创作者中心用OpenCLI查
4. 对比发展日志记录值和实时值，判断是否还在增长

**⚠️ 发展日志有两个副本（2026-06-12验证）**：
- **技能目录版本**（`E:/Users/Administrator/AppData/Local/hermes/skills/content/douyin-data-check/references/发展日志.md`）→ **这是权威版本**，skill_view读取的就是这个
- **工作目录版本**（`./references/发展日志.md`）→ 可能是旧版本，数据不完整
- **规则**：必须用 `skill_view` 读取发展日志，不要用 `read_file` 读取本地副本。两个文件会不同步，本地副本可能缺少最新的视频数据（如视频10-13）

**⚠️ 数据异常监控（2026-07-16新增）**：
- **点赞减少**：如果页面显示的点赞数比发展日志少（如V26从7→6），可能是用户取消点赞或数据波动。记录变化但不修改历史数据
- **播放量停滞**：如果连续2次定时更新播放量无变化，标记视频为"已停止增长"
- **私密状态视频**：如V28"仅自己可见"，其推荐页/搜索占比数据可能受私密状态影响，诊断时需注明

**第一步永远是：cronjob list 检查今天是否已经有定时任务跑过！**

如果抖音数据定时任务（抖音数据-上午/抖音数据-晚上）今天已经跑过且状态ok，直接告诉用户"已经跑过了，数据如下"，不要重复执行。

**⚠️ 当前session就是cron job时，跳过此步骤**：如果你自己就是正在执行的定时任务（prompt中注明"You are running as a scheduled cron job"），不需要检查cronjob list——你就是那个任务。直接开始数据采集流程。

**绝对不要跳过这一步直接去拿数据。** 用户会生气："你应该去看看定时任务有没有成功，谁让你直接就去拿来。"

**⚠️⚠️⚠️ 查看定时任务结果的正确方式（2026-06-06教训）**

**当用户说"看看刚刚跑完的数据"时：**

1. `cronjob list` → 找到最近跑完的任务，看last_run_at和last_status
2. `session_search` → 搜对应的session记录（如 `cron_{job_id}_{date}`），找到输出结果
3. 直接把结果给用户

**绝对不要做的事：**
- ❌ `cronjob run` 手动触发一次新的运行（会导致重复执行，浪费资源）
- ❌ 看到last_status是error就以为任务没跑成功（可能是之前手动触发导致的error）

**正确理解last_status：**
- last_status是error ≠ 定时任务没成功
- 可能是之前某次手动触发（cronjob run）导致的error
- 要看session记录才能确认实际执行结果

**只有在以下情况才手动执行数据查看流程：**
- 定时任务今天没跑过
- 用户明确要求手动查看

**⚠️ 定时任务报错时的处理（2026-06-06教训）**

当用户说"没看到任务跑"或发现定时任务报错时：
1. 先检查错误日志，找到具体原因（如API key未设置、模型不可用等）
2. **主动修复错误**，而不是只问用户"要不要修"
3. 修复后再触发一次
4. 等待执行结果，确认成功

常见错误：
- `XIAOMI_API_KEY 未设置` → 环境变量没加载，需要在脚本中手动加载.env
- `model_not_found 503` → PackyAPI的vision模型不可用，改用Xiaomi Vision API
- `anysearch参数错误` → 命令格式不对，检查skill中的正确用法

## ⚠️ cron job 环境限制

**`execute_code` 在 cron job 中被禁止**（无用户审批模式）。如果需要用 Python 处理数据（如格式化报告、计算比率），改用 `terminal` 执行 Python 脚本，或直接在 final response 中手写 markdown 表格。

### ⚠️ Python 执行方式（2026-06-23更新）

**`python3` 命令在本机返回 exit code 49（Windows Store stub），必须用 `python` 代替。**

```bash
# ❌ python3 返回 exit code 49（Windows Store stub）
python3 script.py  # exit code 49
python3 -c "print(1)"  # exit code 49

# ❌ uv run python 有 SRE 模块 mismatch 问题（反复出现），不要使用
# uv run python script.py
# uv run python -c "print(1)"

# ✅ 用 python（不带3，不带uv）— 唯一可靠方式
python script.py
python -c "print(1)"
```

**terminal中直接用 `python -c "..."` 最简单**，无需写脚本文件。
⚠️ **绝对不要用 `uv run python`**，本机的 uv Python 版本与系统 Python 存在 SRE 模块版本冲突，每次都会报 `AssertionError: SRE module mismatch`。

**⚠️ 批量更新发展日志：Python脚本 vs 多次patch**

**当需要同时更新多个数据行（如新视频+多个已有视频数据微调）时，有两种方法：**

**方法A（推荐用于10+行更新）：Python脚本，用实际中文字符串**
```python
# ✅ 正确：Python脚本 + 实际中文字符串（不是Unicode转义）
updates = [
    ('| V28 | 我们们对... | 06-30 17:08 | 360 |', 
     '| V28 | 我们们对... | 06-30 17:08 | 362 |'),
    # ... 更多替换
]
for old, new in updates:
    content = content.replace(old, new, 1)
```
- ✅ 14行更新只需1次Python调用，比14次patch快10倍
- ✅ 实际中文字符串匹配可靠（2026-07-08验证：14/14行全部成功）
- ❌ **绝对不要用Unicode转义序列**（`\uXXXX`）——MSYS环境下匹配中文会失败

**方法B（适用于<10行更新）：多次patch调用**
```bash
patch(path="发展日志.md", old_string="| V21 | 脱碳甲醛...", new_string="| V22 | HR...")
```

**⚠️ Python脚本的坑（2026-07-08发现，2026-07-16更新）**：
1. `uv run python`（3.11）有SRE模块mismatch，**绝对不要用**
2. 系统`python`（3.10）也可能有SRE模块mismatch——如果uv Python在PATH中，即使调用`/e/Python/python.exe`，`re`模块也会被uv的版本覆盖
3. **如果Python失败，改用shell命令**：`head/tail` 操作文件行（插入/删除），`patch` 工具做单行替换
4. 批量修正评论/分享互换时，**必须逐条对照页面数据**验证每个视频的shares/comments值是否正确，不能只依赖列映射——因为有些视频在日志中已经是正确的，盲目swap会反而搞错

**✅ Python失败时的shell替代方案**：
```bash
# 插入新行（如在第440行后插入更新记录）
cd "path/to/references" && head -440 发展日志.md > /tmp/new_log.md && echo '新条目内容' >> /tmp/new_log.md && tail -n +441 发展日志.md >> /tmp/new_log.md && cp /tmp/new_log.md 发展日志.md

# 单行替换用 patch 工具（更可靠）
patch(path="发展日志.md", old_string="旧内容", new_string="新内容")
```

**⚠️ 2026-07-14教训**：batch更新时没有逐条对照页面数据，导致V23/V21的评论和分享被错误交换。**每次batch更新后，必须用read_file重新读取相关行，逐条验证每个视频的评论/分享值是否与页面数据一致。**

### ⚠️ patch 工具 escape drift（2026-07-15发现）

**当 `old_string`/`new_string` 包含复杂中文+特殊字符（如 `\"已完成\"`）时，patch 工具会报 "Escape-drift detected" 错误。**

**症状**：
```
Escape-drift detected: old_string and new_string contain the literal sequence '\\\"' 
but the matched region of the file does not.
```

**根因**：tool-call serialization 会给引号加反斜杠，但文件中的引号没有反斜杠，导致不匹配。

**解决方案**：用 `head`/`tail` 通过 terminal 操纵文件：
```bash
# 示例：在第440行后插入新条目
cd "path/to/references" && head -440 发展日志.md > /tmp/new_log.md && echo '新条目内容' >> /tmp/new_log.md && tail -n +441 发展日志.md >> /tmp/new_log.md && cp /tmp/new_log.md 发展日志.md
```

**适用场景**：
- patch 报 "Escape-drift detected" 错误
- old_string 包含 `\"`、`\'` 等转义字符
- 需要插入新行而非替换现有行

### ⚠️ patch 工具匹配失败的 Python 回退方案

**当 `patch` 工具因 old_string 匹配失败（重复行、孤立行等）无法修正文件时，用 Python 脚本直接操作文件。**

```python
# 示例：删除孤立行（lines 91-97）
with open('path/to/file.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()
new_lines = lines[:90] + lines[97:]
with open('path/to/file.md', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
```

**适用场景**：
- `patch` 报 "Found N matches for old_string" 且无法提供更多上下文区分
- 需要删除/插入多行连续内容
- 需要基于行号精确操作（而非文本匹配）

### ⚠️ Python + MSYS 中文编码陷阱

**在 MSYS/bash 环境下用 `terminal` 执行 Python 时，format 字符串中的中文字符会导致 `ValueError: unsupported format character`。**

```bash
# ❌ 会报错：中文字符在 format string 中导致编码错误
python -c "print('播放量均值: %.1f' % mean)"  # OK，无中文
python -c "print('均值: %.1f' % mean)"  # ❌ ValueError

# ✅ 解决方案1：用 ASCII-only format string
python -c "print('mean=%.1f' % mean)"

# ✅ 解决方案2：用 + 拼接（中文放在非 format 部分）
python -c "print('mean=' + str(round(mean,1)))"

# ✅ 解决方案3：print 不带中文前缀
python -c "print(round(mean,1))"
```

**根因**：MSYS 的 locale 设置不支持 UTF-8 中文，Python 的 `%` 格式化在解析 format string 时遇到多字节中文字符会失败。

```bash
# ❌ cron job 中会报错
# execute_code(code="...")

# ✅ 替代方案：直接在回复中写 markdown，或用 terminal 跑 Python
terminal(command="uv run python -c 'print(1865/6*100)'")
```

## 注意事项

1. **必须用`douyin`作为session名**（不是自定义名称）
2. **截图后用vision_analyze分析**，不要直接读DOM
3. **数据页需要JS渲染**，打开后等几秒再截图
4. **Chrome必须已经登录抖音创作者中心**，OpenCLI是复用登录态
5. **Browser Bridge未连接时**，按上述排查步骤操作
6. **⚠️ 不要点击视频列表中的视频缩略图！** 点击会打开内置播放器，不会跳转到详情页。如需查看单个视频详情，使用React onPreview或直接导航到详情页URL
7. **⚠️ 封面点击率数据可能不一致**：首次加载页面时可能显示0%，刷新或重新加载后可能显示正确值（如100%）。如果发现封面点击率为0%但其他数据正常，刷新页面后重新提取innerText验证
8. **⚠️ 完播率和2秒跳出率只在详情页显示**：列表页的innerText不包含这些指标。如需这些数据，必须导航到详情页（可通过React Fiber提取视频ID）
9. **⚠️ 详情页内容在跨域iframe中**：无法通过父页面eval访问。使用React onPreview触发预览，或直接打开iframe URL
10. **⚠️ OpenCLI open命令可能超时**：前台模式30秒限制，直接重试即可（`--background`标志不存在，不要使用）
11. **⚠️ React Fiber提取视频ID是可行的**：通过`document.querySelectorAll('[class*="video-card-z"]')`找到视频卡片，然后遍历React Fiber tree找`memoizedProps.data.aweme_id`
12. **⚠️ eval点击按钮的正确方式**：使用IIFE（立即执行函数）避免变量重复声明错误：
    ```javascript
    // ✅ 正确：使用IIFE
    (function(){
      var btn = Array.from(document.querySelectorAll('*')).find(function(el) { 
        return el.textContent.trim() === '查看分析' && el.offsetParent !== null; 
      });
      if(btn) { btn.click(); return 'clicked'; }
      return 'not found';
    })()
    
    // ❌ 错误：直接声明变量（会报Identifier has already been declared）
    var btn = Array.from(document.querySelectorAll('*')).find(...)
    ```
13. **⚠️ 等待时间很重要**：页面加载后需要等待6-8秒才能提取数据，点击按钮后需要等待3-5秒让数据加载
14. **⚠️ 从详情页返回内容管理页会丢失tab状态（2026-06-11验证）**：点击"查看分析"进入详情页后，用`opencli browser douyin open`重新打开内容管理页，页面会回到"最新作品"默认视图，**不会记住之前的"近期作品"tab**。需要重新点击"近期作品"tab。因此查看多个视频详情时，最好在每次返回后都重新点击"近期作品"tab。
15. **⚠️ eval点击返回undefined是正常行为（2026-06-11验证）**：执行`el.click()`后，eval返回`undefined`（因为`.click()`没有返回值）。**这不是错误信号**，不要因为看到`undefined`就以为点击失败。正确的做法是等待3-5秒后用`document.body.innerText`检查页面是否已切换到详情页。
16. **⚠️ 作品管理页没有"查看分析"按钮（2026-06-12验证）**：作品管理页（侧边栏→内容管理→作品管理）只有"编辑作品""设置权限""作品置顶""删除作品"按钮。要点击"查看分析"获取详细数据，必须回到内容管理概览页（重新`open`该URL）。这是最容易踩的坑——很多人（包括Agent）会以为在作品管理页就能点击"查看分析"。
17. **⚠️ 投稿列表的"分析详情"按钮在OpenCLI中无法跳转（2026-06-15验证）**：数据中心→作品分析→投稿列表中的"分析详情"按钮是`<div class="btn-y5DK0U">`元素，点击后不会导航到新页面。但表格本身已包含所有关键指标（完播率、5s完播率、2s跳出率等），无需点击"分析详情"。
**⚠️ content-manage/video URL重定向行为已变化（2026-06-15验证，2026-06-19再次验证可用）**：直接`open`这个URL曾被重定向到`/home`（2026-06-15），但2026-06-19实测可以正常加载。**建议优先使用该URL，如果重定向则回退到`/data-center/content` URL**。正确方法是通过数据中心导航，或直接使用`/data-center/content` URL。

## 定时检查（Cron Job）分类规则

当作为定时任务运行时，按发布时间分类处理。**注意：不同cron job可能配置不同的检查时间点**，以下是最常见的几种配置：

### 配置A：上午检查（18小时检查）
| 发布时间 | 检查类型 | 操作 |
|----------|---------|------|
| 今天发布的 | 18小时检查 | 记录数据 |
| 昨天发布的 | 24小时检查（最后一次） | 记录数据，标记为"已完成" |
| 更早发布的 | 不再检查 | 跳过 |

### 配置B：下午检查（6小时检查）
| 发布时间 | 检查类型 | 操作 |
|----------|---------|------|
| 今天发布的（下午发布） | 6小时检查 | 记录数据 |
| 昨天发布的 | 18小时检查 | 记录数据 |
| 更早发布的 | 不再检查 | 跳过 |

### 配置C：晚上检查（23:00左右）
| 发布时间 | 检查类型 | 操作 |
|----------|---------|------|
| 今天发布的（晚上7-10点发布） | 首次数据检查（2-5h） | 记录初始数据，标记"待6h检查" |
| 今天发布的（下午发布） | 6小时检查 | 记录数据 |
| 昨天发布的 | 最终数据检查 | 记录数据，标记"已完成" |
| 更早发布的 | 不再检查 | 跳过 |

### 配置D：15小时检查（接近24h）
| 发布时间 | 检查类型 | 操作 |
|----------|---------|------|
| 昨天发布的（晚上发布） | 15h检查（接近24h） | 记录完整数据，对比2h数据，标记"待24h确认" |
| 今天发布的 | 跳过（太早） | 跳过 |
| 更早发布的 | 不再检查 | 跳过 |

**15h检查的特殊价值**：
- 比2h检查更能反映视频的真实表现
- 比24h检查更早发现问题，及时调整
- 可以对比2h和15h的数据变化趋势
- 如果15h播放量<1000，可能需要考虑是否继续投入

**⚠️ 晚上检查特殊情况**：
- 如果视频是当天晚上7-10点发布的，距发布仅2-5小时，**不要做正式6h检查**，只记录初始数据
- 真正的6h检查应在第二天凌晨进行（如果配置了凌晨cron job）
- 如果没有凌晨cron job，则在第二天上午检查时一并记录

**判断方法**：用 `document.body.innerText` 提取的日期文本（如"2026年06月03日 17:16"）与当前日期对比。具体使用哪种配置，取决于cron job的任务描述。

### ⚠️ 新视频发现处理

如果在列表中发现**发展日志中没有记录的新视频**：
1. 立即纳入追踪，记录基础数据（播放、点赞、评论、分享）
2. 根据发布时间判断检查类型（今天→18h，昨天→24h）
3. 更新发展日志的视频数据记录表
4. 如果数据异常，触发问题诊断表中的对应规则

## 每次查看数据后必须做的事

**⚠️ 看完数据不是结束，更新发展日志+优化文案skill才是结束。**

### Step A：更新发展日志
1. 更新 `references/发展日志.md` 中的视频数据记录表
2. **⚠️ 同步更新诊断文本**：表格数据更新后，诊断文本中引用的具体数值（如"播放580""完播率1.91%"）也必须同步修正。这是最常犯的错误（错误模式2b）。
3. **⚠️ 同步更新优化分组表**：表格数据更新后，"关键优化方向"中的分组表（点赞率<1%、评论率<0.3%、5s完播率<50%等）也必须同步更新。特别是：
   - 数据漂移可能导致视频脱离或进入某个分组（如V18播放123→127，点赞率0.81%→0.79%）
   - 小样本视频（播放<50）的比率可能大幅波动（如V19从1→3播放，点赞率0%→33.33%），需在分组中注明"样本无意义"
   - 更新分组时，用最新的播放量和互动数重新计算每个视频的比率，确保分组准确
4. **⚠️ "已完成"视频也可能有显著增长（2026-06-22验证）**：即使视频已标记"已完成"，播放量仍可能大幅增长。**V22案例**：24h检查时807播放标记"已完成"，但后续增长到1,471（+82.3%），接近往期均值。**规则**：每次cron job检查时，都要对比发展日志中"已完成"视频的播放量与数据中心最新值，发现显著增长（>20%）则更新记录。
5. 如果有里程碑事件（破1000播放、破100赞等），更新里程碑表
6. 如果发现新的经验教训，添加到"经验教训"部分
7. 更新待验证假设的状态（验证了就打勾）

### Step B：优化hot-roast-writer skill（必须生成可执行规则）

**⚠️ 何时跳过**：如果本次检查是常规数据更新（播放量增长、点赞增加），且没有发现新的内容规律或异常模式，则跳过Step B和Step C。只有当发现以下情况时才执行：
- 某个视频的数据显著偏离往期模式（如完播率突然翻倍）
- 发现新的有效标题模式或话题类型
- 某个指标出现系统性恶化趋势
- 用户提出新的文案要求或约束

**⚠️⚠️⚠️ 用户纠正（2026-06-14）：不要只说"加金句""控制时长"这种模糊建议，要生成可执行的具体规则。**

**具体做法**：把数据诊断结论翻译成hot-roast-writer可执行的规则，用 `skill_manage(action='patch')` 写入。

| 数据表现 | 生成的规则（写入hot-roast-writer） |
|----------|-----------------------------------|
| 完播率<10% | 在Agent3执行前检查中加：视频必须≤1:30，每15秒一个钩子 |
| 点赞率<1% | 在Agent3执行前检查中加：必须设计2个以上情绪爆点（自嘲、反转、金句） |
| 评论率<0.3% | 在Agent3执行前检查中加：结尾必须有反问观众的句子 |
| 5s完播率<50% | 在Agent3执行前检查中加：前5秒必须有强钩子 |
| 2s跳出率>30% | 在Agent3执行前检查中加：开头3秒内必须给钩子 |
| 某类话题表现好 | 在Agent2选题优先级中加：这类话题排前面 |
| 某类话题表现差 | 在Agent2选题禁忌中加：这类话题降级 |
| 标签组合效果好 | 在Agent3标签规则中加：记录有效标签组合 |

**⚠️ 禁止行为**：
- ❌ 不要只在报告中说"应该优化"，要实际执行 `skill_manage(action='patch')`
- ❌ 不要给出模糊建议（如"加强情绪共鸣"），要具体到文案的哪一行加什么
- ❌ 不要重复已知问题，要给出新的解决方案
- ✅ 要生成可执行的、具体的、可验证的规则

### Step C：更新Skill优化日志
1. 更新 `references/Skill优化日志.md` 的优化记录表
2. 标注影响了哪个Agent
3. 更新待验证/已验证状态
4. 统计每个Agent的优化次数

这样形成闭环：写文案 → 发布 → 看数据 → 更新日志 → 优化skill → 记录优化 → 下一条文案更好

### ⚠️ 分析时不要重复skill里已有的建议（2026-06-14用户纠正）

**当数据分析发现问题时，不要重复skill里已经写好的改进建议（如"控制时长""前5秒钩子""第二个钩子"）。**

用户原话："这些都在skill是有的，你得看怎么改进到每次都能执行"

**正确做法：**
1. 先确认skill里是否已有对应的改进建议
2. 如果有 → 不要重复建议，而是分析"为什么这些建议没有被执行"
3. 找出执行层面的gap（如：数据分析和文案写稿是分开的两个session，数据结论没有传递到文案执行中）
4. 提出具体的执行改进方案（如：在文案skill中加入"执行前数据对齐"步骤）

**错误示范：**
- ❌ "完播率低，建议控制在1:15-1:30" → 这个建议skill里已经有了
- ❌ "点赞率低，建议加金句" → 这个建议skill里已经有了

**正确示范：**
- ✅ "完播率低的问题skill里已有建议，但每次执行时没有检查上一个视频的数据问题。建议在文案skill中加入数据对齐步骤"
- ✅ "点赞率连续7个视频低于1%，说明执行层面没有落实'加金句'的建议。需要在质检时检查'这条文案是否解决了上一个视频的问题'"

## 审核机制（2026-06-09新增，2026-06-10增强）

数据采集cron job跑完后，有独立的审核cron job做交叉检查：

| 任务 | 时间 | 职责 |
|------|------|------|
| 抖音数据-上午 | 11:00 | 采集数据 |
| 抖音数据-审核 | 11:30 | 审核上午采集结果 |
| 抖音数据-晚上 | 23:00 | 采集数据 |
| 抖音数据-审核(晚) | 23:30 | 审核晚上采集结果 |

**审核内容：**
1. 数据校验——点赞率、评论率是否算对，指标是否在合理范围
2. 诊断复核——上一轮的诊断和数据是否对得上
3. 遗漏发现——上一轮没注意到的规律
4. 趋势对比——最近3个视频同阶段数据对比

**审核结果处理：**
- ✅通过 → 无需操作
- ⚠️有疑点 → 标记到发展日志，下次采集时重点验证
- ❌有问题 → 修正发展日志中的错误数据/诊断

### ⚠️ 审核必做：逐条计算验证（2026-06-10验证）

**不要只看记录值，必须用原始数据重新计算。** 已发现的错误模式：

**错误模式1：阈值比较方向搞反**
- 案例：视频7评论率 2/305 = 0.66%，记录说"低于0.3%合格线"
- 实际：0.66% > 0.3%，已达标
- 原因：采集时可能在小样本阶段（6h时0条评论/0%），24h更新后忘了重新判断
- **校验方法**：对每条视频，用 `点赞/播放×100` 和 `评论/播放×100` 重新计算，与记录值对比

**错误模式2：快照值未更新到最终值**
- 案例：视频4点赞率记录为0.53%（来自15h快照 10/1900），最终值应为11/1940=0.57%
- 原因：数据表在15h检查时填写，24h最终数据来后没有同步更新比率
- **校验方法**：检查数据表中的比率是否与最终的播放量/点赞/评论一致

**错误模式2a：旧播放量残留计算（2026-06-19发现）**
- 案例：V18诊断文本写"点赞率1.16%"，但最终播放量是123（1/123=0.81%）。1.16%实际是播放量86时的计算结果（1/86=1.16%），数据更新后未重新计算
- 原因：诊断写好后，播放量从86增长到123，但比率没有用新分母重新计算
- **校验方法**：对诊断文本中每个比率，用数据表当前的播放量和互动数重新计算。公式：`点赞率 = 点赞/播放×100`，`评论率 = 评论/播放×100`
- **修复方法**：用新播放量重新计算并修正诊断文本中的比率值

**错误模式2b：诊断文本引用过期中间值（2026-06-13发现）**
- 案例：V12（LOL老玩家）诊断文本中评论率记录为0.16%（基于24h检查时的数据 3/1865），但数据表已更新为最新值（5/1960=0.26%）。审核cron成功发现了这个差异。
- 原因：诊断结论写好后，数据表被后续更新覆盖了原始值，但诊断文本没有同步修正
- **校验方法**：审核时不仅要比对数据表，还要比对诊断文本中引用的具体数值。如果诊断说"评论率0.16%"，用数据表当前的播放量和评论数重新计算，看是否一致
- **修复方法**：发现不一致时，用 `patch` 工具修正诊断文本中的过期数值，不要只在报告中说"应该修正"

**错误模式3：诊断结论与数据矛盾**
- 采集时的诊断可能基于早期数据，后续数据更新后诊断未同步修正
- **校验方法**：重新阅读每条诊断，用最终数据验证结论是否仍然成立

### 审核校验清单（逐条执行，必须全量重新计算）

```
对每个视频：
1. 用最终播放量重新计算：点赞率 = 点赞/播放×100，评论率 = 评论/播放×100
2. 对比计算值与记录值，差异>0.05%则标记为⚠️
3. 检查所有指标是否在合理范围（0-100%）
4. 重新阅读每条诊断结论，用最终数据验证
5. 检查对比表中的数据是否与各视频最终值一致
6. 在发展日志中新增"审核记录"章节，记录修正结果

⚠️ 关键：对优化分组表做"反向校验"——不是检查某条视频是否在组里，而是遍历全部视频，看每条应该在哪个组，然后对比分组表是否遗漏或多列。

⚠️ 新增视频后必做：添加新视频（如V18）后，重新验证所有视频的排名描述：
- "全号最低/最高" → 遍历所有视频确认
- "倒数第N" → 按指标排序后确认位置
- 里程碑中的排名描述 → 用当前完整数据集重新计算
- 诊断文本中的对比描述 → 确认对比对象和数值正确

⚠️ 上轮"已修正"验证：检查上一轮审核记录中标注"已修正"的项目，用 read_file 重新读取相关行确认修正确实生效。不能因为标注了"已修正"就跳过检查。
```

### ⚠️ 审核陷阱：只标记不修正（2026-06-18总结，第五次审计反复出现）

**问题**：审核cron多次发现同一个错误（如V13/V6误入"5s完播>50%但总完播<3%"分组），但连续5轮审计都只是"标记"而没有实际用 `patch` 修正，导致问题持续存在。

**根因**：审核报告只是输出了发现，没有执行修正动作。

**规则（强制执行）**：
1. **审核发现 = 修正动作**：每发现一个数据错误，必须立即用 `patch` 工具修正发展日志，不能只在审核报告中说"应该修正"
2. **"反向校验"优先于"正向检查"**：不要问"V13是否在正确分组里"，而是问"V13的完播率3.30%>3%，那分组条件'总完播<3%'是否排除了V13"——这样才不会遗漏
3. **系统性问题要全局扫描**：当发现"点赞率<1%"只列了4条视频时，必须遍历全部13条视频计算点赞率，看实际有多少条<1%（答案：12条）
4. **里程碑数据必须与表格最终值对齐**：如果表格中V16的2s跳出率是12.04%，里程碑里就不能写11.44%
5. **诊断文本中的具体数字必须与表格一致**：如果诊断写"5s完播率44.53%"但表格写44.59%，这是需要修正的错误，不是"微小差异"

### ⚠️ 审核陷阱：诊断文本内自相矛盾（2026-06-19发现）

**问题**：同一视频的诊断文本中，不同段落引用的数值不一致。例如V17诊断中，行109写"播放729"（与表格一致），但行119写"播放量从373→723"（差6），增长率也因此错误（93.8%应为95.4%）。

**根因**：诊断文本分多次写入（首次检查→最终检查），后写的段落没有回溯修正前文。

**规则**：
1. **同一视频诊断内的所有数值必须自洽**：如果行109说"播放729"，行119的增长计算也必须用729
2. **增长百分比必须与播放量对齐**：如果播放量从373→729，增长率=(729-373)/373=95.4%，不能写93.8%
3. **引用其他视频的数据必须用最终值**：如V17诊断引用V18的5s完播率，必须用V18最终值35.71%而非首次值33.72%
4. **审核时对同一视频的所有段落做交叉验证**：不仅要比对表格，还要比对诊断内不同段落的数值

### 审核陷阱：里程碑排名未随新视频更新（2026-06-19发现）

**问题**：里程碑中的排名描述在新视频添加后失效。如V16里程碑称"完播率第7低"，加入V19/V18后实际为"第9低"。V13里程碑称"2s跳出率全号最低（12.91%）"，但V16后来以12.04%超越。

**规则**：
1. **添加新视频后，必须重新计算所有里程碑中的排名描述**
2. **里程碑中的"全号最低/最高"描述需要加注"后被XX超越"**
3. **系统级统计（条均完播率、5s均值）在新视频添加后必须重新计算**
4. **里程碑中的数值必须与表格最终值对齐**（如V13播放应为2456而非2447）

### ⚠️ 定时更新后诊断文本全面脱节（2026-07-08发现，累积第四次）

**问题**：定时数据更新（cron job）只修改了数据记录表的数值（播放量、完播率等），但没有同步更新诊断正文、优化分组表、系统统计值。导致**全部23条视频的诊断文本引用的播放量、完播率、5s完播率等全部过时**。

**根因**：定时更新流程只做"表格微调"（播放量+2、点赞+1等），不会触发诊断文本的重新计算。

**具体影响**：
- 所有视频诊断正文的播放量过时
- V27完播率诊断写10.54%→实际10.36%，V26写1.69%→实际1.68%等
- V21收藏数诊断写1→实际2，V19播放写11→实际12
- 优化分组表V27完播率写10.2%→实际10.36%
- 系统均值完播率2.88%→实际2.97%，5s完播率43.85%→实际42.97%

**规则（强制执行）**：
1. **定时更新后必须做"诊断同步扫描"**：遍历所有视频的诊断正文，对比诊断中引用的具体数值与表格最新值，发现不一致则用patch修正
2. **优化分组表做"数据新鲜度检查"**：对比分组表中每个数值与数据表最终值
3. **系统统计值（完播率均值、5s均值）在每次数据变更后重新计算**
4. **评论率分组需定期全量校验**：用最新数据重新计算所有视频的评论率，确认分组计数准确（2026-07-08发现V10/V12/V7被遗漏，实际22条非声称的20条）
5. **⚠️ 表格自身也可能部分过时（2026-07-13发现）**：定时更新日志记录了率值变化（如"5s 49.17%→48.96%"），但表格中的完播率/5s完播率/2s跳出率列仍显示旧值，只有播放量已同步。**审核时不仅要比对"诊断vs表格"，还要比对"更新日志vs表格"**——如果更新日志说V27 5s从49.17%变为48.96%，但表格仍显示49.17%，说明表格率列未同步。**验证方法**：检查最近一次更新日志中的"→"右侧值是否与表格一致。

### ⚠️ 遗漏陷阱：质量恶化趋势被高推荐率掩盖（2026-06-23发现）

**问题**：视频推荐页占比高（>99%）时，诊断容易只关注"算法在推"而忽略质量指标的下滑。

**案例**：V21→V22
- V22推荐页99.4%，诊断只说"算法强力推荐"
- 但播放量从1,808降至1,471（-18.6%），完播率从3.29%降至1.64%（-50.2%），点赞从12降至5（-58.3%）
- 质量指标全面下滑，诊断完全未提及

**规则**：
1. **趋势对比必须用同阶段数据**：对比V21和V22时，都用最终值或都用首次值
2. **推荐页占比高不代表内容质量好**：算法推流≠内容留人，必须同时检查完播率、互动率趋势
3. **当连续2+个视频质量指标下降时，必须在诊断中标注恶化趋势**
4. **审核时对最近3个视频做"质量趋势表"**：播放量、完播率、5s完播率、点赞数逐个对比

### ⚠️ 遗漏陷阱：话题类型规律未总结（2026-06-23发现）

**问题**：数据中存在明显的话题类型规律，但诊断只逐条分析没有归纳。

**案例**：辟谣/科普话题完播率普遍高于均值
- V8(金价暴跌) 6.61%、V13(西瓜打针) 3.28%、V21(脱碳甲醛) 3.29%、V23(圣女果) 5.45%
- 均值2.83%，该类型全部高于均值
- 诊断未归纳此规律

**规则**：
1. **每5个视频后做一次"话题类型分析"**：按话题分类统计平均完播率、互动率
2. **发现某类话题持续表现好/差时，必须在诊断中归纳并更新选题优先级**
3. **审核时检查诊断是否遗漏了跨视频的规律性发现**

### 审核陷阱：优化分组表首次值残留（2026-06-21发现）

**问题**：新视频首次检查时，数据被添加到"关键优化方向"分组表。但24h最终数据来后，分组表中的数值没有同步更新。V21在分组表中显示5s完播率=38.60%、点赞率=0.90%、评论率=0.10%（首次检查值），实际最终值为44.56%、0.68%、0.06%。

**根因**：首次检查时采集cron将数据写入分组表，但最终检查时采集cron只更新了数据表和诊断文本，没有回溯更新分组表。

**规则**：
1. **每次新视频最终数据检查后，必须遍历"关键优化方向"分组表，确认该视频的所有比率值已更新为最终值**
2. **特别注意首次检查时用旧播放量计算的比率**：如V21首次998播放时点赞率0.90%（9/998），最终1770播放时0.68%（12/1770），分组表必须用最终值
3. **审核时对分组表做"数据新鲜度检查"**：对比分组表中的每个数值与数据表最终值，不一致则标记

### 审核陷阱：三处数据不同步（2026-06-23发现）

**问题**：同一视频的数据在三个位置不一致——数据记录表（表格）、诊断正文、里程碑。更新其中一处后遗漏另外两处。

**案例**：V19「纸尿裤」
- 表格：播放6，2s跳出率60%，评论0
- 诊断正文：播放3，2s跳出率50%，评论1（33.33%）
- 里程碑：播放3，2s跳出率50%
- → 表格已更新至6播放，但诊断和里程碑仍引用旧的3播放数据

**根因**：数据更新时只修改了表格，没有回溯检查诊断正文和里程碑中引用的同一视频数据。

**规则**：
1. **每次更新表格数据后，必须在诊断正文和里程碑中搜索该视频的所有引用，同步更新**
2. **审核时对每个视频做"三处交叉验证"**：表格值 = 诊断值 = 里程碑值
3. **优先级：表格为准**，诊断和里程碑必须与表格对齐

### 审核陷阱：错误均值导致错误诊断结论（2026-06-23发现）

**问题**：播放量均值计算错误后，诊断结论中引用均值做的判断也随之错误。

**案例**：
- 日志均值1,553（实际1,386，偏差+12.0%）
- V22诊断称"播放量1,471接近往期均值"
- 实际：1,471 > 1,386（高于均值6.1%），应表述为"略高于均值"

**规则**：
1. **均值/中位数必须先独立验证正确，再用其做诊断判断**
2. **诊断中涉及"接近均值""高于/低于均值"的表述，必须用实际均值重新验证**
3. **当均值错误被修正后，所有引用均值的诊断结论必须逐条复核**
4. **低播放量视频会显著拉低均值（2026-06-28验证）**：V27仅107播放，将均值从1,460拉低至1,375（-5.8%）。当新视频播放量远低于往期均值时，均值会大幅下降，此时"播放量接近均值"的判断需要更新为"播放量低于均值"。诊断结论中引用均值时，必须用最新计算值。

### 审核陷阱：跨阶段数据对比（2026-06-23发现）

**问题**：对比两个视频时混用首次检查值和最终值，导致对比不公平。

**案例**：V23诊断称"5s完播率42.45%优于V22（42.17%）"
- V23是首次检查值（42.45%）
- V22引用的是最终值（42.17%）
- V22首次检查值其实是44.91%——如果用同阶段对比，V23(42.45%) < V22首次(44.91%)

**规则**：
1. **同阶段对比原则**：对比两个视频时，必须使用相同检查阶段的数据（都是首次检查值，或都是最终值）
2. **如果必须跨阶段对比，必须明确标注**："V23首次检查完播率5.45%高于V22最终值1.64%"
3. **审核时检查诊断中的跨视频对比是否使用了同阶段数据**

### 审核陷阱：中位数反复计算错误（2026-06-21发现，多次审计反复出现）

**问题**：播放量中位数在多次审计中被错误计算。06-21审计发现日志写1,537，实际应为1,782。此前06-20审计也发现中位数错误（1,715 vs 1,701.5）。

**根因**：每次添加新视频后，中位数被重新计算，但排序或取中间值的步骤出错。

**🔴🔴🔴 中位数验证步骤（每次计算后必须执行）**

**中位数正确公式**：
- **N为偶数时**：取第 N/2 和第 N/2+1 位的平均值
- **N为奇数时**：直接取第 (N+1)/2 位的值（不需要平均！）

**逐条验证方法**：
```bash
# 计算中位数后，必须用以下代码验证：
python -c "
plays = [368,478,1211,1539,845,1602,1524,1970,2031,12,153,734,2044,1048,1479,2473,2020,1803,2291,310,1614,1880,1982]
plays.sort()
n = len(plays)
if n % 2 == 1:
    median = plays[n//2]
else:
    median = (plays[n//2-1] + plays[n//2]) / 2
print(f'N={n}, median={median}, sorted[{n//2}]={plays[n//2]}')
"
```

**⚠️ 常见错误**：对奇数N也用了偶数公式（取中间两个值平均），导致结果偏移。2026-07-14发现：日志写中位数1600，实际应为1539（sorted[11]），偏差+4.1%。

**2026-07-14教训（回归式修复，2026-07-15发现）**：即使有上述文档和验证代码，agent仍然算错了中位数。根因：没有运行验证代码就直接写入日志。**每次计算中位数后必须运行上述验证代码确认结果。**

**⚠️ Python代码陷阱（2026-07-13发现）**：
```python
# ❌ 错误：对奇数N也用了偶数公式，结果偏移
n = len(sorted_plays)  # n=23 (奇数)
median = (sorted_plays[n//2-1] + sorted_plays[n//2]) / 2  # 取了第11和第12位平均=1524.5

# ✅ 正确：奇数N直接取中间值
n = len(sorted_plays)  # n=23 (奇数)
median = sorted_plays[n//2]  # 取第12位=1531
```

**示例（23条视频，N为奇数）**：
- 排序后第12位=1,531(V25)，中位数=1,531
- 错误公式取第11位(1,518)和第12位(1,531)平均=1,524.5，偏差-0.4%

**示例（16条视频，N为偶数）**：
- 排序后第8位=1770(V21)，第9位=1794(V11)，中位数=(1770+1794)/2=1782

**规则**：
1. **每次更新数据表后，必须用正确公式重新计算中位数**
2. **审核时独立验证中位数**：排序播放量列表，奇数取中间值，偶数取中间两值平均
3. **同时验证最高值和最低值**：遍历播放量列表确认max和min

### 审核陷阱：伪修正（2026-06-19发现，第7次审计仍未解决）+ 回归式修复（2026-07-09发现）

**问题**：审核记录中标注"已修正"，但实际重新读取文件后发现修正并未生效。连续多轮审计（06-18 00:00声称"已修正"→06-18 23:00标记"✅通过"→06-19 00:30重新发现同一问题）。

**⚠️ 回归式修复（2026-07-09发现，新变体）**：07-08更新声称"修复V21/V19评论/分享互换（评论1→0，分享0→1）"，但实际上页面数据显示V21评论=1/分享=0、V19评论=1/分享=0。**07-08的"修复"把正确的值交换了，引入了新的互换。** 根因：更新者混淆了cells[9]=分享和cells[10]=评论的映射关系，把页面数据的分享值当作评论值处理。

**根因**：
1. 审核报告写完后没有重新读取文件验证修正已生效
2. `patch` 工具的 old_string 匹配失败时可能静默跳过（hunk命名不准确导致找不到目标）
3. 后续审计只看审核记录的"已修正"标签，没有独立验证

**规则（强制执行）**：
1. **修正后必须验证**：每次用 `patch` 修正发展日志后，立即用 `read_file` 重新读取相关行，确认修正已实际生效。不能只依赖 `patch` 返回的 `success: true`
2. **审核记录中的"已修正"不可信**：后续审计不能因为前一轮标注"已修正"就跳过检查，必须独立重新验证
3. **`patch` 工具 old_string 必须精确**：使用实际文件内容作为 old_string（包含足够上下文），不要用描述性 hunk 名称（如 `@@ add audit record @@`）。如果 old_string 匹配不到，`patch` 会静默失败
4. **排名描述必须在每次数据变更后重新计算**：添加新视频（如V18）后，之前视频的排名（"倒数第N"、"全号最低"等）可能变化。必须用完整数据集重新排序验证
5. **同一诊断文本内的数字必须自洽**：如果同一视频的诊断中出现两处播放量增长百分比（如+7.6%和+7.3%），必须核实哪个正确并统一

### 审核修正必须实际应用

**发现错误后，必须用 `patch` 工具实际修正发展日志中的相关行，不能只在报告中说"应该修正"。** 修正后必须用 `read_file` 验证修正已生效。

## ⚠️ 桌面浮窗问题排查（2026-06-12）

如果用户报告桌面出现奇怪的浮窗/置顶窗口（无论打开什么程序都显示在最前面）：

**常见来源**：
- **douyin_tray**：抖音托盘浮窗卡住，结束这个进程即可，抖音会自动重启
- 游戏overlay（如原神YuanShen.exe）
- 临时目录的可疑进程（如`AppData\Local\Temp\...\xxx.exe`）

**排查命令**：
```bash
# 查找游戏进程
tasklist | grep -i -E "Genshin|YuanShen|mihoyo|hoyoverse"

# 查找TOPMOST窗口（PowerShell）
powershell -command 'Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Select-Object Name, Id, MainWindowTitle'
```

**用户实测**：结束 `douyin_tray` 进程后，桌面白框消失。
