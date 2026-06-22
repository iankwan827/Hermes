---
name: topic-ideas
description: |
  选题灵感管理。随时记录、查看、筛选选题。
  触发方式：「记一下选题」「看看选题库」「选题灵感」
  Manage topic ideas — record, view, filter, and track status.
version: 1.1.0
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

### 1. 抖音热搜榜（首选）
```bash
curl -s 'https://www.douyin.com/aweme/v1/web/hot/search/list/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
  -H 'Referer: https://www.douyin.com/' \
  --max-time 15
```
免登录，返回JSON。用node解析 `data.word_list` 数组，取 `word`（话题名）和 `hot_value`（热度值）。label字段：`[1]=新` `[3]=热` `[5]=荐` `[8]=荐` `[16]=科普`。

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

### 5. 角度提案格式
深挖完一个话题后，给用户2-3个角度选项，每个包含：
- **角度名称**（一句话概括核心冲突/笑点）
- **吐槽点**（这个角度好笑在哪）
- **受众共鸣点**（为什么观众会感同身受）

不要直接写终稿，等用户选定角度再进dbs-video-workflow。

## Pitfalls

- 选题库文件在 GitHub 仓库里，改完记得 push 同步
- 记录选题时「角度」列要写清楚，不只是标题（角度是核心，标题可以改）
- 状态是「已定」的选题，备注里要写清楚关键信息（人物、场景、笑点来源）

## 选题决策流程

用户的标准工作流：**记录灵感 → 扫热点 → 定选题 → 开写**

1. 随时记录灵感（状态=灵感）
2. 每天先扫热点/热搜，看有没有能切入的角度
3. 从灵感池里挑一个跟热点匹配的，或者热点里找新角度（状态→已定）
4. 确定后走 dbs-video-workflow

用户原话："明天看完热点再说"——不要催着定选题，等看完热点再决定。
