# 八字多Agent架构重设计

## 文档位置
`~/Pictures/八字课/bazi-multi-agent-arch.md`

## 核心设计决策（已确认）

1. **排盘Agent独立化**：只运行JS脚本，输出bazi.json，不做分析
2. **Skill指针数组**：课程内容按专题拆成独立skill，agent按问题类型动态加载
3. **三Agent架构**：排盘Agent → 分析Agent（加载skill）→ 审核Agent
4. **JSON为数据桥梁**：排盘Agent输出JSON，下游Agent读取JSON工作

## 实施顺序
1. 架构文档（已完成）
2. bazi-master协调器skill
3. 逐个写专题skill
4. 审核skill
5. 测试完整流程

## 状态
- 架构文档：v1（2026-07-06）
- 用户要求：先定架构，skill最后写
- 当前bazi-analysis暂不改动，等架构确认后统一重构
