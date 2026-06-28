---
name: topic-ideas
description: |
  选题灵感管理。随时记录、查看、筛选选题。
  触发方式：「记一下选题」「看看选题库」「选题灵感」
  Manage topic ideas — record, view, filter, and track status.
version: 1.2.0
created: 2026-06-21
platforms: [windows]
---

# 选题灵感管理

## 选题库文件

路径：`D:/hermes-agent/文案/`（文案统一存储目录）
命名格式：`YYYY-MM-DD_主题.md`

选题库索引文件：`E:/Users/Administrator/hermes-repo/docs/topic-ideas.md`

## 操作

### 记录新选题

读取选题库文件，在「待定（灵感池）」表格中追加一行：

```
| 日期 | 选题 | 角度 | 状态 | 备注 |
```

状态标记：
- `灵感` — 刚想到，还没细想
- `已定` — 确定要做，角度明确
- `已拍` — 拍完了
- `已发` — 已发布，可记录数据

### 查看选题库

读取选题库文件，按状态分组展示。

### 筛选选题

按状态/关键词筛选。用户说"看看有什么灵感"时展示所有 `灵感` 状态的选题。

### 标记完成

用户说"这个拍了"或"发了"时，更新状态并移到「已拍/已发」表格。

## 热点调研工具

扫热点/热搜时，按优先级使用以下工具：

**快速路径**（30秒出结果）：直接用 codelife.cc 聚合API（见1b），一次curl拿一个平台的完整热搜。不需要OpenCLI、不需要浏览器、不需要登录。

**详细路径**（需要深挖时）：用OpenCLI浏览器打开抖音/小红书，配合vision_analyze分析内容。

### 1. 抖音热搜榜（首选）
```bash
curl -s 'https://www.douyin.com/aweme/v1/web/hot/search/list/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
  -H 'Referer: https://www.douyin.com/' \
  --max-time 15
```
免登录，返回JSON。用node解析 `data.word_list` 数组，取 `word`（话题名）和 `hot_value`（热度值）。label字段：`[1]=新` `[3]=热` `[5]=荐` `[8]=荐` `[16]=科普`。

### 1a. 抖音热搜页（curl API返回空时的备选）
当curl API返回空的`aweme_list`时，用OpenCLI浏览器直接抓取热搜页：
```bash
opencli browser douyin open "https://www.douyin.com/hot"
sleep 3
opencli browser douyin eval "
const allLinks = document.querySelectorAll('a');
const topics = [];
allLinks.forEach(a => {
  const h = a.href || '';
  const t = a.innerText || '';
  if(h.includes('/hot/') && t.length > 3 && t.length < 50) {
    topics.push(t);
  }
});
[...new Set(topics)].join('\\n');
"
```
注意：热搜页显示的是「热点视频」列表，真正的热搜话题藏在`<a href="/hot/...">`链接里。不要用innerText直接提取（会混入视频信息）。

⚠️ 重复eval变量冲突：页面上下文中`const`声明的变量不会被清除，再次eval同名变量会报`SyntaxError: Identifier 'xxx' has already been declared`。解法：每次eval用不同变量名（如第一次`allLinks`，第二次`pageLinks`）。

### 1b. 第三方聚合API（最可靠的备选）
当OpenCLI断连、抖音API返回空、微博被拦截时，用codelife.cc聚合API，**免登录、免浏览器**：
```bash
# 抖音热搜
curl -sk --max-time 10 "https://api.codelife.cc/api/top/list?lang=cn&id=mproPpoq6O" -H "User-Agent: Mozilla/5.0" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const j=JSON.parse(d);(j.data||[]).forEach(i=>console.log(i.index+'. '+i.title+' ('+i.hotValue+')'));})"

# 微博热搜
curl -sk --max-time 10 "https://api.codelife.cc/api/top/list?lang=cn&id=KqndgxeLl9" -H "User-Agent: Mozilla/5.0" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const j=JSON.parse(d);(j.data||[]).forEach(i=>console.log(i.index+'. '+i.title+' ('+i.hotValue+')'));})"

# 知乎热榜
curl -sk --max-time 10 "https://api.codelife.cc/api/top/list?lang=cn&id=74KvxwokxM" -H "User-Agent: Mozilla/5.0" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const j=JSON.parse(d);(j.data||[]).forEach(i=>console.log(i.index+'. '+i.title+' ('+i.hotValue+')'));})"

# 今日头条
curl -sk --max-time 10 "https://api.codelife.cc/api/top/list?lang=cn&id=n/mproPpoq6O" -H "User-Agent: Mozilla/5.0" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const j=JSON.parse(d);(j.data||[]).forEach(i=>console.log(i.index+'. '+i.title+' ('+i.hotValue+')'));})"
```
⚠️ 必须用node解析JSON（python有SRE module mismatch问题）。返回格式：`index`（排名）、`title`（标题）、`hotValue`（热度值）、`link`（微博搜索链接）。这个API是免费第三方聚合，长期可用但偶尔也会挂，挂了换下一个平台试。

