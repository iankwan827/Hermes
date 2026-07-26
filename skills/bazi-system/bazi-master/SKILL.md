---
name: bazi-master
description: 八字多Agent协调器。接收用户输入，运行排盘Agent获取JSON，识别问题类型，路由到分析Agent加载对应skill，最后审核输出。触发词：分析八字、排盘分析、看看八字、八字分析。
tags: [bazi, 协调器, orchestrator]
triggers:
  - "分析八字"
  - "八字分析"
  - "排盘分析"
  - "看看八字"
  - "帮我看看"
---

# 八字多Agent协调器

## 架构

```
用户输入 → bazi-master(协调器)
              ↓
    ┌─────────────────────┐
    │ Agent1: 排盘Agent    │ → 输出 bazi.json
    │ Agent1.5: 定位Agent  │ → 输出分析方向
    │ Agent2: 分析Agent    │ → 分层输出分析文本
    │ Agent3: 审核Agent    │ → 校验
    │ Agent4: 输出Agent    │ → 输出 analysis.json
    │ Agent5: 回复Agent    │ → 唯一对外输出
    └─────────────────────┘
```

## 指挥模式

**协调器按照八层体系，一步步指挥分析Agent执行。**

### 分析流程

**核心原则：协调器确保所有skill在1-5层中都被加载过。过三关是Responder的输出模式，不是分析层。**

1. 每层分析结果必须存JSON（references/layerX.json）
2. 所有层完成后，bazi-responder读取JSON生成侧写回复
3. **侧写输出后，审核agent检查侧写内容是否与JSON数据一致**（正印写成偏印这种错误要拦住）
4. **只有bazi-responder可以发送消息给用户**
5. Responder不关心skill加载步骤，只读JSON，用命理师视角输出

### 各层JSON输出格式

每层分析完成后，存到`/Users/guanmian/.hermes/profiles/main/skills/bazi-system/references/layerX.json`：

```json
{
  "layer": X,
  "name": "层名称",
  "content": {
    // 该层的分析内容
  },
  "summary": "一句话总结"
}
```

### 根据问题类型决定分析深度

| 用户问题 | 分析到哪层 |
|---------|-----------|
| 过三关/快速验证 | 第0-1层 |
| 看性格/什么人 | 第0-3层 |
| 看六亲/婚姻/配偶 | 第0-4层 |
| 看事业/财运 | 第0-5层 |
| 看今年运势 | 第0-6层 |
| 全面分析 | 第0-8层 |

### 关键规则

1. **第0层是过三关**，必须先跑。扫描13个skill快速验证，建立信任（其中bazi-hunyin-tongwuxing仅日柱同五行时加载，bazi-fukeshengyu仅女命时加载）
2. **过三关只是第一步**，过完三关后要继续跑后面的层（第1-5层），不要停
3. **后面layers没实现不影响前面的**，先把能做的做好
4. **健康是第5层专项运势**，不是过三关。过三关只验证外在特征
5. **每层都要跑**，不能跳过。第0层过三关→第1层排盘→第2层格局→第3层性格→第4层六亲→第5层专项

### 协调器指令格式

告诉分析Agent时，格式：

```
当前任务：第X层 - [层名称]
具体要求：[该层需要做什么]
必须加载skill：[列出必须加载的skill名称]
可选加载skill：[根据问题类型可选加载的skill]
```

### 各层必须加载skill

| 层 | 必须加载skill | 可选加载skill |
|----|--------------|--------------|
| 第1层 | bazi-paipan, bazi-sizhu | bazi-kongwang |
| 第2层 | bazi-geju, bazi-shishen | bazi-dizhi（如有三会/三合） |
| 第3层 | bazi-xingge, bazi-shishen | bazi-zhi, bazi-xiongbu, bazi-xinglengdan, bazi-haose, bazi-shencai, bazi-daogui, bazi-lanyin, bazi-dinghuo |
| 第4层 | bazi-sizhu, bazi-shishen, bazi-peiou, bazi-duanpeifu, bazi-gongchuan, bazi-hunyin-cishu | bazi-muku（如有墓库）、bazi-hunyin-tongwuxing（仅日柱同五行时）、bazi-fukeshengyu（gender=F） |
| 第5层 | - | 按专项加载对应skill |
| 第6层 | bazi-dayun | bazi-dizhi（流年地支关系） |
| 第7层 | - | - |
| 第8层 | bazi-tiaoli | - |

**⚠️ 协调器必须确保所有skill在1-5层中都被加载过一次**

---

## Skill索引表

