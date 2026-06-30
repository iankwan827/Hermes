# 批量下载作者主页视频工作流

## 完整流程

### 第一步：从低粉爆款列表提取作者 sec_uid

**方法A：TikHub API**（需余额，$0.009/次）
```bash
curl -X GET "https://api.tikhub.io/api/v1/douyin/web/fetch_one_video?aweme_id=<ID>" \
  -H "Authorization: Bearer $KEY"
# 响应结构: data.aweme_detail.author.sec_uid
```

**方法B：OpenCLI 浏览器桥**（推荐，免费）
```bash
opencli browser default open "https://www.douyin.com/video/<AWEME_ID>"
sleep 4
opencli browser default eval "(async () => {
  const a = window.location.pathname.split('/').pop();
  const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'});
  const d = await r.json();
  const w = d.aweme_detail;
  if (!w) return JSON.stringify({error:1});
  return JSON.stringify({nickname: w.author?.nickname, sec_uid: w.author?.sec_uid});
})()"
```

### 第二步：打开作者主页提取视频列表

```bash
opencli browser default open "https://www.douyin.com/user/<SEC_UID>"
sleep 5
opencli browser default eval "(() => {
  const links = Array.from(document.querySelectorAll('a[href*=\"/video/\"]'));
  const seen = new Set(); const ids = [];
  links.forEach(a => { const m = a.href.match(/\\/video\\/(\\d+)/);
    if (m && !seen.has(m[1])) { seen.add(m[1]); ids.push(m[1]); } });
  return ids.slice(0,20).join(',');
})()"
```

### 第三步：逐个下载视频

```bash
opencli browser default open "https://www.douyin.com/video/<VID>"
sleep 3
DL_URL=$(opencli browser default eval "(async () => {
  const a = window.location.pathname.split('/').pop();
  const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'});
  const d = await r.json();
  const w = d.aweme_detail;
  if (!w) return '';
  return (w.video?.play_addr?.url_list || [])[0] || '';
})()")
curl -s -o "output.mp4" -L "$DL_URL" -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.douyin.com/"
```

## 已验证效果（2026-06-28 国学命理 niche）

| 步骤 | 结果 |
|------|------|
| 搜索API获取低粉爆款 | 90条（172关键词，$2.22） |
| 提取作者sec_uid | 87个唯一作者 |
| 下载5个作者主页视频 | 48个视频 |
| 每个作者约10个视频 | 成功率高 |

## 关键注意事项

1. 视频直链有效期约几分钟，获取后立即下载
2. 每次页面操作间隔3-5秒，避免触发风控
3. Chrome必须运行，OpenCLI Browser Extension必须已连接
4. 不要花时间导出Chrome Cookie——DPAPI解密在Windows上不可靠
5. TikHub fetch_user_post_videos 需要付费余额，免费额度用完返回402