### 1c. 今日头条热搜榜（OpenCLI可用时）
```bash
opencli toutiao hot --limit 20
```
返回结构化热搜列表，含rank、title、hot_value、label（new/hot/onSite/refuteRumors）。免登录，直接出结果。注意：toutiao adapter没有搜索功能，只有hot命令。⚠️ 需要Chrome扩展连接，断连时用1b。

### 2. 背景调研（深挖某个话题时）
- **搜狗（首选）**：`https://www.sogou.com/web?query=关键词` — 中文分词准确，能正确处理复合词（如"圣女果"不会拆成"圣女"+"果"）
- **Bing（备选）**：`https://www.bing.com/search?q=关键词` — 英文内容更好，但中文复合词容易误拆
- **百度（不推荐）**：极易触发验证码，curl请求基本会被拦截

### 3. 搜标签（确认话题热度）
用OpenCLI搜抖音话题：`opencli browser default open "https://www.douyin.com/search/关键词"` → 看搜索结果 → 点进视频看标签。不要用 `opencli douyin hashtag search`（走的是creator API，不是抖音主页）。

### 4. 分析搜索结果内容（深挖某个话题时）
打开抖音搜索页后，用vision_analyze读取截图分析热门内容：
```bash
opencli browser default open "https://www.douyin.com/search/关键词"
sleep 5
opencli browser default screenshot "$HOME/topic_search.png"
# 然后用 vision_analyze 读截图，问：列出视频标题、作者、点赞数、内容方向
```
注意：vision_analyze只支持本地文件路径（不支持远程URL），截图保存到本地再读取。

### 5. 小红书灵感搜索（热点不适用时的备选）
当抖音热搜全是新闻/体育/娱乐，不适合「身边小事共鸣」风格时，用小红书搜生活痛点。

#### 方法A：OpenCLI浏览器（推荐，更稳定）
```bash
# 打开小红书搜索页
opencli browser xiaohongshu open "https://www.xiaohongshu.com/search_result?keyword=关键词&type=1"
sleep 4

# 提取搜索结果标题
opencli browser xiaohongshu eval "
const cards = document.querySelectorAll('[class*=\"note\"], [class*=\"card\"], [class*=\"item\"]');
const results = [];
cards.forEach(card => {
  const title = card.querySelector('[class*=\"title\"], [class*=\"desc\"], h3, span');
  if(title && title.innerText && title.innerText.length > 5) {
    results.push(title.innerText.trim());
  }
});
[...new Set(results)].slice(0, 20).join('\\n');
"
```

⚠️ 小红书采集规则：间隔3-8秒随机，每分钟≤5次eval，每5篇暂停10-15秒。

#### 方法B：OpenCLI适配器（备选）
```bash
opencli xiaohongshu search "关键词" --limit 5 -f json
```

#### 常用搜索词方向（按主题分组搜）
**职场/打工人**：打工人、上班、职场、同事、领导、加班、辞职
**社交/人际**：社交累、人际关系、朋友、独处、社恐、尴尬
**生活/中年**：成年人、累、崩溃、心累、内耗、中年
**情绪/吐槽**：怒气、吐槽、生气、发泄、阴阳怪气

#### 搜索策略
1. 先搜大类词（如"打工人"、"社交"、"成年人"），看整体方向
2. 再搜具体痛点词（如"社交疲惫"、"心累"、"职场人际"），找具体角度
3. 每次搜索间隔5-6秒，避免触发限制

#### 结果呈现
搜索结果按主题分组呈现，每组3-5个标题，格式：
```
【主题名】（热度说明）
  · 标题1
  · 标题2
  · 标题3
```

筛选后给用户2-3个方向选项，等用户选定再进dbs-video-workflow。

### 6. 热点故事深挖（用户问"分别是什么故事"时）

**⚠️ 核心限制：codelife.cc API只返回标题+热度，没有文章内容。** 要获取某个话题的详细故事/背景，需要额外搜索。

**深挖优先级（实测可靠性）：**
1. **OpenCLI浏览器（最可靠）**：用Chrome扩展打开百度/搜狗搜索页，eval提取搜索结果摘要。需要Chrome扩展连接。
2. **codelife.cc API返回的link字段**：微博话题有链接（`s.weibo.com/weibo?q=...`），知乎话题有链接（`zhihu.com/question/...`）。但这些链接直接curl会被拦截（403/重定向）。
3. **头条hot event API**：`https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc` 返回的item有`Url`字段可尝试。

**⚠️ 已验证失败的方法（不要浪费时间）：**
- ❌ curl直接抓取百度/搜狗/Bing搜索页 → 返回空或JS代码
- ❌ curl抓取知乎/zhihu文章页 → 403 Forbidden
- ❌ curl抓取微博话题页 → 重定向到登录
- ❌ 头条search API → 返回空数组
- ❌ DuckDuckGo/Google搜索 → 返回空或被拦截
- ❌ 第三方新闻API（vvhan/thepaper等）→ 大部分已失效
- ❌ python解析JSON → SRE module mismatch，import re就崩

