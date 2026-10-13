#!/usr/bin/env python3
"""
语录文件处理脚本：给每条语录加上📋（蓝）和🎙️（黄）交替标记
用法：python3 process_yulu.py [输入文件] [输出文件]
默认：~/Pictures/八字课/语录/理华老师语录.md → 理华老师语录_飞书版.md
"""
import re
import sys

def process_yulu(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    output_lines = []
    item_count = 0
    
    for line in lines:
        # Day标题直接保留，重置计数
        if re.match(r'^## Day', line):
            if item_count > 0:
                output_lines.append('')
            output_lines.append(line)
            output_lines.append('')
            item_count = 0  # 每个Day重新编号
            continue
        
        # 编号条目 (1. 2. 3. 等)
        item_match = re.match(r'^(\d+)[.、．]\s*(.+)$', line)
        if item_match:
            item_count += 1
            if item_count % 2 == 1:
                output_lines.append(f'📋 **语录{item_count}**')
            else:
                output_lines.append(f'🎙️ **语录{item_count}**')
            output_lines.append(item_match.group(2))
            output_lines.append('')
            output_lines.append('---')
            output_lines.append('')
            continue
        
        # 无编号条目（空行后的非标题行）
        if line.strip() and not line.startswith('#') and not line.startswith('---'):
            item_count += 1
            if item_count % 2 == 1:
                output_lines.append(f'📋 **语录{item_count}**')
            else:
                output_lines.append(f'🎙️ **语录{item_count}**')
            output_lines.append(line.strip())
            output_lines.append('')
            output_lines.append('---')
            output_lines.append('')
            continue
        
        # 空行/分隔线 → 跳过
        if not line.strip() or line.strip() == '---':
            continue
        
        # 其他行直接保留
        output_lines.append(line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f'✅ 处理完成: {item_count} 条语录')
    print(f'📁 输出: {output_file}')

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else '/Users/guanmian/Pictures/八字课/语录/理华老师语录.md'
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.md', '_飞书版.md')
    process_yulu(input_file, output_file)
