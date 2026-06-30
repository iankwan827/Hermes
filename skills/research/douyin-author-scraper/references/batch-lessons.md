# 批量下载工作流 - 实战经验

## 处理了75个作者后的关键发现（87个总数，12个跳过）

### 成功率统计
- 总体下载成功率: ~97%
- 视频API返回空URL: ~3-5%
- 作者页面不存在/无视频: ~14%（87个中12个跳过）

### 已验证的工作模式

**单作者流程（~2-3分钟）**:
1. `opencli browser default open` 作者主页 → sleep 5
2. `opencli browser default eval` 提取视频ID → `| tail -1`
3. 逐个视频: open → sleep 3 → eval下载链接 → curl下载

**批量流程（推荐）**:
1. 用 `execute_code` 从 authors.json 生成去重列表
2. 保存到 `remaining_authors.txt`（格式: `sec_uid|nickname`）
3. 运行 `scripts/batch_download.sh remaining_authors.txt`

### 作者分类

**正常作者**（~85%）: 页面加载正常，有视频列表
**空页面作者**（~10%）: 页面加载但无视频（可能是: 封号、注销、仅直播号）
**失效sec_uid**（~5%）: 返回 "Page not found: XXX — stale page identity"

### 视频下载结果分类

- `OK xxxxB`: 成功下载，文件大小正常
- `EXISTS`: 已下载过，跳过
- `NO_URL`: API返回空链接（视频已删除/受限）
- `FAIL xxxB`: 下载失败或文件太小（<10KB），已删除

### 时间估算
- 单个作者: 2-3分钟（10个视频）
- 全部87个作者: 约4-5小时（含跳过失败的，实际分两天完成）

### 进度追踪
- 进度文件: `D:/hermes-agent/文案/作者扒视频进度.md`
- 每完成一批（~10个作者）就更新一次
- 下次继续时读取进度文件，跳过已完成的

### 常见问题处理

1. **OpenCLI超时**: 拆开 open 和 eval，不要放一条命令链
2. **eval输出混乱**: 用 `| tail -1` 提取最后一行
3. **页面打不开**: 可能是stale page，先 open 百度再 open 目标页
4. **Python环境坏**: 用 execute_code 工具替代 terminal 里的 python 命令
5. **后台脚本无输出**: bash 输出缓冲问题，改用前台跑或 stdbuf

### 爆款视频筛选经验（新）

**核心原则**：只下载爆款视频，不是前10个视频！用户原话："前十不爆没用"

**两种筛选方式**：
1. **TikHub API**：`fetch_user_post_videos` 返回 `digg_count`，可按点赞排序。⚠️ 需要付费余额。
2. **浏览器页面提取**：从作者主页提取视频卡片的点赞数文本。

**浏览器提取点赞数据的JS模式**（已验证）：
```javascript
(() => {
  const results = [];
  document.querySelectorAll('a[href*="/video/"]').forEach(a => {
    const m = a.href.match(/\/video\/(\d+)/);
    if (!m) return;
    const vid = m[1];
    let el = a;
    for (let i = 0; i < 5; i++) {
      el = el.parentElement;
      if (!el) break;
      const text = el.innerText || '';
      if (text.length > 5 && text.length < 300) {
        results.push(vid + '|||' + text.replace(/\n/g, ' ').substring(0, 150));
        break;
      }
    }
  });
  return results.join('\n');
})()
```

**输出格式**：`视频ID|||点赞数 标题`
**筛选阈值**：点赞 > 500（可根据需要调整）

**⚠️ 关键发现**：直接打开作者页可能数据不加载。必须先打开 `https://www.douyin.com/` → sleep 2 → 再打开作者页 → sleep 6 → 单独 eval。

**bash解析点赞数**：
```bash
likes_str=$(echo "$content" | grep -oP '^\s*\K[\d.]+万?')
if echo "$likes_str" | grep -q "万"; then
  likes=$(echo "$likes_str" | sed 's/万//' | awk '{printf "%d", $1 * 10000}')
else
  likes=$(echo "$likes_str" | awk '{printf "%d", $1}')
fi
```

### 转文字稿经验（758个视频）

**环境要求**：
- ffmpeg: 已安装（WinGet路径）
- Whisper: `/e/Python/python.exe` + `whisper` 包
- 模型缓存: `/e/Users/Administrator/.cache/whisper/small.pt`（483MB）

**关键路径问题**：
- ❌ `/tmp/test_audio.wav` → Windows上不存在
- ✅ `D:/videos/temp_audio.wav` → 正确

**性能数据**：
- small模型 CPU: ~2-3分钟/视频（5分钟视频）
- 758个视频: 预计20+小时
- large-v3-turbo模型已下载，可能更快

**批量转录脚本**：`scripts/batch_transcribe.py`
- 一次加载模型，循环处理所有视频
- 输出到 `D:/videos/authors_transcripts/{author}/{vid}.txt`
- 自动跳过已转录的（检查文件存在且非空）

**监控进度**：
```bash
find D:/videos/authors_transcripts -name "*.txt" -size +0c | wc -l  # 成功数
find D:/videos/authors_transcripts -name "*.txt" | wc -l  # 总数（含空）
```
