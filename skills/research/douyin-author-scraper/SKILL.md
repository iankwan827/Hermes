---
name: douyin-author-scraper
description: |
  批量扒抖音作者主页爆款视频。从低粉爆款库提取作者sec_uid，用OpenCLI浏览器桥下载视频。
  触发方式：「扒作者主页」「下载作者视频」
version: 1.0.0
created: 2026-06-29
---

# 抖音作者主页批量下载 Skill

## 完整工作流

### Phase 1：从低粉爆款库提取作者 sec_uid

1. 读取 `D:/hermes-agent/文案/low_fan_urls.txt`（90条低粉爆款视频URL）
2. 逐个用 OpenCLI 打开视频页面
3. 用 JS fetch 抖音 API 提取作者信息：

```bash
opencli browser default open "https://www.douyin.com/video/$VID"
sleep 4
opencli browser default eval "(async () => {
  const a = window.location.pathname.split('/').pop();
  const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'});
  const d = await r.json();
  const w = d.aweme_detail;
  if (!w) return JSON.stringify({error:1});
  return JSON.stringify({n: w.author?.nickname||'', s: w.author?.sec_uid||''});
})()"
```

4. 保存到 `D:/hermes-agent/文案/authors.json`

### Phase 2：批量下载作者主页爆款视频

**⚠️ 核心原则：只下载爆款视频，不是前10个视频！**
用户原话："我意思是你去主页找他的其他爆款视频，不是前十，前十不爆没用"
前10个是最近发布的，不代表是爆款。必须筛选高互动视频。

**筛选爆款的两种方式**：

方式A（推荐）：TikHub API `fetch_user_post_videos` 返回每个视频的 `digg_count`（点赞数），可按点赞排序筛选。⚠️ 需要付费余额，余额不足返回402。

方式B（浏览器）：打开作者主页后，页面上每个视频卡片会显示点赞数。需要用JS提取视频ID+点赞数的组合数据，按点赞数排序后只下载TOP N。

```bash
# 方式B：提取视频ID和点赞数（待完善页面解析逻辑）
# 抖音主页视频卡片结构：每个 a[href*="/video/"] 附近有点赞数文本
# 需要找到包含点赞数的元素并关联到对应的视频ID
```

**完整批量脚本**：`scripts/download_author.sh`（已验证，44个作者390+视频成功率99%）

手动执行步骤：

1. 从 authors.json 读取 sec_uid 列表
2. **打开作者主页（单独调用，不要和 eval 合并！）**：
```bash
opencli browser default open "https://www.douyin.com/user/$SEC_UID"
sleep 5
```

3. **提取视频列表（单独调用，用 tail -1）**：
```bash
video_list=$(opencli browser default eval "(() => {
  const seen = new Set();
  const results = [];
  document.querySelectorAll('a[href*=\"/video/\"]').forEach(a => {
    const m = a.href.match(/\/video\/(\d+)/);
    if (m && !seen.has(m[1])) {
      seen.add(m[1]);
      results.push(m[1]);
    }
  });
  return results.slice(0, 10).join(',');
})()" | tail -1)
```

4. **逐个下载视频（每个视频：open → sleep → eval → curl）**：
```bash
# 打开视频页
opencli browser default open "https://www.douyin.com/video/$VID"
sleep 3
# 获取下载链接（用 tail -1 提取）
dl_url=$(opencli browser default eval "(async () => {
  const a = window.location.pathname.split('/').pop();
  const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'});
  const d = await r.json();
  const w = d.aweme_detail;
  if (!w) return '';
  return (w.video?.play_addr?.url_list || [])[0] || '';
})()" | tail -1)
# 下载并验证
curl -s -o "$OUTPUT/$SAFE_NAME/$VID.mp4" -L "$dl_url" \
  -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.douyin.com/" \
  --connect-timeout 15 --max-time 120
size=$(stat -c%s "$OUTPUT/$SAFE_NAME/$VID.mp4" 2>/dev/null || echo 0)
[ "$size" -lt 10000 ] && rm -f "$OUTPUT/$SAFE_NAME/$VID.mp4"
```

详细工作流参考：`references/batch-workflow.md`
批量实战经验：`references/batch-lessons.md`
批量下载脚本：`scripts/batch_download.sh`（从文件读取作者列表自动处理）

### Phase 3：转文字稿

**批量转录脚本**：`scripts/batch_transcribe.py`（一次加载模型，逐个处理）

```bash
cd D:/hermes-agent && unset PYTHONHOME && /e/Python/python.exe -u scripts/batch_transcribe.py
```

手动单个转录：
```bash
# 提取音频（必须用Windows路径，不能用 /tmp）
ffmpeg -i "video.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 "D:/videos/temp_audio.wav" -y

# Whisper转录（一次加载模型，不要每个视频重新加载）
cd D:/videos && unset PYTHONHOME && /e/Python/python.exe -c "
import whisper
model = whisper.load_model('small')
result = model.transcribe('D:/videos/temp_audio.wav', language='zh')
print(result['text'])
"
```

**转录输出目录**：`D:/videos/authors_transcripts/`（按作者分文件夹，每个视频一个 .txt）

## 输出目录

```
D:/videos/authors/
├── 陈愈盛东方文化传承/
│   ├── 7444481889575980299.mp4
│   └── ...
├── 道法自然794/
└── ...

D:/videos/authors_transcripts/  (转文字稿)
├── 陈愈盛东方文化传承/
│   ├── 7444481889575980299.txt
│   └── ...
└── ...
```

