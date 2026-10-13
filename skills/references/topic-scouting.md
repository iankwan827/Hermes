# 抖音热搜选题侦察

## 触发时机
用户说"看看热搜"、"今天有什么选题"、"找找选题"

## 流程

### Step 1：拉抖音热搜全榜

**方法A（推荐，免登录）：抖音热搜API**
```bash
curl -s "https://www.douyin.com/aweme/v1/web/hot/search/list/" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Referer: https://www.douyin.com/" | node -e "
const d=[];process.stdin.on('data',c=>d.push(c));process.stdin.on('end',()=>{
  const data=JSON.parse(Buffer.concat(d).toString());
  (data.data?.word_list||[]).slice(0,30).forEach((item,i)=>{
    console.log(String(i+1).padStart(2)+'. '+item.word+'  ('+item.hot_value+')');
  });
});"
```
返回JSON中 data.word_list 就是热搜列表，含热度数值，最稳定。

**方法B：OpenCLI浏览器（搜话题详情时用）**
```bash
opencli browser default open "https://www.douyin.com/hot"
```
⚠️ 注意用 `default` session（已登录抖音），不要用自建的 `douyin` session（无登录态）。

**不要用微博、不要用web搜索代替。** 默认平台是抖音。

### Step 2：通读全榜50条
- 逐条过，找与账号定位（粤语栋笃笑/吐槽）能搭上的选题
- 重点关注：身边小事、日常生活、有共鸣的话题
- 排除：纯政治、纯体育赛事结果、纯娱乐八卦（除非能吐槽）

### Step 3：筛选标准
适合做选题的：
- 普遍体验类（如"什么行为改善了你的心理健康"）
- 日常生活类（如"坐三轮车情绪价值拉满"）
- 有反差/荒诞感的（如"中国小电驴在英国卖爆了"）
- 能用粤语吐槽切入的（如"方言版"系列有交集）

不适合的：
- 纯新闻事件（如某地暴雨）
- 太专业/小众的（如ETF、特定品牌事件）
- 已经过了时效的（如昨天的体育赛果）

**热搜分类快速过滤（2026-06-07 新增）：**

拿到热搜全榜后，先快速分类再逐条筛选：

| 类别 | 例子 | 适合度 | 处理方式 |
|------|------|--------|----------|
| 高考/考试类 | 高考语文、第一批丢身份证 | ⭐⭐⭐ | 大众化但要找"身边小事"角度（丢身份证、爸妈紧张），不要做"加油"类空洞内容 |
| 社会/民生类 | 金饰价格大降、暴雨 | ⭐⭐⭐ | 从打工人/钱的角度切入最稳 |
| 体育/电竞 | 哈兰德、BLG击败JDG | ⭐ | 受众窄，除非有荒诞/搞笑角度（如哈兰德模仿大赛第二名） |
| 综艺/娱乐 | 歌手、乘风、奔跑吧 | ⭐ | 不适合吐槽定位，除非能反讽 |
| 生活/季节类 | 夏天就要Seawalk、西瓜季节 | ⭐⭐ | 轻松搞笑方向，适合但要有共鸣点 |
| 专业/学历类 | 我学这个的他们都不信 | ⭐⭐⭐ | 完美匹配打工人方向，专业被误解人人有共鸣 |

**推荐选题的判断标准：**
1. 跟你之前表现最好的方向一致吗？（职场/打工人：公司跑路1940播放，已读1766播放）
2. 能不能找到"身边小事"的切入角度？
3. 大众化吗？不做自媒体的人也会看吗？

### Step 4：点进去看详情（不能只看标题）
- 对感兴趣的2-3个话题，搜索具体内容（视频、新闻、评论区）
- **搜索话题详情用 `default` session**（已登录抖音）：
  1. `opencli browser default open "https://www.douyin.com/search/关键词?type=video"`
  2. `sleep 4` 等页面加载
  3. `opencli browser default eval "..."` 提取搜索结果
- **不要用 `douyin` session**：该session无登录态，搜索页会卡在登录页面
- 话题详情页URL格式：`https://www.douyin.com/hot/{topic_id}/{topic_name}`，但topic_id会变，必须从热榜页面动态获取
- 确认内容的真实经过、网友反应、有没有后续回应
- 用户原话："最搭的几个你都点进去看过内容吗？" — 不点进去就推荐 = 没做功课

### Step 5：给用户3-5个候选方向
不要预设用户要什么话题。给候选让用户选，或用户说"再找找"继续挖。

## 多平台扫描（用户说"看看有没有啥选题"时）
当用户要你广泛找选题，不要只看抖音。用以下直接API比tophub更稳定：

### 各平台直接API（curl+node，免登录）

**抖音热搜（首选）：** 见上方 Step 1

