# cnlunar 八字排盘使用指南

## 安装
```bash
uv pip install cnlunar
```

## 环境注意
- cnlunar **只能在 `uv python` 环境中运行**
- 系统python（如 /e/Python/python）会报 `ImportError: cannot import name 'NamespaceLoader'`
- 正确调用方式：`PYTHON="$(uv python find 3.11)"`

## 基本用法
```python
import cnlunar
from datetime import datetime

dt = datetime(1987, 9, 12, 6, 0)  # 年月日时, 分=0
a = cnlunar.Lunar(date=dt, godType='12TianGang')

print(f'年柱: {a.year8Char}')      # 丁卯
print(f'月柱: {a.month8Char}')     # 己酉
print(f'日柱: {a.day8Char}')       # 甲子
print(f'时柱: {a.twohour8Char}')   # 丁卯
```

## 已知限制
- **不提供大运数据** — 需要手动计算或用户提供
- **不提供十神** — 需要根据天干地支关系自行推算
- **不提供纳音** — 需要查表

## 大运计算（cnlunar不支持时的手动方法）

### 规则
- 阳年男命/阴年女命 → 顺排（从月柱向后排）
- 阴年男命/阳年女命 → 逆排（从月柱向前排）

### 起运年龄
- 数出生日到上一个节气（逆排）或下一个节气（顺排）的天数
- 3天 = 1年起运年龄
- 例：出生日距白露4天 → 4/3 ≈ 1.3岁起运

### ⚠️ 常见错误
1. 地支index搞混：DI_ZHI=['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']，酉=9不是7
2. 大运逆排时，月柱天干地支要分别减index再取模
3. 起运年龄不同流派算法不同，**必须让用户确认**

## 自写脚本常见Bug
- 月柱天干计算公式错误（把己酉算成辛酉）
- 地支index从0开始还是从1开始搞混
- 大运起运年龄算法不统一
