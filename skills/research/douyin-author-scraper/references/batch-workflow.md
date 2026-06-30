# 批量下载工作流

## 流程（每个作者约2-3分钟）

```
for each author in authors.json (skip completed):
  1. open page → sleep 5 → eval video IDs (SEPARATE calls!)
  2. for each video ID:
     a. open video page → sleep 3
     b. eval download URL (SEPARATE call, | tail -1)
     c. curl download → validate size > 10KB
  3. update progress file
```

## 关键模式

### OpenCLI 调用必须拆开
```bash
# ❌ 会超时
opencli browser default open "$URL" && sleep 5 && opencli browser default eval "..."

# ✅ 分两次调用
opencli browser default open "$URL"
sleep 5
opencli browser default eval "..." | tail -1
```

### eval 输出提取
```bash
# OpenCLI 输出混合了 update notices，实际结果在最后一行
result=$(opencli browser default eval "..." | tail -1)
```

### 文件大小验证
```bash
size=$(stat -c%s "$target" 2>/dev/null || echo 0)
if [ "$size" -gt 10000 ]; then
  echo "OK"
else
  rm -f "$target"  # 删除错误页面
fi
```

## 进度追踪
- 文件：`D:/hermes-agent/文案/作者扒视频进度.md`
- 记录：已完成作者数/总数、每个作者的sec_uid和状态
- 下次继续时读取此文件跳过已完成的

## 性能数据（实测）
- 44个作者 × 10视频 = 440个视频
- 总耗时约 2-3 小时
- 成功率约 99%（6个视频无下载链接）
- 每个作者平均 2-3 分钟