**正确流程：**
1. 先用codelife.cc拿到热点标题列表（快速，30秒）
2. 筛选出用户关注的话题（按共鸣/吐槽方向过滤）
3. 如果用户问某个话题的详细故事：
   - **首选**：启动Chrome扩展 → 用OpenCLI搜百度 → eval提取摘要
   - **备选**：如果Chrome不可用，直接告诉用户"这条的详细内容我暂时抓不到，你可以在微博/知乎搜一下关键词"——不要像无头苍蝇一样反复尝试不同API（浪费用户时间）
4. ⚠️ **绝对不要**花超过3次尝试去抓取详细内容。如果前3次都失败，直接告诉用户当前限制。

**用户沟通模板（抓不到详细内容时）：**
```
这条热搜我只能拿到标题（XXX），详细故事暂时抓不到——Chrome扩展没连上。
关键词：「XXX」，你在微博/知乎搜一下就能看到完整故事。
```

### 7. 热点筛选时的用户语言理解

**⚠️ 用户说"前面四个"时，指的是我刚刚筛选出来高亮的那几个话题，不是热点列表的前四名。**

示例：我从50条热搜中筛出4条"跟我们内容方向相关的"，用户说"看看前面四个热点分别是什么故事"——这4条是：
1. 200万粉网红诋毁袁隆平
2. 奔驰取消9万员工年终奖
3. 成龙扑街不断vs周星驰消失七年
4. 央视曝光高考志愿填报咨询陷阱

而不是微博热搜的前4名（韩国淘汰、网红诋毁袁隆平、链博会、黄灿灿通告费）。

**规则：** 用户指"前面/这几个/这几个"时，回溯上下文看我刚刚highlight了哪些，不要默认是列表前N条。

### 8. 角度提案格式
深挖完一个话题后，给用户2-3个角度选项，每个包含：
- **角度名称**（一句话概括核心冲突/笑点）
- **吐槽点**（这个角度好笑在哪）
- **受众共鸣点**（为什么观众会感同身受）

不要直接写终稿，等用户选定角度再进dbs-video-workflow。

## Pitfalls

- 选题库文件在 GitHub 仓库里，改完记得 push 同步
- 记录选题时「角度」列要写清楚，不只是标题（角度是核心，标题可以改）
- 状态是「已定」的选题，备注里要写清楚关键信息（人物、场景、笑点来源）
- OpenCLI搜索小红书的正确语法是 `opencli xiaohongshu search "关键词"`，不是 `opencli search xiaohongshu`（后者会报 unknown command）
- 热搜全是世界杯/股市/娱乐时不要硬凑，直接切小红书搜痛点方向更高效
- OpenCLI浏览器桥接断开时（报BROWSER_CONNECT错误），所有browser命令都会失败。备选方案：用curl模拟手机UA直接抓取移动版网页，再用grep提取正文段落。示例：`curl -sL "https://m.toutiao.com/article/ID/" -H "User-Agent: Mozilla/5.0 (iPhone; ...)" | grep -oP '<p[^>]*>.*?</p>'`
- **热点工具优先级**（实测可靠性排序）：① codelife.cc聚合API（最稳，免登录免浏览器）→ ② OpenCLI douyin/toutiao（需要Chrome扩展）→ ③ 抖音官方curl API（经常返回空）→ ④ 微博官方API（被拦截Forbidden）。优先用①，别在③④上浪费时间。
- **不要用python解析JSON**：当前环境python的SRE module mismatch，import re就崩。解析JSON一律用node。
- **不要反复尝试抓取详细内容**：codelife.cc API只返回标题，没有文章内容。如果前3次尝试（不同方法）都抓不到详细内容，直接告诉用户当前限制+给搜索关键词，不要花20+工具调用反复试——用户会不耐烦。正确做法：坦诚说"这条暂时抓不到详细内容"。
- **用户说"前面/这几个"指的是我刚highlight的话题，不是列表前N条**：回溯上下文确认。

## 内容方向过滤（用户说"看看今天热点"时必须执行）

用户的标准工作流：**记录灵感 → 扫热点 → 定选题 → 开写**

1. 随时记录灵感（状态=灵感）
2. 每天先扫热点/热搜，看有没有能切入的角度
3. 如果热点全是新闻/体育/娱乐（不适合身边小事共鸣），→ 用小红书搜生活痛点找灵感
4. 从灵感池里挑一个跟热点匹配的，或者热点/小红书里找新角度（状态→已定）
5. 确定后走 dbs-video-workflow

用户原话：「明天看完热点再说」——不要催着定选题，等看完热点再决定。
用户原话：「就是没有」——如果用户说没灵感，主动用小红书搜痛点方向，给2-3个选项等用户挑。