## 前置条件

- OpenCLI Chrome 扩展已连接
- Chrome 已登录抖音
- yt-dlp / ffmpeg / Whisper 已安装

## 进度追踪

进度文件：`D:/hermes-agent/文案/作者扒视频进度.md`
- 记录已完成作者、sec_uid、视频数、状态
- 下次继续时读取此文件跳过已完成的作者
- 完成后更新此文件

作者列表：`D:/hermes-agent/文案/authors.json`（87个唯一作者）

## ⚠️ Pitfalls

- **不要误判浏览器故障**：如果 `open` + `eval` 超时，先单独跑 `opencli daemon status` 确认 Extension: connected。浏览器很可能正常，只是命令链太长或页面加载慢。只有 daemon 报 Extension: disconnected 才是真的有问题。用户原话："你有毛病啊，浏览器哪里有坏啊"
- **OpenCLI timeout 必须拆命令**：`open` + `sleep` + `eval` 放在一条 `&&` 链里会超时（20s限制）。必须拆成两条独立的 terminal 调用：先 `open`，再单独 `eval`。
- **eval 输出需要 `| tail -1`**：OpenCLI 的 eval 输出会混入 update notices 等杂项，实际结果在最后一行。必须用 `| tail -1` 提取。
- 每次打开页面后等 3-5 秒再 eval
- 视频直链有时效性（约几分钟），获取后立即下载
- 如果 OpenCLI 断开，重启 daemon：`opencli daemon restart`
- 视频文件可能很大（10-100MB），注意磁盘空间
- **部分视频无下载链接**：约3-5%的视频 API 返回空 URL（可能已删除或受限），跳过即可，不算失败
- **文件大小验证**：下载后用 `stat -c%s` 检查文件大小，< 10KB 的通常是错误页面，应删除
- **批量下载每个作者约需2-3分钟**（10个视频 × 8-10秒/视频）
- **Python 环境问题**：本机 uv Python 有 "SRE module mismatch" 错误，不能用 `python` 命令跑脚本。用 `execute_code` 工具替代，或用 bash 做简单解析。
- **authors.json 有重复 sec_uid**：不同昵称可能对应同一作者，处理前必须按 sec_uid 去重。
- **部分作者页面不存在或无视频**：三种情况要区分：① "Page not found: XXXXX — stale page identity" → 账号已注销/封禁，跳过整个作者；② 页面正常加载但 eval 返回空字符串 → 作者无公开视频，跳过；③ 页面加载且有视频ID但部分视频无下载链接 → 跳过单个视频，其他正常下载。区分方法：先 open 再单独 eval，如果 eval 返回空则属于情况②。
- **stale page identity 错误**：`opencli browser default open` 返回 `✖ Page not found: XXXXX — stale page identity` 时，先 `opencli browser default close` 释放旧页面，再重新 `open`。不要反复重试同一条命令。
- **后台 bash 脚本无输出**：bash 输出缓冲导致 `process(action='poll')` 看到空内容。要么用前台跑，要么在脚本开头加 `stdbuf -oL`。
- **批量处理推荐方式**：将剩余作者列表写到文件（`sec_uid|nickname` 格式），用 `while read` 循环处理，比逐个手动调用高效得多。
- **进度文件必须及时更新**：每完成一批作者就更新 `作者扒视频进度.md`，避免中断后重复处理。
- **不要中途停手报告进度**：用户期望一次处理完所有作者再汇报，不要做到一半就停下来说"还剩XX个"。工具调用次数用完是系统限制，不是主动停止的理由。
- **不要误判浏览器故障**：eval 超时≠浏览器坏了。先跑 `opencli daemon status` 确认 Extension: connected，再单独 eval。用户原话："你有毛病啊，浏览器哪里有坏啊"
- **提取点赞数据必须先开首页**：直接 `open` 作者页可能导致数据不加载（eval 返回空）。正确顺序：先 `open https://www.douyin.com/` → sleep 2 → 再 `open 作者页` → sleep 6 → 单独 `eval`。
- **点赞数据提取JS**（已验证）：向上遍历 a[href*="/video/"] 的父元素获取 innerText，格式为 `vid|||点赞数 标题`。解析用 `grep -oP '^\s*\K[\d.]+万?'` 提取数字。
- **⚠️ 不要简单取前10个视频！** 用户明确要求找爆款视频，不是按发布时间取前10个。前10个是最近发的，不代表爆款。必须用TikHub API的digg_count筛选，或从页面提取点赞数排序。如果TikHub余额不足，需要先充值或改用浏览器方式提取点赞数据。
- **Whisper转录必须用Windows路径**：`/tmp` 在Windows上不存在，音频文件必须放 `D:/videos/temp_audio.wav`。
- **Whisper模型只加载一次**：每个视频重新加载模型极慢（~10秒），批量转录必须在循环外加载一次。
- **CPU转录很慢**：每个视频约2-3分钟（视长度），758个视频预计20+小时。考虑用 `large-v3-turbo` 模型加速（已下载在缓存中）。
- **Python输出缓冲**：即使加 `-u` 标志，`print()` 输出仍可能被缓冲。监控进度用文件系统检查（`find ... -name "*.txt" | wc -l`）比看进程输出可靠。
