#!/usr/bin/env python3
"""
语录文件处理：每个Day一个颜色（奇数蓝/偶数黄），编号从1开始
对没有编号的Day，按句号+话题关键词自动拆分成独立条目

用法：python3 process_yulu_feishu.py [输入文件] [输出文件]
默认：输入=理华老师语录.md，输出=理华老师语录_飞书版.md
"""
import re
import sys
import os

DEFAULT_INPUT = os.path.expanduser("~/Pictures/八字课/语录/理华老师语录.md")
DEFAULT_OUTPUT = os.path.expanduser("~/Pictures/八字课/语录/理华老师语录_飞书版.md")

# 话题起始关键词（出现在句号后面说明是新条目）
TOPIC_STARTERS = [
    '七杀', '偏印', '伤官', '食神', '比劫', '比肩', '劫财',
    '正印', '正官', '正财', '偏财', '官杀', '印星', '食伤',
    '枭印', '枭神', '财星', '丁火', '甲木', '癸水',
    '地支', '天干', '桃花', '辰戌', '卯酉', '寅申',
    '追偏印', '身弱', '身强', '十神', '一个驿马', '两个驿马',
    '三个驿马', '四个驿马', '命带', '没有驿马', '偏枯', '木代表',
    '语言和', '2026', '高层次', '普通人', '真正', '格局', '看财运',
    '官杀旺', '伤官如果', '伤官，', '伤官的人', '伤官女',
    '比劫的人', '比肩一般', '比劫，', '比劫太旺',
    '印旺的人', '印星太旺', '印星的人', '印星代表',
    '食伤喜欢', '食伤制', '食伤女', '食伤泄秀',
    '财生官', '财星女', '枭印的', '枭印为忌',
    '正印的', '正印比较', '正印能够',
    '官杀为用', '官杀的人', '官杀为忌', '官杀属于',
    '七杀得', '七杀偏印', '七杀正官', '七杀不会',
    '丁火恋', '丁火就像',
    '偏印谈恋爱', '偏印的人', '偏印喜欢', '偏印容易',
    '大食伤', '大伤官',
    '八字偏枯', '火木伤官', '一片伤官', '伤官见官',
    '癸水丁火', '子平先生', '从事一些', '凡大富贵', '伤官穿',
    '枭神', '伤官旺', '伤官崇尚', '伤官的聪明', '伤官是聪明',
    '月支七杀', '伤官七杀', '伤官的人报复', '伤官的人头脑',
    '伤食泄秀', '身财两旺', '一个人命里', '正印的人一般',
    '官印类型', '关于劫财', '正偏印都', '印旺的人容易不好',
    '偏印的人恋爱', '官杀旺的人容易有强迫症', '官杀虽然理性',
    '高层次的八字不是', '伤官虽然喜欢展示', '偏印喜欢钻牛角',
    '偏印，吃软不吃硬', '《滴天髓》：旺者',
    '正偏印都有的人', '偏印容易脾气古怪',
    '为什么说八字通气那么重要', '命带神煞金舆',
    '没有驿马的一人一般', '一个驿马好动，但',
    '两个驿马，无法', '三个驿马，不但', '四个驿马，总想',
    '伤官和七杀', '比劫，就想', '念头就是',
    '伤官崇尚自由', '伤官如果主动', '十神们约了',
    '伤官，劫财旺', '七杀偏印旺', '七杀，属于是',
    '偏印，属于是', '七杀得印星', '比肩一般比较',
]


def extract_day_number(day_str):
    """从Day标题提取数字"""
    m = re.match(r'Day(\d+)', day_str)
    return int(m.group(1)) if m else 0


def split_into_items(text):
    """将一段文本按句号拆分成条目"""
    sentences = re.split(r'(?<=[。！？])', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return []

    items = []
    current_item = sentences[0]

    for sent in sentences[1:]:
        is_new_topic = any(sent.startswith(starter) for starter in TOPIC_STARTERS)
        if is_new_topic:
            items.append(current_item)
            current_item = sent
        else:
            current_item += sent

    items.append(current_item)
    return items


def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    output_lines = []
    current_day = None
    day_num = 0
    day_content_lines = []

    def flush_day():
        nonlocal day_content_lines
        if not current_day or not day_content_lines:
            return

        has_numbering = any(re.match(r'^\d+[.、．]\s', l.strip()) for l in day_content_lines)
        item_count = 0
        tag = '📋' if day_num % 2 == 1 else '🎙️'

        if has_numbering:
            # 有编号：按编号拆分
            current_item = []
            for line in day_content_lines:
                stripped = line.strip()
                if not stripped or stripped == '---':
                    if current_item:
                        item_count += 1
                        merged = ' '.join(current_item)
                        output_lines.append(f'{tag} **{item_count}.**')
                        output_lines.append(merged)
                        output_lines.append('')
                        current_item = []
                    continue

                item_match = re.match(r'^(\d+)[.、．]\s*(.+)$', stripped)
                if item_match:
                    if current_item:
                        item_count += 1
                        merged = ' '.join(current_item)
                        output_lines.append(f'{tag} **{item_count}.**')
                        output_lines.append(merged)
                        output_lines.append('')
                    current_item = [item_match.group(2).strip()]
                elif stripped.startswith('#'):
                    continue
                else:
                    current_item.append(stripped)

            if current_item:
                item_count += 1
                merged = ' '.join(current_item)
                output_lines.append(f'{tag} **{item_count}.**')
                output_lines.append(merged)
                output_lines.append('')
        else:
            # 没有编号：合并后按话题拆分
            all_text = ' '.join(
                l.strip() for l in day_content_lines
                if l.strip() and l.strip() != '---' and not l.strip().startswith('#')
            )

            items = split_into_items(all_text)
            for item_text in items:
                item_count += 1
                output_lines.append(f'{tag} **{item_count}.**')
                output_lines.append(item_text)
                output_lines.append('')

        day_content_lines = []

    for line in lines:
        day_match = re.match(r'^## (Day\d+.*)$', line)
        if day_match:
            flush_day()
            if current_day:
                output_lines.append('')
            current_day = day_match.group(1)
            day_num = extract_day_number(current_day)
            output_lines.append(f'## {current_day}')
            output_lines.append('')
            day_content_lines = []
            continue

        if current_day:
            day_content_lines.append(line)

    flush_day()

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    # 统计
    blue = sum(1 for l in output_lines if l.startswith('📋'))
    yellow = sum(1 for l in output_lines if l.startswith('🎙️'))
    print(f"✅ Done! {output_path}")
    print(f"   📋 蓝色: {blue}条  🎙️ 黄色: {yellow}条  总计: {blue+yellow}条")


if __name__ == '__main__':
    inp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT
    process_file(inp, out)
