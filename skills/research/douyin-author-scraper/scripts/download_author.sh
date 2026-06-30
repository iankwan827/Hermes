#!/bin/bash
# 批量下载单个作者的前10个视频
# Usage: bash download_author.sh "sec_uid" "作者昵称"
# 依赖：opencli, curl, stat

SEC_UID="$1"
SAFE_NAME="$2"
OUT="D:/videos/authors/$SAFE_NAME"
mkdir -p "$OUT"

# 1. 打开作者主页（单独调用，不要和 eval 合并）
opencli browser default open "https://www.douyin.com/user/$SEC_UID"
sleep 5

# 2. 提取视频ID列表（单独调用）
video_list=$(opencli browser default eval "(() => {
  const seen = new Set();
  const results = [];
  document.querySelectorAll('a[href*=\"/video/\"]').forEach(a => {
    const m = a.href.match(/\\/video\\/(\\d+)/);
    if (m && !seen.has(m[1])) {
      seen.add(m[1]);
      results.push(m[1]);
    }
  });
  return results.slice(0, 10).join(',');
})()" | tail -1)

if [ -z "$video_list" ]; then
  echo "无视频，跳过"
  exit 0
fi

IFS=',' read -ra ARR <<< "$video_list"
echo "${#ARR[@]} 个视频"

ok=0
for vid in "${ARR[@]}"; do
  target="$OUT/$vid.mp4"
  if [ -f "$target" ]; then echo "$vid 已存在"; ((ok++)); continue; fi

  # 打开视频页（单独调用）
  opencli browser default open "https://www.douyin.com/video/$vid"
  sleep 3

  # 获取下载链接（单独调用，用 tail -1 提取）
  dl_url=$(opencli browser default eval "(async () => {
    const a = window.location.pathname.split('/').pop();
    const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'});
    const d = await r.json();
    const w = d.aweme_detail;
    if (!w) return '';
    return (w.video?.play_addr?.url_list || [])[0] || '';
  })()" | tail -1)

  if [ -n "$dl_url" ] && [[ "$dl_url" == http* ]]; then
    curl -s -o "$target" -L "$dl_url" \
      -H "User-Agent: Mozilla/5.0" \
      -H "Referer: https://www.douyin.com/" \
      --connect-timeout 15 --max-time 120
    size=$(stat -c%s "$target" 2>/dev/null || echo 0)
    if [ "$size" -gt 10000 ]; then
      echo "$vid OK ${size}B"
      ((ok++))
    else
      echo "$vid FAIL ${size}B"
      rm -f "$target"
    fi
  else
    echo "$vid 无下载链接"
  fi
  sleep 1
done

echo "$SAFE_NAME: $ok/${#ARR[@]} done"
