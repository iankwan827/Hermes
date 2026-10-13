# MEMORY 文件系统：突破 2200 字符限制

## 问题
Hermes 内置 MEMORY 工具有 2200 字符限制。压缩后丢失重要细节。

## 方案
MEMORY 只做索引，详细内容存文件。

## 目录结构
```
~/.hermes/memory/
├── 01_douyin_platform.json  # 抖音/平台/小红书/热搜
├── 02_bazi.json             # 八字/排盘/Web系统/课程
├── 03_content_workflow.json # 文案工作流/栋笃笑/开头技巧
├── 04_tools_config.json     # Vercel/GitHub/skill/配置
└── 05_user_profile.json     # 用户信息/风格/标准
```

## MEMORY 索引格式
```
§
【MEMORY文件系统】详细记忆存~/.hermes/memory/，按主题分文件：01_xxx.json（主题说明）、02_xxx.json（主题说明）。需要详情时read_file对应JSON。
```

## 使用方式
1. 新 session 启动 → 读 MEMORY 索引
2. 需要详细信息 → `read_file("~/.hermes/memory/02_bazi.json")`
3. 更新记忆 → 直接修改对应 JSON 文件

## 优点
- 无大小限制
- 结构化（按主题分文件）
- 可搜索（JSON 格式）
- 不会被压缩丢失

## 注意
- MEMORY 索引要简洁（主题名 + 文件路径）
- JSON 文件用中文 key（方便阅读）
- 更新时直接改文件，不用管 MEMORY 大小
