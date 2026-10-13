#!/usr/bin/env python3
"""
拆分多十神条目到对应的skill
对于包含多个十神的条目，复制到每个对应的skill
"""

import json
import os
import re
from collections import defaultdict

# 十神映射
SHISHEN_MAP = {
    "比肩": "bijian",
    "劫财": "jiecai", 
    "食神": "shishen",
    "伤官": "shangguan",
    "偏财": "piancai",
    "正财": "zhengcai",
    "偏印": "pianyin",
    "正印": "zhengyin",
    "七杀": "qisha",
    "正官": "zhengguan",
}

def load_yulu_json():
    """加载语录分类JSON"""
    with open(os.path.expanduser("~/Pictures/八字课/语录/语录分类.json"), 'r') as f:
        return json.load(f)

def extract_shishen_sentence(text, target_shishen):
    """
    从多十神文本中提取与目标十神相关的句子
    简单策略：找到包含目标十神关键词的句子
    """
    # 分句
    sentences = re.split(r'[。！？]', text)
    
    relevant = []
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        
        # 检查是否包含目标十神关键词
        shishen_keywords = {
            "比肩": ["比肩", "比劫", "身强", "独立"],
            "劫财": ["劫财", "比劫", "破财", "合伙"],
            "食神": ["食神", "食伤", "口福", "才华"],
            "伤官": ["伤官", "食伤", "叛逆", "口才"],
            "偏财": ["偏财", "桃花", "意外之财", "大方"],
            "正财": ["正财", "稳定收入", "务实", "节俭"],
            "偏印": ["偏印", "枭印", "枭神", "玄学"],
            "正印": ["正印", "母亲", "贵人", "学业"],
            "七杀": ["七杀", "偏官", "压力", "权力"],
            "正官": ["正官", "规矩", "责任", "稳定"],
        }
        
        keywords = shishen_keywords.get(target_shishen, [target_shishen])
        for kw in keywords:
            if kw in sent:
                relevant.append(sent)
                break
    
    return "。".join(relevant) + "。" if relevant else ""

def main():
    # 加载语录分类
    data = load_yulu_json()
    items = data["items"]
    
    print(f"总条目数: {len(items)}")
    
    # 按十神分类（包括多十神条目的拆分）
    by_shishen = defaultdict(list)
    
    for item in items:
        shishen_list = item.get("shishen", [])
        
        # 过滤掉"日元"
        shishen_list = [s for s in shishen_list if s != "日元"]
        
        if len(shishen_list) == 0:
            continue
        
        # 对于每个十神，添加到对应的skill
        for shishen in shishen_list:
            if shishen in SHISHEN_MAP:
                skill_name = SHISHEN_MAP[shishen]
                
                # 如果是多十神条目，尝试提取相关句子
                if len(shishen_list) > 1:
                    extracted = extract_shishen_sentence(item["content"], shishen)
                    if extracted:
                        # 使用提取的内容
                        new_item = item.copy()
                        new_item["content"] = extracted
                        new_item["original_content"] = item["content"]
                        by_shishen[skill_name].append(new_item)
                    else:
                        # 提取失败，使用原内容
                        by_shishen[skill_name].append(item)
                else:
                    by_shishen[skill_name].append(item)
    
    print(f"\n分类统计:")
    for skill_name, items_list in sorted(by_shishen.items()):
        print(f"  {skill_name}: {len(items_list)}条")
    
    # 生成新的yulu.md文件
    output_dir = os.path.expanduser("~/.hermes/profiles/main/skills/bazi-system")
    
    for skill_name, items_list in by_shishen.items():
        skill_dir = os.path.join(output_dir, f"bazi-shishen-{skill_name}")
        if skill_name == "shishen":
            yulu_path = os.path.join(skill_dir, "references/shishen-yulu.md")
        else:
            yulu_path = os.path.join(skill_dir, "references/yulu.md")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(yulu_path), exist_ok=True)
        
        # 按主题分组
        by_topic = defaultdict(list)
        for item in items_list:
            topic = item.get("topics", ["通用"])[0] if item.get("topics") else "通用"
            by_topic[topic].append(item)
        
        # 生成内容
        content = f"# {skill_name}语录集\n\n> 共{len(items_list)}条，按主题分类\n"
        
        for topic, topic_items in by_topic.items():
            content += f"\n## {topic}（{len(topic_items)}条）\n\n"
            for item in topic_items:
                day = item.get("day", "")
                text = item.get("content", "")
                content += f"- **Day{day}** {text}\n"
        
        # 写入文件
        with open(yulu_path, 'w') as f:
            f.write(content)
        
        print(f"已生成: {yulu_path}")
    
    # 输出统计
    print(f"\n{'='*60}")
    print("完成！所有十神语录已重新分配")
    print("="*60)

if __name__ == "__main__":
    main()
