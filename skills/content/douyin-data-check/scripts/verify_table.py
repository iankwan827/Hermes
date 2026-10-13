#!/usr/bin/env python3
"""发展日志主表统计复算（douyin-data-check 审核任务用）。

用法: python3 verify_table.py [发展日志.md 路径]
不传路径时按 mtime 自动定位三份候选中的主日志。

核心逻辑源自 2026-10-12 审核会话中实测通过的 heredoc 脚本，
改为直接解析 markdown 表格。解析不出的行会计数并告警，不静默跳过。
"""
import re
import sys
import statistics
from pathlib import Path

CANDIDATES = [
    Path.home() / ".hermes/skills/content/douyin-data-check/references/发展日志.md",
    Path.home() / ".hermes/profiles/main/skills/content/douyin-data-check/references/发展日志.md",
    Path.home() / ".hermes/profiles/main/skills/douyin-data-check/references/发展日志.md",
]

ROW_RE = re.compile(
    r"^\|?\s*V(\d+)\s*\|"          # | V28 |
)


def pick_log():
    existing = [p for p in CANDIDATES if p.exists()]
    if not existing:
        sys.exit("未找到任何发展日志候选文件")
    return max(existing, key=lambda p: p.stat().st_mtime)


def parse_num(s):
    s = s.strip().replace("%", "").replace(",", "")
    return float(s)


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else pick_log()
    rows, skipped = [], 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not ROW_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # 期望: V# | 标题 | 发布时间 | 播放 | 完播率 | 5s完播率 | 2s跳出率 | 平均播放时长 | 点赞 | 评论 | 分享 | 收藏 | 状态
        if len(cells) < 13:
            skipped += 1
            continue
        try:
            rows.append(dict(
                v=cells[0],
                play=int(parse_num(cells[3])),
                fin=parse_num(cells[4]),
                s5=parse_num(cells[5]),
                b2=parse_num(cells[6]),
                like=int(parse_num(cells[8])),
                cm=int(parse_num(cells[9])),
            ))
        except ValueError:
            skipped += 1

    if not rows:
        sys.exit("表格解析失败：0 行")
    plays = [r["play"] for r in rows]
    print(f"日志: {path}")
    print(f"N={len(rows)}  合计={sum(plays)}  均值={sum(plays)/len(rows):.2f}  "
          f"中位数={statistics.median(plays)}  最大={max(plays)}  最小={min(plays)}")
    print(f"点赞之和={sum(r['like'] for r in rows)}  "
          f"评论之和={sum(r['cm'] for r in rows)}")
    if skipped:
        print(f"⚠️ 解析失败/跳过行数={skipped}（表格格式可能有变，检查列数）")

    viol = []
    for r in rows:
        for k in ("fin", "s5", "b2"):
            if not 0 <= r[k] <= 100:
                viol.append((r["v"], f"{k}超范围 {r[k]}"))
        if r["s5"] < r["fin"]:
            viol.append((r["v"], f"5s完播率{s5_fmt(r)}<完播率{fin_fmt(r)}"))
        if r["fin"] + r["b2"] > 100.01:
            viol.append((r["v"], f"完播率+2s跳出率={r['fin']+r['b2']:.2f}>100"))
    print("自洽性违例:", viol if viol else "无 ✅")

    print(f"完播率<10%: {sum(1 for r in rows if r['fin'] < 10)}/{len(rows)}")
    print("5s完播率>=50%:", [r["v"] for r in rows if r["s5"] >= 50])
    print("2s跳出率>30%:", [r["v"] for r in rows if r["b2"] > 30])
    excl_v19 = [r for r in rows if r["play"] >= 100]  # 小样本剔除
    print(f"点赞率<1%（play>=100）: {sum(1 for r in excl_v19 if r['like']/r['play'] < 0.01)}/{len(excl_v19)}")
    print(f"评论率<0.3%: {sum(1 for r in rows if r['cm']/r['play'] < 0.003)}/{len(rows)}")
    print(f"系统均值: 完播率={sum(r['fin'] for r in rows)/len(rows):.2f}%  "
          f"5s完播率={sum(r['s5'] for r in rows)/len(rows):.2f}%")


def s5_fmt(r):
    return f"{r['s5']}%"


def fin_fmt(r):
    return f"{r['fin']}%"


if __name__ == "__main__":
    main()
