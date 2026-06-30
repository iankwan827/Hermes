#!/bin/bash
# 批量下载作者视频 - 从文件读取作者列表
# 用法: bash batch_download.sh <authors_file> [start_index]
# authors_file 格式: 每行 "sec_uid|nickname"

OUTPUT_DIR="D:/videos/authors"
AUTHORS_FILE="${1:-D:/hermes-agent/scripts/remaining_authors.txt}"
START="${2:-0}"

if [ ! -f "$AUTHORS_FILE" ]; then
  echo "文件不存在: $AUTHORS_FILE"
  exit 1
fi

total=$(wc -l < "$AUTHORS_FILE")
echo "=== 开始批量下载 === $total 个作者，从第 $((START+1)) 个开始"

count=0
while IFS='|' read -r sec_uid nickname; do
  [ -z "$sec_uid" ] && continue
  ((count++))
  [ "$count" -le "$START" ] && continue

  # 检查已有视频
  safe_name=$(echo "$nickname" | tr '/' '_')
  if [ -d "$OUTPUT_DIR/$safe_name" ]; then
    existing=$(ls "$OUTPUT_DIR/$safe_name/"*.mp4 2>/dev/null | wc -l)
    if [ "$existing" -ge 8 ]; then
      echo "[$count/$total] $nickname - 已有${existing}个，跳过"
      continue
    fi
  fi

  echo ""
  echo "[$count/$total] $nickname"

  # 打开作者主页
  opencli browser default open "https://www.douyin.com/user/$sec_uid" 2>/dev/null
  sleep 5

  # 提取视频ID
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
  })()" 2>/dev/null)

  if [ -z "$video_list" ]; then
    echo "  无视频，跳过"
    continue
  fi

  IFS=',' read -ra vids <<< "$video_list"
  echo "  ${#vids[@]} 个视频"

  mkdir -p "$OUTPUT_DIR/$safe_name"
  dl_ok=0

  for vid in "${vids[@]}"; do
    target="$OUTPUT_DIR/$safe_name/$vid.mp4"
    if [ -f "$target" ]; then ((dl_ok++)); continue; fi

    opencli browser default open "https://www.douyin.com/video/$vid" 2>/dev/null
    sleep 3

    dl_url=$(opencli browser default eval "(async () => {
      const a = window.location.pathname.split('/').pop();
      const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'});
      const d = await r.json();
      const w = d.aweme_detail;
      if (!w) return '';
      return (w.video?.play_addr?.url_list || [])[0] || '';
    })()" 2>/dev/null | tail -1)

    if [ -n "$dl_url" ] && [[ "$dl_url" == http* ]]; then
      curl -s -o "$target" -L "$dl_url" -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.douyin.com/" --connect-timeout 15 --max-time 120
      size=$(stat -c%s "$target" 2>/dev/null || echo 0)
      if [ "$size" -gt 10000 ]; then ((dl_ok++)); else rm -f "$target"; fi
    fi
    sleep 1
  done

  echo "  $nickname: $dl_ok/${#vids[@]} 完成"
done < "$AUTHORS_FILE"

echo ""
echo "=== 全部完成 ==="
