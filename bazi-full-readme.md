# 八字多Agent系统 Skill完整包

**打包时间**: 2026-07-26
**文件**: bazi-full-package.tar.gz (909K, 329文件)

## 目录结构

```
├── bazi-system/          # 主系统（41个skill）
│   ├── bazi-master       # 协调器/指挥
│   ├── bazi-analyst      # 分析Agent
│   ├── bazi-reviewer     # 审核Agent
│   ├── bazi-responder    # 回复Agent
│   ├── bazi-paipan       # 排盘（含JS脚本）
│   ├── bazi-trigger      # 条件触发检测
│   ├── bazi-shishen      # 十神总纲
│   ├── bazi-shishen-*    # 10个十神专题（比肩/劫财/偏财/正财/食神/伤官/偏印/正印/七杀/正官）+ 十天干
│   ├── bazi-geju         # 格局判定
│   ├── bazi-xiyong       # 取喜用神
│   ├── bazi-dizhi        # 地支关系
│   ├── bazi-sizhu        # 四柱代表
│   ├── bazi-xingge       # 性格分析
│   ├── bazi-peiou        # 配偶画像
│   └── ...               # 健康/痣相/性冷淡/身材等专项
│
├── bazi/                 # 独立模块（5个skill）
│   ├── bazi-analysis     # 旧版分析（含多Agent架构设计文档）
│   ├── bazi-dayun-liunian # 大运流年分析
│   ├── bazi-kongwang     # 空亡专题
│   ├── bazi-muku         # 墓库专题
│   └── bazi-yulu         # 语录管理（含飞书处理脚本）
│
├── bazi-sales/           # 销售系统（6个skill + 知识库）
│   ├── bazi-fukeshengyu  # 女命生育判断
│   ├── bazi-zhiduan      # 直断速查（28秘诀+速查表）
│   ├── bazi-sales-steps  # 销售实战步骤
│   ├── scripts/          # 排盘JS脚本（7个）
│   └── references/       # 15份知识库 + 案例
│
├── bazi-sales-*/         # 销售多Agent（8个skill）
│   ├── bazi-sales-orchestrator  # 协调器
│   ├── bazi-sales-validator     # 话术质检
│   ├── bazi-sales-agent1-*      # 诊断/解析
│   ├── bazi-sales-agent2-*      # 知识库/话术
│   ├── bazi-sales-agent3-*      # 成交
│   └── bazi-sales-agent5-*      # 话术生成
│
└── 独立skill（9个）
    ├── bazi-geju              # 格局判定（独立版）
    ├── bazi-trigger           # 条件触发检测（独立版）
    ├── bazi-paipan-agent      # 排盘Agent
    ├── bazi-hunyin-cishu      # 婚姻次数判断
    ├── bazi-gongchuan         # 夫妻宫穿夫妻星
    ├── bazi-duanpeifu         # 配偶类型判断
    ├── bazi-dinghuo           # 丁火专题
    ├── bazi-ganbing           # 肝部健康
    └── bazi-xinzangbing       # 心脏健康
```

## 部署方法

```bash
cd ~/.hermes/profiles/main/skills/
tar xzf bazi-full-package.tar.gz
# 重启 Hermes 使 skill 生效
```

## 核心流程

```
用户输入(年月日时性别) → bazi-master(协调器)
  → bazi-paipan(排盘) → bazi.json
  → bazi-trigger(条件检测) → trigger.json
  → bazi-analyst(分析，按8层体系)
    每层加载对应skill，输出layerX.json
  → bazi-reviewer(审核，检查skill完整性)
  → bazi-responder(回复，命理师视角输出)
```

## 依赖

- Node.js（排盘JS脚本）
- `node generate_bazi_analysis.js <年> <月> <日> <时> <性别(M/F)>`
