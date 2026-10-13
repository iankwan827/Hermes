#!/usr/bin/env python3
"""
抖音发展日志自动校验脚本
用法: python verify_development_log.py <发展日志路径>

功能:
1. 解析数据记录表，提取每个视频的最新值
2. 解析更新日志，找到每个指标的最新更新
3. 对比表格值 vs 更新日志最新值
4. 检查评论/分享互换
5. 检查优化分组表成员
6. 计算均值/中位数并对比
7. 输出结构化校验报告

输出: JSON格式的校验结果
"""

import re
import sys
import json
from collections import OrderedDict


def parse_table(log_content):
    """解析数据记录表，返回视频数据字典"""
    videos = OrderedDict()
    # 匹配表格行: | V28 | 标题 | 时间 | 播放量 | 完播率 | 5s完播率 | 2s跳出率 | 平均播放时长 | 点赞 | 评论 | 分享 | 收藏 | 状态 |
    pattern = r'\|\s*(V\d+)\s*\|[^|]+\|\s*([^|]+)\|\s*([\d,]+)\s*\|\s*([\d.]+%?)\s*\|\s*([\d.]+%?)\s*\|\s*([\d.]+%?)\s*\|\s*([^|]+)\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+)\|'
    
    for match in re.finditer(pattern, log_content):
        vid = match.group(1)
        plays = int(match.group(3).replace(',', ''))
        comp = float(match.group(4).replace('%', ''))
        fives = float(match.group(5).replace('%', ''))
        twos = float(match.group(6).replace('%', ''))
        likes = int(match.group(8))
        comments = int(match.group(9))
        shares = int(match.group(10))
        fav = int(match.group(11))
        
        videos[vid] = {
            'plays': plays,
            'comp': comp,
            'fives': fives,
            'twos': twos,
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'fav': fav,
        }
    
    return videos


def parse_update_log(log_content):
    """解析更新日志，找到每个视频每个指标的最新值"""
    latest = {}
    
    for line in log_content.split('\n'):
        if '定时数据更新' not in line and '定时数据检查' not in line:
            continue
        
        # 提取每个视频的更新
        for vid_match in re.finditer(r'(V\d+)', line):
            vid = vid_match.group(1)
            if vid not in latest:
                latest[vid] = {}
            
            # 提取播放量更新
            play_match = re.search(rf'{vid}播放([\d,]+)→([\d,]+)', line)
            if play_match:
                latest[vid]['plays'] = int(play_match.group(2).replace(',', ''))
            
            # 提取完播率更新
            comp_match = re.search(rf'{vid}[^完]*?完播率([\d.]+%)→([\d.]+%)', line)
            if comp_match:
                latest[vid]['comp'] = float(comp_match.group(2).replace('%', ''))
            
            # 提取5s完播率更新
            fives_match = re.search(rf'{vid}[^5]*?5s完播率([\d.]+%)→([\d.]+%)', line)
            if fives_match:
                latest[vid]['fives'] = float(fives_match.group(2).replace('%', ''))
            
            # 提取2s跳出率更新
            twos_match = re.search(rf'{vid}[^2]*?2s跳出率([\d.]+%)→([\d.]+%)', line)
            if twos_match:
                latest[vid]['twos'] = float(twos_match.group(2).replace('%', ''))
    
    return latest


def check_comment_share_swap(videos):
    """检查评论/分享互换问题"""
    issues = []
    for vid, data in videos.items():
        if data['comments'] == 0 and data['shares'] == 0:
            continue
        if data['comments'] == data['shares'] and data['comments'] > 0:
            issues.append({
                'video': vid,
                'type': 'comment_share_equal',
                'detail': f'评论={data["comments"]}, 分享={data["shares"]}',
                'note': '评论和分享相等，可能是互换，需人工确认'
            })
    return issues


