# 变量数据字典

> 记录所有关键变量的定义位置、数据来源、使用位置。
> 修改时必须对照此文档，避免变量错乱。

---

## 全局变量

| 变量名 | 数据 | 数据来源 | 赋值位置 | 使用位置 |
|--------|------|---------|---------|---------|
| `sandeLevel` | 三得法结果 | computeSanDe() | line XX | renderTab2, renderStrengthSummary |
| `tongguanMedicine` | 通关用神五行 | renderYongShen() | line XX | renderYongShen, renderStrengthSummary, renderDayunLiunian |
| `bingyaoMedicine` | 病药用神五行 | renderYongShen() | line XX | renderYongShen, renderStrengthSummary, renderDayunLiunian |
| `currentResult` | 排盘结果对象 | doCalc() | line XX | renderTab1/2/3 |

---

## 数据流

```
doCalc()
  → computeSanDe() → sandeLevel
  → renderYongShen() → tongguanMedicine, bingyaoMedicine
  → renderStrengthSummary() → 直接用上面的变量
  → renderDayunLiunian() → 直接用上面的变量
```

---

## 常见错误

1. 函数内定义变量，其他函数访问不到 → 用全局变量
2. 同一变量多处定义 → 只在全局定义一次
3. 显示时重新计算 → 直接用已计算的变量
4. 变量名不一致 → 统一命名
