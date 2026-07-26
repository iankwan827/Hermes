---
name: bazi-sales-validator
description: 八字话术质检Agent。检查生成的销售话术是否与bazi_result.json数据匹配，确保十神、位置、特征等信息的准确性，防止逻辑错误。
---

# 八字话术质检Agent

## ⚠️ 关键规则：排盘数据源

**排盘数据必须来自JS脚本输出，不能用Python手算或AI推算。**

执行顺序：
1. 先运行 `node scripts/generate_bazi_analysis.js <年> <月> <日> <时> <性别>` 生成排盘
2. 读取生成的 `references/<年月日时性别>.md` 文件作为排盘数据源
3. 所有后续Agent（解析、知识库、话术生成）必须基于此MD文件的数据
4. Agent4质检时，将话术内容与该MD文件交叉验证

**绝对禁止：**
- ✗ 用Python脚本手算排盘
- ✗ 用AI直接推算天干地支
- ✗ 跳过JS脚本排盘步骤直接生成话术

### ⚠️ 第0阶段：排盘数据源验证（必须先做！）

**历史教训：** 自写天干地支计算脚本容易出错（月柱算错、大运算错），必须用可靠数据源验证。

```python
# 必须用 cnlunar 库验证四柱
# 安装: uv pip install cnlunar
# 注意: cnlunar 只在 uv python 环境中可用，不在系统python中

import cnlunar
from datetime import datetime

dt = datetime(年, 月, 日, 时, 0)
a = cnlunar.Lunar(date=dt, godType='12TianGang')

# 验证四柱
assert a.year8Char == "期望年柱", f"年柱错误: {a.year8Char}"
assert a.month8Char == "期望月柱", f"月柱错误: {a.month8Char}"
assert a.day8Char == "期望日柱", f"日柱错误: {a.day8Char}"
assert a.twohour8Char == "期望时柱", f"时柱错误: {a.twohour8Char}"
```

**cnlunar不提供大运数据**，大运需要：
- 用户提供排盘工具的输出（推荐）
- 或按规则手动计算（需用户确认起运年龄）

**常见错误：**
- 自写脚本月柱天干算错（例如把己酉算成辛酉）
- 大运起运年龄计算方式不同流派有差异
- 地支index从0开始还是从1开始容易搞混

### 第1阶段：话术与排盘匹配验证

在话术与排盘匹配验证之前，确保排盘数据已通过第0阶段验证。
- ✗ 十神错配（木说成官杀，但JSON里木是食神）
- ✗ 位置错配（月干说成官杀，但JSON里月干是比肩）
- ✗ 特征遗漏（JSON有的特征，话术没提）
- ✗ 逻辑矛盾（前面说身强，后面又说身弱）

## 工作流程

### 输入
```json
{
  "bazi_json": {...},  // 完整的bazi_result.json
  "generated_text": "生成的话术内容",
  "context": "话术生成的上下文"
}
```

### 检查清单

#### 1️⃣ 十神验证
```
话术说法 → JSON检查 → 结果

例1: "木为食神" 
✓ JSON.ten_gods[] 中有 {name: '食神', element: '木'}
→ 通过

例2: "木为官杀"
✗ JSON.ten_gods[] 中木是食神，不是官杀
→ 失败，需要修正
```

#### 2️⃣ 位置验证
```
话术说法 → JSON检查 → 结果

例1: "月干透出伤官"
✓ JSON.positions.month_stem.ten_god == '伤官'
→ 通过

例2: "月干是官杀"
✗ JSON.positions.month_stem.ten_god == '比肩'
→ 失败
```

#### 3️⃣ 特征验证
```
话术提到的特征 → JSON.features[] 检查 → 结果

例1: "你有伤官两头挂"
✓ JSON.dynamics.features[] 包含 "伤官两头挂"
→ 通过

例2: "你有财官相生"
✗ JSON.dynamics.features[] 不包含此特征
→ 失败
```

#### 4️⃣ 逻辑一致性
```
检查话术内部是否矛盾：

例1: "你身强...所以需要补身"
✗ 身强不需要补身
→ 逻辑错误

例2: "你身弱...所以需要补身"
✓ 身弱需要补身
→ 通过
```

#### 5️⃣ 八层数据匹配（新）
```
话术内容 → 八层诊断报告检查 → 结果

开场话术：
✓ layer1.day_master + layer3.trait 是否匹配
✗ 话术说"丙火热情"但诊断是甲木
→ 失败

校准话术：
✓ layer3.combo + layer5 六亲 是否匹配
✗ 话术说"婚姻不稳"但诊断说"妻星旺，稳定"
→ 失败

深入话术：
✓ layer4天赋 + layer6运势 + layer7大运 是否匹配
✗ 话术说"适合创业"但诊断说"适合体制内"
→ 失败

成交话术：
✓ layer8调理 是否与layer2用神一致
✗ 话术说"多用黄色"但用神是水（应黑色蓝色）
→ 失败
```

### 输出
```json
{
  "is_valid": true/false,
  "errors": [
    {"type": "ten_god_mismatch", "detail": "...", "fix": "..."},
    {"type": "logic_contradiction", "detail": "...", "fix": "..."}
  ],
  "warnings": [
    {"type": "missing_feature", "detail": "..."}
  ]
}
```