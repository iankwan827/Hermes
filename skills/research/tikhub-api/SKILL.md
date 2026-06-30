---
name: tikhub-api
description: "TikHub社交媒体数据API。支持抖音/小红书/微博/B站等16个平台的数据爬取。用于热点调研、竞品分析、内容灵感、对标账号搜索。"
triggers:
  - "tikhub"
  - "社交媒体数据"
  - "爬取数据"
  - "API数据"
  - "对标账号"
  - "低粉爆款"
---

# TikHub 社交媒体数据API

## 概述

TikHub是社交媒体数据基础设施平台，提供16个平台1000+个API端点，可爬取抖音、小红书、微博、B站等平台的公开数据。

## 支持的平台

| 平台 | 端点数 | 用途 |
|------|--------|------|
| 抖音（Douyin） | 300 | 视频、用户、评论、搜索、热榜、星图、低粉爆款 |
| 小红书（Red Note） | 61 | 笔记、用户、评论、搜索、热榜 |
| 微博（Weibo） | 64 | 帖子、用户、评论、热搜、搜索 |
| B站（Bilibili） | - | 视频、用户、评论、弹幕、搜索 |
| TikTok, Instagram, YouTube, Twitter/X, 快手, Threads, LinkedIn, Reddit, 微信, Lemon8, 知乎 |

## 认证方式

API Key保存在 `references/api_key.txt`：

```bash
TIKHUB_KEY=$(cat "E:/Users/Administrator/AppData/Local/hermes/skills/research/tikhub-api/references/api_key.txt")
```

```python
key_path = "E:/Users/Administrator/AppData/Local/hermes/skills/research/tikhub-api/references/api_key.txt"
with open(key_path) as f:
    api_key = f.read().strip()
headers = {"Authorization": f"Bearer {api_key}"}
```

**⚠️ Xiaomi MiMo key 故障排查**：见 `references/xiaomi-key-troubleshooting.md`

## Base URL

```
https://api.tikhub.io
```

## ⚠️ 关键发现：端点名称与文档不一致

文档中的端点名称（如 `fetch_hot_search_list`、`fetch_billboard_list`）**不存在**。
正确端点从 OpenAPI schema 获取：`https://api.tikhub.io/openapi.json`（1066个端点）。

**搜索/榜单类端点用POST方法，内容类端点用GET方法。**

## 已验证可用的API端点

### 抖音搜索（POST方法）

```bash
# 搜索用户（对标账号）✅已验证
curl -X POST "https://api.tikhub.io/api/v1/douyin/search/fetch_user_search" \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"keyword":"国学 八字","count":10}'

# ⚠️ 数据结构：用户信息在 dynamic_patch.raw_data.user_info 里
# 需要 JSON.parse(item.dynamic_patch.raw_data) 获取 user_info.nickname, follower_count 等

# 搜索视频 ✅已验证
curl -X POST "https://api.tikhub.io/api/v1/douyin/search/fetch_video_search_v1" \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"keyword":"国学 八字","count":10}'

# ⚠️ 数据结构：视频在 data[].aweme_info 里
# aweme_info.desc = 标题, aweme_info.author.nickname = 作者
```

### 抖音榜单（POST方法）

```bash
# 低粉爆款榜 ✅端点已验证，能返回数据但不支持分类过滤
curl -X POST "https://api.tikhub.io/api/v1/douyin/billboard/fetch_hot_total_low_fan_list" \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"page":1,"page_size":10,"date_window":24,"tags":[{"value":624,"children":[{"value":62401}]}]}'

# 高播放量榜 / 高点赞榜 / 热门账号榜
# fetch_hot_total_high_play_list / fetch_hot_total_high_like_list / fetch_hot_account_list

# ⚠️ 该接口返回全品类低粉爆款，不支持分类过滤！对垂类内容研究无用。
# 实测行为：每次返回约9条，翻页（cursor>0）返回0条，total显示1000但实际拿不到
# tags参数实测无效（传了文化标签也返回宠物/搞笑内容）
# 响应结构：data.data.objs[]，字段：item_title, fans_cnt, like_cnt, play_cnt, nick_name, item_url

# 获取垂类内容标签 ✅已验证
curl -X GET "https://api.tikhub.io/api/v1/douyin/billboard/fetch_content_tag" \
  -H "Authorization: Bearer *** # 常用标签ID：
# 文化: 624, 传统文化: 62401, 武术: 62415, 书法: 62406
# 美食: 628, 教育: 626, 知识: 635
```

### 抖音内容（GET方法）