**微博热搜：**
```bash
curl -s "https://weibo.com/ajax/side/hotSearch" \
  -H "User-Agent: Mozilla/5.0" -H "Referer: https://weibo.com/" | node -e "
let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{
  const data=JSON.parse(d);
  (data.data?.realtime||[]).slice(0,15).forEach((w,i)=>{
    const tag=w.is_hot?' [热]':w.is_new?' [新]':w.is_fei?' [沸]':'';
    console.log(String(i+1).padStart(2)+'. '+w.note+' ('+w.num+')'+tag);
  });
});"
```
⚠️ Windows下node读stdin需要用临时文件方案（见下方Windows注意事项）。

**百度热搜：**
```bash
curl -s "https://top.baidu.com/board?tab=realtime" -H "User-Agent: Mozilla/5.0" | node -e "
let html='';process.stdin.on('data',d=>html+=d);process.stdin.on('end',()=>{
  const m=html.match(/\"word\":\"([^\"]+)\"/g)||[];
  m.slice(0,15).forEach((w,i)=>{
    console.log(String(i+1).padStart(2)+'. '+w.replace(/\"word\":\"/,'').replace(/\"$/,''));
  });
});"
```

**今日头条热榜：**
```bash
curl -s "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc" \
  -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.toutiao.com/" | node -e "
let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{
  const data=JSON.parse(d);
  (data.data||[]).slice(0,15).forEach((w,i)=>{
    console.log(String(i+1).padStart(2)+'. '+w.Title);
  });
});"
```

**头条搜索（搜具体话题详情时用）：**
```bash
curl -s "https://so.toutiao.com/search?keyword=关键词&pd=information&source=input" \
  -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.toutiao.com/" | node -e "
let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{
  const abstracts=d.match(/\"abstract\":\"[^\"]*\"/g)||[];
  abstracts.slice(0,5).forEach((a,i)=>{
    const t=a.replace(/\"abstract\":\"/,'').replace(/\"$/,'');
    console.log((i+1)+'. '+t);
  });
});"
```

### Windows下Node.js读stdin的坑
Windows的Git Bash/MSYS2下，`process.stdin` pipe给node -e会失败（`/dev/stdin`不存在）。解决方案：
1. **用临时文件**：`curl -s URL -o /d/hermes-agent/tmp.json && node -e "...readFileSync('D:/hermes-agent/tmp.json','utf8')..."`
2. **避免用pipe**：先把curl结果存文件，再用node读文件解析
3. Python的`json`模块在Windows uv环境下可能报`SRE module mismatch`，用node替代

### 备选：tophub.today
当上述API都不可用时，用tophub：
```bash
opencli browser douyin open "https://tophub.today/n/KqndgxeLl9"  # 微博
opencli browser douyin open "https://tophub.today/n/mproPpoq6O"  # 知乎
```

## 工具备选（Fallback Chain）

**优先级：anysearch → Node.js anysearch → OpenCLI浏览器 → 直接网页**

### 1. Python anysearch 失败
- Python anysearch_cli.py 可能报 `SRE module mismatch` 错误（uv Python环境问题）
- 直接切换到Node.js版：`node <skill_dir>/scripts/anysearch_cli.js <command>`
- Node.js版参数不同：用 `search "关键词"` 而不是 `search --query "关键词"`，用 `-z cn` 指定中国区
- 功能完全一样，不需要修Python环境

### 2. anysearch 额度用完（2026-06-13 实测）
- anysearch 免费额度有每日上限（实测约10000+次/天），用完返回 `user_daily_quota_exhausted`
- 此时只能用浏览器方案，anysearch当天内不可恢复
- **不要反复重试**，直接切浏览器

### 3. Camofox 浏览器不可用
- 如果 Camofox 没启动（`Cannot connect to Camofox at http://localhost:9377`），用 OpenCLI：`opencli browser <session> open <url>`
- OpenCLI 复用 Chrome 登录态，不需要额外服务
- session名：抖音搜索/详情用 `default`（已登录），不要用自建的 `douyin` session（无登录态）

### 4. tophub.today 触发验证码（2026-06-13 实测）
- tophub.today 有时返回503，重试一次通常能通
- **更常见的情况**：触发安全验证（CAPTCHA），页面显示"安全验证"而非内容
- 验证码无法自动完成，遇到直接放弃TopHub，改用其他来源
- 备选：直接访问各平台官网（见下方"终极备选"）

### 5. 微博API不可用（2026-06-13 实测）
- `weibo.com/ajax/side/hotSearch` 返回 `Forbidden`（需要登录Cookie）
- **正确方式**：访问网页版 `s.weibo.com/top/summary`，用 eval 提取文本
- 命令：`opencli browser <session> open "https://s.weibo.com/top/summary"` → `eval "document.body.innerText"`

### 小红书搜索（找话题真实例子/评论区的终极武器）

当抖音搜索API返回空数据或需要登录时，**小红书搜索是找话题真实例子和评论区反应的最佳来源**：

```bash
opencli xiaohongshu search "关键词" -f json
```

- 返回结构化结果：标题、作者、点赞数、URL
- 可以用返回的URL获取笔记详情和评论区
- 评论区往往有大量真实案例，比自己编的更接地气

**获取笔记详情：**
```bash
opencli xiaohongshu note "完整URL（含xsec_token）" -f json
```