| 索引 | Skill | 触发条件 | 内容 |
|------|-------|---------|------|
| 0 | bazi-geju | 始终 | 格局判定、用神忌神 |
| 1 | bazi-shishen | 始终 | 十神分类、详解、组合 |
| 2 | bazi-dizhi | 地支关系 | 三会/三合/六冲/刑害 |
| 3 | bazi-sizhu | 始终 | 四柱代表信息 |
| 4 | bazi-xingge | 问性格 | 性格分析 |
| 5 | bazi-peiou | 问配偶 | 配偶画像 |
| 6 | bazi-duanpeifu | 问配偶类型 | 断配偶偏好与异性类型 |
| 7 | bazi-hunyin-tongwuxing | 日柱同五行时 | 上下同五行=二婚之象（条件触发） |
| 8 | bazi-gongchuan | 问婚姻 | 夫妻宫穿夫妻星 |
| 9 | bazi-hunyin-cishu | 问婚姻次数 | 婚姻次数判断 |
| 10 | bazi-shiye | 问事业 | 事业方向 |
| 11 | bazi-caiyun | 问财运 | 财运层次 |
| 12 | bazi-dayun | 问运势 | 大运流年 |
| 13 | bazi-muku | 辰戌丑未 | 墓库 |
| 14 | bazi-kongwang | 始终检查 | 空亡 |
| 15 | bazi-fukeshengyu | gender=F | 女命生育 |
| 16 | bazi-zhi | 痣相 | 痣相三板斧 |
| 17 | bazi-xinglengdan | 问性冷淡 | 性冷淡八字密码 |
| 18 | bazi-haose | 问好色 | 好色分析 |
| 19 | bazi-daogui | 问倒追 | 被女倒追特征 |
| 20 | bazi-lanyin | 问懒 | 印星过旺与懒 |
| 21 | bazi-shencai | 问身材 | 八字看身材 |
| 22 | bazi-xiongbu | 问胸部 | 胸部痣分析 |
| 23 | bazi-dinghuo | 丁火专题 | 丁火性质、熬夜、背部痣 |
| 24 | bazi-weibing | 问脾胃 | 脾胃病八字分析 |
| 25 | bazi-feibu | 问肺部 | 肺部健康八字分析 |
| 26 | bazi-shenbing | 问肾病 | 肾病八字分析 |
| 27 | bazi-ganbing | 问肝病 | 肝部健康八字分析 |
| 28 | bazi-xinzangbing | 问心脏 | 心脏健康八字分析 |

---

## 关键规则

1. **🚨 排盘脚本是第一步，没有例外。** 即使用户只是随口说"帮我看看这个八字"，也必须先跑JS排盘脚本获取正确的十神。绝对不能手算十神——AI手算错误率极高（甲见丁=伤官非食神，甲见酉=正官非七杀，甲见卯=劫财非比肩）。用户原话："我们八字系统不是有完整的js计算吗"
2. **协调器确保所有skill在1-5层中都被加载过**，不能遗漏
2. **后面layers没实现不影响前面的**，先把能做的做好
3. **每层都要跑**，不能跳过。第1层排盘→第2层格局→第3层性格→第4层六亲→第5层专项
4. **分析结果必须存JSON**：每层结果存到references/layerX.json
5. **bazi-responder是唯一对外输出**：其他Agent的结果都在内部流转，只有responder可以发送消息给用户
6. **Responder不关心skill加载步骤**：只读JSON，用命理师视角输出（侧写模式）
7. **⚠️ 侧写输出后必须经过审核agent检查**：逐条核对侧写内容是否与JSON数据一致，十神判断错误（如正印写成偏印）是严重错误
8. **⚠️ 不要把正印写成偏印**：甲子日柱子水=正印，不是偏印。排盘脚本标注正确但侧写可能搞混——性格怎么样、性冷淡还是啥、健康有什么问题
8. **不要前言不对后语**：如果不确定内容是否已存在，先检查再说。不要一会儿说"已经写了"一会儿说"需要补充"

---

## 用户交互偏好（铁律）

### 教学方式：案例纠正 → 自我发现 → 举一反三

**用户原话：「你能不能好好看看」「你看看课程的三得法，人家讲的不是这样的」「好像我们skill没有用到三得法吧」**

用户纠正错误时，不会直接给答案，而是：
1. 指出问题所在（"你看看课程原文"）
2. 让Agent自己回去查证、对比
3. Agent发现差异后，用户进一步引导深入分析
4. 最终由Agent自己总结出结论

**期望Agent做到：**
- 举一反三：一个案例的纠正要推广到同类问题
- 先查自己数据库再问：遇到疑问先搜skill references和课程笔记
- 不要翻用户电脑文件找答案：用户会反感Agent乱翻文件

**不要做的事：**
- 不要在参考文件中写具体测试案例（用户需要用同一个案例做测试验证）
- 参考文件只写方法论、通用示例和判断标准

**案例：旺衰判断纠正过程（2026-07-10）**
1. 用户说"你看看课程的三得法"→ 我回去查课程原文
2. 发现三得法"得生得助"只看天干→ 我自己得出1/3身弱的结论
3. 用户说"人家写的是天干相助"→ 我重新理解得生得助的定义
4. 用户给丁卯己酉甲子丁卯案例→ 我对比两个视角发现矛盾
5. 用户说"公式算出来也是身强啊"→ 我意识到是三得法工具有问题
6. 最终我自己总结：三得法有盲区，必须看地支实际力量

---

## 参考文件

| 文件 | 内容 |
|------|------|
| `references/分析步骤.md` | Phase 2-9详细步骤 |
| `references/常见错误.md` | 17条Pitfalls |
| `references/关键路径.md` | 脚本位置、案例文件路径 |