```bash
# 获取用户发布的视频列表 ✅已验证
curl -X GET "https://api.tikhub.io/api/v1/douyin/web/fetch_user_post_videos?sec_user_id=<ID>&max_cursor=0&count=20" \
  -H "Authorization: Bearer *** # 获取单个视频详情 ✅已验证
# ⚠️ 响应结构：data.aweme_detail.author.sec_uid（不是 data.author）
curl -X GET "https://api.tikhub.io/api/v1/douyin/web/fetch_one_video?aweme_id=<AWEME_ID>" \
  -H "Authorization: Bearer ***"
```

### 小红书（GET方法）

```bash
# 搜索笔记 / 热榜 / 用户信息 / 搜索用户
# /api/v1/xiaohongshu/web_v3/fetch_search_notes
# /api/v1/xiaohongshu/web_v3/fetch_hot_list
# /api/v1/xiaohongshu/web_v3/fetch_user_info
# /api/v1/xiaohongshu/web_v3/fetch_search_users
```

### 微博（GET方法）

```bash
# 热搜 / 搜索 / 用户信息
# /api/v1/weibo/web/fetch_hot_search
# /api/v1/weibo/web/fetch_search
# /api/v1/weibo/web/fetch_user_info
```

## 视频下载工作流（省钱方案）

TikHub API可以获取视频高清下载链接，配合本地curl下载，不用走TikHub的下载接口（每个视频省$0.001）：

```bash
# 第一步：获取视频下载链接 ✅已验证
curl -X GET "https://api.tikhub.io/api/v1/douyin/web/fetch_video_high_quality_play_url?aweme_id=<AWEME_ID>" \
  -H "Authorization: Bearer ***"

# 返回 original_video_url 字段，直接用curl下载
curl -sk -L -o "output.mp4" "<original_video_url>" -H "User-Agent: Mozilla/5.0"
```

**批量下载脚本（Node.js）：**
```javascript
const videos = [{id: 'xxx', title: '视频标题'}, ...];
// 遍历获取URL → curl下载，每次间隔2秒避免限流
```

**⚠️ 注意**：
- 下载链接有时效性，拿到后尽快下载
- 部分视频可能是MOV格式（不是MP4），ffmpeg转码时需注意
- 批量下载每次间隔2-3秒，避免触发限流

低粉爆款榜（`fetch_hot_total_low_fan_list`）需要先获取标签ID：

```bash
# 第一步：获取垂类内容标签
curl -X GET "https://api.tikhub.io/api/v1/douyin/billboard/fetch_content_tag" \
  -H "Authorization: Bearer *** # 第二步：用标签ID查询低粉爆款
curl -X POST "https://api.tikhub.io/api/v1/douyin/billboard/fetch_hot_total_low_fan_list" \
  -H "Authorization: Bearer *** -d '{\"page\":1,\"page_size\":10,\"date_window\":24,\"tags\":[{\"value\":624,\"children\":[{\"value\":62401}]}]}'
```

**⚠️ 该接口返回全品类低粉爆款，不支持分类过滤！对垂类内容研究无用。**

## 使用场景

1. **对标账号搜索**：搜索特定领域的创作者，分析粉丝量、内容风格
2. **低粉爆款发现**：用 `fetch_video_search_v1` 按关键词搜索，筛选粉丝<1万且点赞>1000的视频（billboard接口不支持分类过滤）
3. **视频下载**：获取视频下载链接，配合本地工具下载
4. **热点调研**：获取热榜数据，发现热门话题
5. **内容灵感**：搜索特定话题的热门内容，分析爆款模式
6. **评论分析**：爬取视频/笔记评论，了解用户反馈

## ⚠️ Python环境冲突问题（2026-06-28验证）

**症状**：`AssertionError: SRE module mismatch` 或 `cannot import name 'NamespaceLoader'`

**原因**：系统环境变量 `PYTHONHOME` 指向了 uv 安装的 cpython-3.11，与系统Python冲突

**解决方案**：创建独立venv安装
```bash
# 创建独立环境
uv venv .venv-tikhub --python 3.12
uv pip install --python .venv-tikhub/Scripts/python.exe tikhub

# 使用时加上 PYTHONHOME="" 清除冲突
PYTHONHOME="" .venv-tikhub/Scripts/python.exe -c "import tikhub"
```

**⚠️ 任何Python包安装都可能遇到此问题**，统一用独立venv解决。

## 两个搜索接口的关键区别

### fetch_general_search_v2（综合搜索）
- 每次返回16-17条，支持翻页（offset: 0, 20, 40...）
- 数据量大，适合快速扫内容
- **⚠️ follower_count 始终返回0！** 无法判断粉丝数
- 数据结构：`j.data.business_data[]` → `item.data.aweme_info`

