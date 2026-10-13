#!/usr/bin/env python3
"""
抖音实时数据与发展日志对比脚本
用法: python compare_live_with_log.py <发展日志路径> [live_data_json]

功能:
1. 解析发展日志中的数据记录表
2. 接收实时页面数据（JSON格式或从stdin读取）
3. 逐字段对比，找出所有差异
4. 特别检查评论/分享互换
5. 输出差异报告和建议修复

输出: JSON格式的差异报告

live_data_json 格式:
{
  "V28": {"plays": 368, "comp": "0.28%", "5s": "14.95%", "2s": "51.03%", "likes": 0, "comments": 0, "shares": 0, "saves": 0},
  "V27": {"plays": 506, "comp": "9.59%", "5s": "46.74%", "2s": "26.82%", "likes": 3, "comments": 0, "shares": 0, "saves": 0},
  ...
}

注意: live数据中 comments/shares 的顺序是页面cells[10]=评论, cells[9]=分享
      日志表格中是: 评论, 分享
"""

import re
import sys
import json
from collections import OrderedDict


def parse_log_table(log_content):
    """解析发展日志中的数据记录表，返回视频数据字典"""
    videos = OrderedDict()
    # 匹配表格行
    pattern = r'\|\s*(V\d+)\s*\|[^|]+\|\s*([^|]+)\|\s*([\d,]+)\s*\|\s*([\d.]+%?)\s*\|\s*([\d.]+%?)\s*\|\s*([\d.]+%?)\s*\|\s*([^|]+)\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+)\|'
    
    for match in re.finditer(pattern, log_content):
        vid = match.group(1)
        plays = int(match.group(3).replace(',', ''))
        comp = match.group(4).strip()
        fives = match.group(5).strip()
        twos = match.group(6).strip()
        avg_dur = match.group(7).strip()
        likes = int(match.group(8))
        comments = int(match.group(9))
        shares = int(match.group(10))
        saves = int(match.group(11))
        status = match.group(12).strip()
        
        videos[vid] = {
            'plays': plays,
            'comp': comp,
            '5s': fives,
            '2s': twos,
            'avg_dur': avg_dur,
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'saves': saves,
            'status': status,
        }
    
    return videos


def parse_rate(rate_str):
    """解析率值字符串，返回浮点数"""
    return float(rate_str.replace('%', ''))


def compare_videos(log_data, live_data):
    """对比日志数据和实时数据，返回差异列表"""
    discrepancies = []
    
    for vid in sorted(live_data.keys(), key=lambda x: int(x[1:])):
        if vid not in log_data:
            discrepancies.append({
                'video': vid,
                'issues': [f'日志中不存在该视频']
            })
            continue
        
        live = live_data[vid]
        log = log_data[vid]
        issues = []
        
        # 对比播放量
        if live['plays'] != log['plays']:
            issues.append(f"播放量: live={live['plays']} log={log['plays']}")
        
        # 对比率值（需要解析百分比字符串）
        for field, key in [('comp', 'comp'), ('5s', '5s'), ('2s', '2s')]:
            live_val = parse_rate(live[field])
            log_val = parse_rate(log[field])
            if abs(live_val - log_val) > 0.001:
                issues.append(f"{field}: live={live[field]} log={log[field]}")
        
        # 对比互动数据
        for field in ['likes', 'comments', 'shares', 'saves']:
            if live[field] != log[field]:
                issues.append(f"{field}: live={live[field]} log={log[field]}")
        
        # 特别检查评论/分享互换
        if live['comments'] != log['comments'] or live['shares'] != log['shares']:
            if live['comments'] == log['shares'] and live['shares'] == log['comments']:
                issues.append(f"⚠️ 评论/分享互换! live:评论={live['comments']}/分享={live['shares']} log:评论={log['comments']}/分享={log['shares']}")
        
        if issues:
            discrepancies.append({
                'video': vid,
                'issues': issues
            })
    
    return discrepancies


def generate_fix_suggestions(discrepancies, live_data, log_data):
    """根据差异生成修复建议"""
    suggestions = []
    
    for d in discrepancies:
        vid = d['video']
        if vid not in live_data or vid not in log_data:
            continue
        
        live = live_data[vid]
        log = log_data[vid]
        
        # 生成表格行替换建议
        old_parts = []
        new_parts = []
        
        if live['plays'] != log['plays']:
            old_parts.append(str(log['plays']))
            new_parts.append(str(live['plays']))
        
        for field, key in [('comp', 'comp'), ('5s', '5s'), ('2s', '2s')]:
            if parse_rate(live[field]) != parse_rate(log[field]):
                old_parts.append(log[field])
                new_parts.append(live[field])
        
        for field in ['likes', 'comments', 'shares', 'saves']:
            if live[field] != log[field]:
                old_parts.append(str(log[field]))
                new_parts.append(str(live[field]))
        
        if old_parts and new_parts:
            suggestions.append({
                'video': vid,
                'old_values': old_parts,
                'new_values': new_parts,
            })
    
    return suggestions


def calculate_stats(log_data):
    """计算统计数据"""
    plays = sorted([d['plays'] for d in log_data.values()])
    n = len(plays)
    total = sum(plays)
    mean = total / n
    
    if n % 2 == 1:
        median = plays[n // 2]
    else:
        median = (plays[n // 2 - 1] + plays[n // 2]) / 2
    
    return {
        'count': n,
        'total': total,
        'mean': round(mean, 2),
        'median': median,
        'min': plays[0],
        'max': plays[-1],
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python compare_live_with_log.py <发展日志路径> [live_data_json]")
        print("  live_data_json: JSON文件路径，或从stdin读取")
        sys.exit(1)
    
    log_path = sys.argv[1]
    
    # 读取日志
    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()
    
    # 解析日志表格
    log_data = parse_log_table(log_content)
    
    # 读取实时数据
    if len(sys.argv) >= 3:
        live_path = sys.argv[2]
        with open(live_path, 'r', encoding='utf-8') as f:
            live_data = json.load(f)
    else:
        live_data = json.load(sys.stdin)
    
    # 对比
    discrepancies = compare_videos(log_data, live_data)
    
    # 生成修复建议
    suggestions = generate_fix_suggestions(discrepancies, live_data, log_data)
    
    # 计算统计
    log_stats = calculate_stats(log_data)
    live_stats = calculate_stats(live_data)
    
    # 输出报告
    report = {
        'log_video_count': len(log_data),
        'live_video_count': len(live_data),
        'log_stats': log_stats,
        'live_stats': live_stats,
        'discrepancy_count': len(discrepancies),
        'discrepancies': discrepancies,
        'fix_suggestions': suggestions,
    }
    
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
