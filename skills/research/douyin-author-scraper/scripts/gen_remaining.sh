#!/bin/bash
# 生成剩余作者列表（去重+过滤已完成）
# 用法: bash gen_remaining.sh > remaining.txt
# 需要: authors.json, 进度文件中的已完成作者列表

AUTHORS_FILE="D:/hermes-agent/文案/authors.json"

# 用 execute_code 工具（不是 python 命令，本机 python 有 SRE 模块错误）
# 在 hermes 中用 execute_code 运行以下 Python 逻辑:
#
# import json
# done = set(['已完成作者1', '已完成作者2', ...])
# with open('D:/hermes-agent/文案/authors.json','r') as f:
#     authors = json.load(f)
# seen = set()
# for a in authors:
#     if a['sec_uid'] not in seen and a['nickname'] not in done and a['nickname'] != '已注销':
#         seen.add(a['sec_uid'])
#         print(a['sec_uid']+'|'+a['nickname'])
#
# 输出重定向到 remaining_authors.txt，然后用 batch_download.sh 处理

echo "用法："
echo "1. 在 hermes 中用 execute_code 生成去重作者列表"
echo "2. 保存到 remaining_authors.txt"
echo "3. bash scripts/batch_download.sh remaining_authors.txt"