### fetch_video_search_v1（视频搜索）✅ 推荐用于低粉爆款研究
- 每次返回8条，支持翻页（cursor）
- **✅ 返回真实粉丝数**（`author.follower_count`）
- 数据结构：`j.data.data[]` → `item.aweme_info`
- 适合构建低粉爆款库，因为能直接筛选粉丝<1万的视频

**结论**：构建低粉爆款库必须用 `fetch_video_search_v1`，综合搜索接口无法筛选粉丝数。

## 批量搜索构建爆款库（低粉爆款版）

**工作流**：
1. 准备100+关键词（十神、神煞、五行、具体场景、修行/心灵/养生等相邻领域）
2. 用 `fetch_video_search_v1` 逐个搜索，每个关键词翻3页
3. 按 `aweme_id` 去重，保留 `follower_count` 和 `digg_count`
4. 筛选：粉丝<1万 且 点赞>1000 = 低粉爆款
5. 保存为 JSON + Markdown 格式

**脚本位置**：
- v2（30关键词）：`D:/hermes-agent/scripts/tikhub_search_with_fans.js`
- v3（172关键词）：`D:/hermes-agent/scripts/tikhub_search_v3.js`

**已验证效果**：

| 版本 | 关键词数 | 去重视频 | 低粉爆款 | 请求次数 | 花费 |
|------|---------|---------|---------|---------|------|
| v2 | 30 | 206 | 35 | 60 | $0.54 |
| v3 | 172 | 481 | 82 | 247 | $2.22 |

**关键发现**：
- ⚠️ 抖音搜索去重机制：很多关键词第一页7-8条，第二页全是重复
- 每关键词实际新增约7-8条唯一内容
- 172个关键词只搜出481条不重复视频（重叠率高）
- 要凑1000+需要搜更多关键词或换搜法（按作者主页搜）

**用标签反推关键词**：
- 先搜一轮拿到低粉爆款视频
- 提取视频标题中的高频标签（如 #国学文化 #命理八字 #偏印）
- 用这些标签作为下一轮搜索关键词
- 实测：35条低粉爆款提取出96个标签，高频标签可作为第二轮搜索词

**扩大规模方法**：
- 增加关键词数量（100+效果远好于30）
- 加入相邻领域词（修行/禅修/养生/心灵成长/人生感悟）
- 用已搜到的低粉爆款标签反推新关键词
- 按热门作者主页批量搜（fetch_user_post_videos）

**⚠️ fetch_user_post_videos 需要付费余额**：免费额度用完后返回 402（Insufficient balance）。余额不足时无法扒作者主页。替代方案：用 OpenCLI 浏览器桥直接从抖音页面提取，详见 `references/batch-author-download.md`。

**获取作者 sec_uid 方法**：用 `fetch_one_video` 接口，响应结构为 `data.aweme_detail.author.sec_uid`（不是 `data.author`）。⚠️ 每次调用扣费 $0.009（与搜索接口同价），90条视频查作者需 $0.81。

**扩充到1000+的最佳策略**：
1. 先用搜索接口拿到一批低粉爆款（80-100条）
2. 用 `fetch_one_video` 获取每条视频作者的 `sec_uid`（⚠️ $0.009/次）
3. 用 `fetch_user_post_videos` 批量下载每个作者主页所有视频（⚠️ 需付费余额）
4. 从主页视频中筛选低粉爆款
5. 这样绕过搜索接口的去重限制，每个作者可贡献几十条新视频

**⚠️ 首选方案：OpenCLI 浏览器桥下载**（不需要 TikHub 余额）

当 `fetch_user_post_videos` 余额不足时，用 OpenCLI 浏览器桥直接从抖音页面提取视频：
1. 打开作者主页 → 提取视频 ID 列表
2. 打开每个视频页 → 用 `fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/...')` 提取下载链接
3. 用 curl 下载（视频直链有效期约几分钟）
详见 `douyin-download` skill 的「首选方案」章节。

**⚠️ 搜索关键词重叠问题**（2026-06-28验证）：
- 172个关键词只搜出481条不重复视频（重叠率极高）
- 很多关键词第一页7-8条，第二页全是重复（+0）
- 后半段关键词（从第60个开始）几乎全部返回0条新增
- **原因**：抖音搜索结果去重机制，相似关键词返回相同视频

**标签反推关键词法**（2026-06-28验证）：
- 先搜一轮拿到低粉爆款视频（35条以上）
- 提取视频标题中的高频标签（96个标签，TOP: 国学文化10次、命理八字5次、国学智慧4次）
- 用这些高频标签作为下一轮搜索关键词
- 比凭空想关键词更精准

