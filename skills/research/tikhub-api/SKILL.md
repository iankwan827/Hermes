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

# ⚠️ 该接口返回全品类低粉爆款，不支持按分类/关键词过滤
# 传tags参数也无法过滤垂类内容（实测无效）
# 响应结构：data.data.objs[]，字段：item_title, fans_cnt, like_cnt, play_cnt, nick_name, item_url
# 对垂类研究（如国学命理）无用，必须用 fetch_video_search_v1 按关键词搜

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
  -H "Authorization: Bearer *** # 获取单个视频详情 / 弹幕 / 推荐流 / 相关视频
# fetch_one_video / fetch_one_video_danmaku / fetch_home_feed / fetch_related_posts
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
1. 准备30+关键词（十神、神煞、五行、具体场景等）
2. 用 `fetch_video_search_v1` 逐个搜索，每个关键词翻5页
3. 按 `aweme_id` 去重，保留 `follower_count` 和 `digg_count`
4. 筛选：粉丝<1万 且 点赞>1000 = 低粉爆款
5. 保存为 JSON + Markdown 格式

**脚本位置**：`D:/hermes-agent/scripts/tikhub_search_with_fans.js`

**已验证效果**：
- 30个关键词 × 5页上限 = 206条去重视频，35条低粉爆款
- 花费：$0.54（60次请求，很多关键词第2页无新结果自动停止）
- ⚠️ 抖音搜索去重机制：很多关键词第一页7-8条，第二页全是重复
- 每关键词实际新增约7-8条唯一内容

**扩大规模方法**：
- 增加关键词数量（具体十神组合、具体神煞名、具体场景词）
- 搜索结果每关键词约7-8条唯一内容

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
