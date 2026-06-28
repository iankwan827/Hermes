# TikHub API 验证记录 (2026-06-28)

## 已验证端点

### 1. 搜索用户（对标账号）
- 端点: POST /api/v1/douyin/search/fetch_user_search
- 参数: {"keyword": "国学 八字", "count": 10}
- 数据结构: data.user_list[].dynamic_patch.raw_data (需JSON.parse)
- user_info 包含: nickname, follower_count, signature

### 2. 搜索视频
- 端点: POST /api/v1/douyin/search/fetch_video_search_v1
- 参数: {"keyword": "八字命理", "count": 20}
- 数据结构: data[].aweme_info
- aweme_info 包含: desc(标题), author.nickname, statistics.digg_count, statistics.comment_count

### 3. 获取用户视频列表
- 端点: GET /api/v1/douyin/web/fetch_user_post_videos
- 参数: sec_user_id, max_cursor, count
- 已验证可用

### 4. 获取垂类内容标签
- 端点: GET /api/v1/douyin/billboard/fetch_content_tag
- 返回: tag_list[].label, tag_list[].value, tag_list[].children[]
- 常用标签: 文化=624, 传统文化=62401, 美食=628, 教育=626

### 5. 低粉爆款榜
- 端点: POST /api/v1/douyin/billboard/fetch_hot_total_low_fan_list
- 参数: {"count": 20, "cursor": 0}
- 响应: data.data.objs[] → {item_id, item_title, nick_name, fans_cnt, like_cnt, play_cnt, item_url}
- ⚠️ 返回全品类低粉爆款（宠物/搞笑/美食等），不支持分类过滤
- tags参数实测无效，对垂类研究（如国学命理）无用
- 对垂类内容研究必须用 fetch_video_search_v1 按关键词搜

## 未验证端点（从OpenAPI schema获取）

### 小红书
- /api/v1/xiaohongshu/web_v3/fetch_search_notes
- /api/v1/xiaohongshu/web_v3/fetch_hot_list
- /api/v1/xiaohongshu/web_v3/fetch_user_info

### 微博
- /api/v1/weibo/web/fetch_hot_search
- /api/v1/weibo/web/fetch_search
- /api/v1/weibo/web/fetch_user_info

## 注意事项

1. 搜索/榜单类端点用POST方法
2. 内容类端点用GET方法
3. 用户搜索返回的数据需要JSON.parse(dynamic_patch.raw_data)才能获取用户信息
4. 视频搜索返回的数据在data[].aweme_info结构中
5. 低粉爆款榜不支持分类过滤，对垂类研究无用