**作者主页批量抓取策略**（2026-06-28验证）：
- 90条低粉爆款中，只有5个作者成功拿到sec_uid（其他返回null bytes）
- 拿到sec_uid的作者：陈愈盛、道法自然794、乾坤书院今道老师、深圳易德文化、高雅兰国学文化
- `fetch_user_post_videos` 需要付费余额，免费额度用完返回402
- **替代方案**：用yt-dlp下载视频时自动获取作者主页URL（需要Cookie）

**详细关键词库和搜索策略**：见 `references/国学命理低粉爆款搜索策略.md`

## ⚠️ TikHub余额不足时的免费替代方案

当TikHub返回402（Insufficient balance）时，以下方法可以免费获取搜索数据：

### 头条搜索（推荐）✅已验证 2026-06-30
头条搜索页面返回的HTML中嵌入了结构化JSON数据，包含新闻标题、摘要、来源等信息。

```javascript
// 用Node.js fetch头条搜索页，解析嵌入的JSON
const https = require('https');
const url = 'https://so.toutiao.com/search/?keyword=搜索关键词';
// 返回的HTML中包含多个JSON对象，提取其中的title/abstract/source字段
// 数据结构：每个结果有 title.text, abstract.text, source, datetime, read_count
```

**优势**：
- 完全免费，无需API Key
- 返回结构化新闻数据（标题、摘要、来源、阅读量）
- 支持中文关键词搜索
- 可获取发布时间和互动数据

**注意**：
- `https://www.toutiao.com/api/search/content/` 接口会被拒绝（shark_decision: reject）
- 必须用搜索页面 `https://so.toutiao.com/search/?keyword=...` 获取数据
- 返回的HTML很大（200KB+），需要从HTML中提取嵌入的JSON块
- 用Node.js的https模块请求，设置正确的User-Agent

### 360搜索
360搜索（so.com）也能返回相关新闻标题，但数据结构化程度不如头条搜索。
- 标题在 `<h3>` 标签中
- 相关搜索词在页面底部

### ⚠️ 本机Python环境冲突
系统Python（uv安装的cpython-3.11）与PYTHONHOME冲突，`python -c "import json"` 都会报 SRE module mismatch。
解决方案：用Node.js处理JSON解析，不要用系统Python。

## 使用原则

1. **先读文档再调接口**：不要盲目试错，先查OpenAPI schema确认端点和参数
2. **能用搜索就不用榜单**：搜索接口更灵活，榜单接口参数复杂
3. **批量操作加间隔**：每次请求间隔1.5-2秒，避免触发限流
4. **下载走本地**：用API获取链接，下载用curl/yt-dlp，省API费用
5. **低粉爆款必须用视频搜索接口**：`fetch_video_search_v1` 才返回真实粉丝数，综合搜索接口粉丝数为0
6. **预算按$0.009/次估算**：视频搜索接口实际扣费比官方表高

## 价格

**⚠️ 实际价格**（2026-06-28验证）：
- 视频搜索接口（fetch_video_search_v1）：**~$0.009/次**
- 综合搜索接口（fetch_general_search_v2）：~$0.001/次
- 低粉爆款榜：~$0.001/次

官方阶梯定价表：

| 日请求量 | 单价 |
|---------|------|
| 0-1,000 | $0.001/次 |
| 1,000-5,000 | $0.0009/次（-10%） |
| 5,000-10,000 | $0.0008/次（-20%） |
| 10,000-20,000 | $0.0007/次（-30%） |
| 20,000-30,000 | $0.0006/次（-40%） |
| 30,000+ | $0.0005/次（-50%） |

- 注册送$0.05免费额度（约50次请求）
- 支持PayPal、支付宝、USDT
- ⚠️ 视频搜索接口实际扣费比官方表高，预算时按$0.009/次估算

## MCP集成

TikHub提供990+个MCP工具，可直接接入AI Agent：
```
https://mcp.tikhub.io/{platform}/mcp
```

## Python SDK

```bash
pip install tikhub
```

GitHub: https://github.com/TikHub/TikHub-API-Python-SDK

## 注意事项

- 只能爬取公开数据
- 遵守GDPR和CCPA
- 默认限速10 RPS，可升级到100+ RPS
- 需要注册账号获取API Key：https://user.tikhub.io/register
- API Key获取：https://user.tikhub.io/dashboard/api
- 从 OpenAPI schema 获取正确端点名：`https://api.tikhub.io/openapi.json`

## 文档

- 完整文档：https://docs.tikhub.io
- Python SDK：https://github.com/TikHub/TikHub-API-Python-SDK
- Discord社区：https://discord.gg/aMEAS8Xsvz