def check_range_and_consistency(videos):
    """检查指标范围和内部一致性（2026-07-24新增）"""
    issues = []
    for vid, data in videos.items():
        # 1. 所有比率必须在0-100%范围
        for metric in ['comp', 'fives', 'twos']:
            val = data[metric]
            if val < 0 or val > 100:
                issues.append({'video': vid, 'type': 'out_of_range',
                    'detail': f'{metric}={val}%', 'severity': 'error'})
        
        # 2. 5s完播率 >= 完播率（逻辑约束）
        if data['fives'] < data['comp']:
            issues.append({'video': vid, 'type': '5s_lt_comp',
                'detail': f'5s={data["fives"]}% < comp={data["comp"]}%', 'severity': 'error'})
        
        # 3. 完播率 + 2s跳出率 <= 100%（逻辑约束）
        total = data['comp'] + data['twos']
        if total > 100:
            issues.append({'video': vid, 'type': 'comp_plus_2s_gt_100',
                'detail': f'comp={data["comp"]}% + 2s={data["twos"]}% = {total}%', 'severity': 'error'})
        
        # 4. 记录计算出的点赞率/评论率供比对
        if data['plays'] > 0:
            data['calc_like_rate'] = round(data['likes'] / data['plays'] * 100, 2)
            data['calc_comment_rate'] = round(data['comments'] / data['plays'] * 100, 3)
    
    return issues


def check_optimization_groups(videos):
    """检查优化分组表成员"""
    groups = {
        '5s>50%_comp<3%': [],
        '5s<50%': [],
        '2s>30%': [],
        'likes_rate<1%': [],
        'comment_rate<0.3%': [],
    }
    
    for vid, data in videos.items():
        likes_rate = data['likes'] / data['plays'] * 100 if data['plays'] > 0 else 0
        comment_rate = data['comments'] / data['plays'] * 100 if data['plays'] > 0 else 0
        
        if data['fives'] > 50 and data['comp'] < 3:
            groups['5s>50%_comp<3%'].append(vid)
        if data['fives'] < 50:
            groups['5s<50%'].append(vid)
        if data['twos'] > 30:
            groups['2s>30%'].append(vid)
        if likes_rate < 1:
            groups['likes_rate<1%'].append(vid)
        if comment_rate < 0.3:
            groups['comment_rate<0.3%'].append(vid)
    
    return groups


def verify_stats(videos):
    """验证均值和中位数"""
    plays = sorted([d['plays'] for d in videos.values()])
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
        print("用法: python verify_development_log.py <发展日志路径>")
        sys.exit(1)
    
    log_path = sys.argv[1]
    
    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析表格
    table_videos = parse_table(content)
    
    # 解析更新日志
    log_latest = parse_update_log(content)
    
    # 对比表格 vs 更新日志
    desync = []
    for vid in table_videos:
        if vid in log_latest:
            for field in ['plays', 'comp', 'fives', 'twos']:
                if field in log_latest[vid]:
                    table_val = table_videos[vid][field]
                    log_val = log_latest[vid][field]
                    if isinstance(table_val, float):
                        diff = abs(table_val - log_val)
                    else:
                        diff = abs(table_val - log_val)
                    if diff > 0.001:
                        desync.append({
                            'video': vid,
                            'field': field,
                            'table': table_val,
                            'log_latest': log_val,
                            'diff': round(diff, 4) if isinstance(diff, float) else diff
                        })
    
    # 检查评论/分享
    cs_issues = check_comment_share_swap(table_videos)
    
    # 检查范围和一致性
    rc_issues = check_range_and_consistency(table_videos)
    
    # 检查优化分组
    groups = check_optimization_groups(table_videos)
    
    # 验证统计
    stats = verify_stats(table_videos)
    
    # 输出报告
    report = {
        'video_count': len(table_videos),
        'stats': stats,
        'table_vs_log_desync': desync,
        'comment_share_issues': cs_issues,
        'range_consistency_issues': rc_issues,
        'optimization_groups': {k: v for k, v in groups.items()},
    }
    
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