**获取评论区：**
```bash
opencli xiaohongshu comments "完整URL（含xsec_token）" -f json
```

⚠️ 注意：note和comments命令需要完整URL（含xsec_token），不能只传note_id。

**使用场景：**
- 写文案前搜话题真实例子（如搜"膈应式教育"找真实案例）
- 验证选题共鸣度（看点赞/收藏/评论数）
- 找评论区金句（用户真实吐槽比AI写的更有共鸣）

### 终极备选：直接访问各平台官网
当 anysearch 和 TopHub 都不可用时，直接用 OpenCLI 访问：
- 抖音热搜：`opencli browser douyin open "https://www.douyin.com/hot"` → eval
- 微博热搜：`opencli browser <session> open "https://s.weibo.com/top/summary"` → eval
- 这两个是最稳定的来源，不需要任何第三方服务

### anysearch extract 可靠数据源（浏览器都不可用时的终极备选）
当 OpenCLI 和 Camofox 都不可用时，用 `anysearch extract` 直接拉取以下站点：

**抖音热搜榜（结构化表格）：**
```bash
node <skill_dir>/scripts/anysearch_cli.js extract "https://www.abangshou.com/tools/douyin.html"
```
- 返回带热度数值的完整50条热搜表格
- 更新时间显示在页面顶部，可判断数据新旧

**抖音官方热点榜（带指数）：**
```bash
node <skill_dir>/scripts/anysearch_cli.js extract "https://www.o000.ltd/rank/video/officialHot?categoryId=-1&current=1"
```
- 官方热点榜，每条有热度指数（如 1110.8w）
- 适合找高热度话题方向

**微博热搜（通用搜索）：**
```bash
node <skill_dir>/scripts/anysearch_cli.js search "微博热搜榜今日" -m 3 -z cn
```
- 搜索结果中会包含微博热搜的摘要数据

注意：anysearch extract 不需要登录态，不需要浏览器，纯 HTTP 请求，是最稳定的备选方案。

## 选题评分框架（多选题对比）

当用户给出多个候选选题问"哪个好"时，用以下4维度框架快速打分对比（满分100）：

| 维度 | 满分 | 评分标准 |
|------|------|----------|
| 选题热度 | 30 | 微博/抖音热搜排名、多平台讨论量、官媒是否下场 |
| 目标受众共鸣 | 25 | 痛点强度、受众覆盖面、是否"身边小事" |
| 账号定位适配 | 25 | 与当前账号赛道匹配度（如打工人/职场/粤语吐槽） |
| 钩子潜力 | 20 | 能否做出认知冲突式开头（参考视频6"你被骗了"模式） |

**评分后输出格式：**
```
| 排名 | 选题 | 热度 | 共鸣 | 适配 | 钩子 | 总分 | 建议 |
|------|------|------|------|------|------|------|------|
| 🥇 | XXX | 25 | 24 | 23 | 18 | 90 | 强烈推荐 |
| 🥈 | XXX | 22 | 20 | 20 | 16 | 78 | 可以做 |
```

**适配度判断依据（基于账号历史数据）：**
- 职场/打工人话题：视频4(1963)、视频5(1840)、视频8(1628) → 推荐页全部>96%，播放全部>1500，**核心赛道**
- 财经/金融话题：视频7(305) → 推荐页44.4%，**高风险赛道**，必须用强钩子
- 彩礼/社会话题：视频3(503) → 表现一般，**非核心赛道**

**钩子潜力判断：**
- 强钩子（18-20分）：能做"你以为X？其实Y"式认知冲突
- 中钩子（14-17分）：能做对比/反问，但冲突感一般
- 弱钩子（<14分）：平铺直叙，缺乏悬念

**多平台批量扫描技巧（anysearch batch_search）：**
```bash
node <skill_dir>/scripts/anysearch_cli.js batch_search \
  --query "微博热搜今天" \
  --query "百度热搜今天" \
  --query "知乎热榜今天" \
  --query "抖音热搜今天" \
  --query "小红书热搜今天"
```
一次请求扫描5个平台，比逐个tophub快3倍。搜索结果会包含各平台热搜摘要数据。

## 注意
- 热搜热度差不多的条目很多，不要只看前3名，往下多看几条
- 高考等节日性话题，要判断是否已到时效窗口内（如高考6月7号才开始，6月5号不会有跑错考场的热搜）
- 搜出来的结果要核对日期，不要把旧数据当今天的（anysearch可能返回去年内容）
- **先看大盘再看细节，先看今天再下结论** — 用户原话："你应该是看今天的热搜，然后如果看到高考的流量大，再点进去看相关的话题内容"
- **不要预设用户要什么话题** — 用户可能只是说"看看热搜"，不要直接挑几个自认为好的推荐，而是先拉全榜，问用户对哪个有兴趣，或用户说"再找找"继续挖
- **用户说"扫多平台"时才扫多平台** — 如果用户没特别说，默认只看抖音。用户说"都扫一遍看看"时才用 tophub 扫微博、知乎、B站等
