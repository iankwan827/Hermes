---
name: douyin-data-check
description: "抖音数据查看。用OpenCLI复用Chrome登录态，打开创作者中心，eval提取文本数据。"
tags: ["douyin", "data", "analytics", "opencli"]
triggers:
  - "看看数据"
  - "抖音数据"
  - "查看播放量"
  - "视频数据"
---

# 抖音数据查看 Skill

## ⚠️ 核心工具：OpenCLI

**OpenCLI复用你本地Chrome的登录态来操作网站。** 不需要额外登录，Chrome已经登录了抖音创作者中心。

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
- ❌ `content-manage/video` → 会重定向到 home
- ❌ 投稿列表中的"分析详情"按钮 → div元素点击不触发跳转（2026-06-15验证）
- ❌ 方法A（侧边栏导航）→ 步骤多，容易失败

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
| 5秒完播率 | >50% | >70% | 开头是否抓人，冷启动基础门槛 |
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

**⚠️ 点击"流量分析"tab的坑（2026-06-10验证）**：`Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '流量分析' && el.offsetParent !== null)` 会匹配到 HTML/BODY 等父容器（因为它们的 textContent 也包含"流量分析"），导致返回 undefined。**必须加 `el.children.length === 0` 过滤叶子节点**：
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

## OpenCLI常用命令速查

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
opencli doctor
# 应显示：[OK] Extension: connected

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

```bash
# 检查 Chrome 是否在运行
tasklist | grep -i chrome

# 如果 Chrome 在运行但扩展未连接，重启 daemon
opencli daemon restart
sleep 5
opencli doctor

# 如果仍未连接，可能需要重新加载扩展（见上方"扩展完全未安装时的手动安装"）
```

### 完整的 Cron Job 启动流程

```bash
# 1. 检查 Chrome 是否已在运行
if ! tasklist 2>/dev/null | grep -qi chrome; then
  echo "Chrome not running, starting..."
  # 后台启动 Chrome（使用 terminal background=true）
  sleep 12
fi

# 2. 验证 OpenCLI 连接
opencli doctor
# 如果未连接，重启 daemon
# opencli daemon restart

# 3. 打开抖音创作者中心
opencli browser douyin open "https://creator.douyin.com/creator-micro/content-manage/video"
sleep 5

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

## ⚠️⚠️⚠️ 每次查看数据前必须做的事（血的教训）

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

**`python3` 命令在本机返回 exit code 49（Windows Store stub），必须用 `python` 或 `uv run python` 代替。**

```bash
# ❌ python3 返回 exit code 49（Windows Store stub）
python3 script.py  # exit code 49
python3 -c "print(1)"  # exit code 49

# ✅ 用 python（不带3）
python script.py
python -c "print(1)"

# ✅ 或用 uv run python
uv run python script.py
```

**terminal中直接用 `python -c "..."` 最简单**，无需写脚本文件。

### ⚠️ 批量更新发展日志：用多次 `patch` 而非 Python 脚本

**当需要同时更新多个数据行（如新视频+多个已有视频数据微调）时，不要写一个大 Python 脚本用 Unicode 转义序列（`\uXXXX`）拼接中文字符串。** Unicode 转义序列在 MSYS 环境下匹配文件中的中文文本时经常失败（字符编码不一致），导致 `str.replace()` 找不到目标。

**正确做法**：用多次 `patch` 调用，每次传入实际的中文字符串：
```bash
# ✅ 正确：多次 patch，直接用中文
patch(path="发展日志.md", old_string="| V21 | 脱碳甲醛...", new_string="| V22 | HR... |\n| V21 | 脱碳甲醛...")
patch(path="发展日志.md", old_string="| V20 | 父母为你好... | 1,981", new_string="| V20 | 父母为你好... | 2,000")

# ❌ 错误：Python 脚本用 \u 转义序列
content = content.replace("\u0056\u0032\u0031...", "| V22 ...")  # 经常匹配失败
```

**什么时候可以用 Python**：只有当替换内容不包含中文字符（如纯数字、英文、百分比）时，Python 脚本才可靠。

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

**中位数正确公式（N=偶数时）**：
1. 将所有播放量从小到大排序
2. 取第 N/2 和第 N/2+1 位的值
3. 中位数 = (第N/2位 + 第N/2+1位) / 2

**示例（16条视频）**：
- 排序后第8位和第9位的平均值
- 如当前数据：第8位=1770(V21)，第9位=1794(V11)，中位数=(1770+1794)/2=1782

**规则**：
1. **每次更新数据表后，必须用正确公式重新计算中位数**
2. **审核时独立验证中位数**：排序播放量列表，取中间两值的平均
3. **同时验证最高值和最低值**：遍历播放量列表确认max和min

### ⚠️ 审核陷阱：伪修正（2026-06-19发现，第7次审计仍未解决）

**问题**：审核记录中标注"已修正"，但实际重新读取文件后发现修正并未生效。连续多轮审计（06-18 00:00声称"已修正"→06-18 23:00标记"✅通过"→06-19 00:30重新发现同一问题）。

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
