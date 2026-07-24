#!/usr/bin/env python3
"""
验证发展日志表格行与页面数据的评论/分享列是否一致。

用法:
  python verify_comments_shares.py <发展日志路径> [页面数据JSON]

示例 (cron job中):
  python verify_comments_shares.py 发展日志.md '{
    "V21": {"comments": 1, "shares": 0},
    "V20": {"comments": 3, "shares": 0}
  }'

列映射（数据中心→发展日志）:
  页面cells: 点赞[8] → 分享[9] → 评论[10] → 收藏[11]
  日志列:   点赞 → 评论 → 分享 → 收藏
  ⚠️ 评论和分享的顺序是反的！
"""
import json
import sys

def parse_table_row(line):
    """从表格行解析各列值"""
    cells = [c.strip() for c in line.split('|') if c.strip()]
    if len(cells) < 12:
        return None
    try:
        vid = cells[0]
        likes = int(cells[8].replace(',', ''))
        comments = int(cells[9].replace(',', ''))
        shares = int(cells[10].replace(',', ''))
        fav = int(cells[11].replace(',', ''))
        return {'vid': vid, 'likes': likes, 'comments': comments, 'shares': shares, 'fav': fav}
    except (ValueError, IndexError):
        return None

def verify(path, page_data=None):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 找表格行
    table_rows = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('| V') and '已完成' in stripped:
            parsed = parse_table_row(stripped)
            if parsed:
                table_rows.append(parsed)

    print(f"找到 {len(table_rows)} 行视频数据\n")

    issues = []
    for row in table_rows:
        vid = row['vid']
        if page_data and vid in page_data:
            pd = page_data[vid]
            # 页面: comments=cells[10], shares=cells[9]
            # 日志: comments=cells[9], shares=cells[10]
            page_comments = pd.get('comments', '?')
            page_shares = pd.get('shares', '?')

            if page_comments != '?' and page_shares != '?':
                log_comments = row['comments']
                log_shares = row['shares']

                if log_comments != page_comments or log_shares != page_shares:
                    issues.append(vid)
                    print(f"❌ {vid}: 日志评论={log_comments}/分享={log_shares} ≠ 页面评论={page_comments}/分享={page_shares}")
                else:
                    print(f"✅ {vid}: 评论={log_comments} 分享={log_shares} 一致")
        else:
            # 无页面数据时只打印
            if row['comments'] > 0 or row['shares'] > 0:
                print(f"  {vid}: 评论={row['comments']} 分享={row['shares']} (需人工核对)")

    print()
    if issues:
        print(f"❌ 发现 {len(issues)} 处评论/分享互换: {', '.join(issues)}")
        print("请用patch修正后再grep验证")
        sys.exit(1)
    else:
        print("✅ 所有核对通过" if page_data else "⚠️ 无页面数据，仅打印非零行供人工核对")
        sys.exit(0)

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'E:/Users/Administrator/AppData/Local/hermes/skills/content/douyin-data-check/references/发展日志.md'
    page_data = None
    if len(sys.argv) > 2:
        page_data = json.loads(sys.argv[2])
    verify(path, page_data)
