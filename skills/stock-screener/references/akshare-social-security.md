# 社保基金持仓数据 (akshare)

## 数据源
akshare `stock_report_fund_hold()` 函数

## 用法
```python
import akshare as ak

# 社保基金重仓股（按季度披露）
df = ak.stock_report_fund_hold(symbol='社保持仓', date='20260331')
# date格式: yyyy-03-31(一季报), yyyy-06-30(中报), yyyy-09-30(三季报), yyyy-12-31(年报)

# 列名: 序号, 股票代码, 股票简称, 持有基金家数, 持股总数, 持股市值, 持股变化, 持股变动数值, 持股变动比例
```

## 可选参数
- `symbol='社保持仓'` — 社保基金
- `symbol='基金持仓'` — 公募基金
- `symbol='QFII持仓'` — QFII
- `symbol='券商持仓'` — 券商
- `symbol='保险持仓'` — 保险
- `symbol='信托持仓'` — 信托

## 数据解读
- **持股变化**: 增仓/减仓/新进
- **持股变动比例**: 正数=增仓，负数=减仓
- **持有基金家数**: 多少只社保组合持有
- **持股市值**: 持仓市值（元）

## 示例：社保重仓TOP30
```python
df = ak.stock_report_fund_hold(symbol='社保持仓', date='20260331')
df = df.sort_values('持股市值', ascending=False)
for _, row in df.head(30).iterrows():
    print(f"{row['股票代码']} {row['股票简称']} | {row['持有基金家数']}家 | {row['持股市值']/1e8:.1f}亿 | {row['持股变化']}")
```

## 注意
- 数据按季度披露，有1-2个月延迟
- 2026Q1数据截至2026-03-31
- 社保基金偏好大市值白马股
- 可与选股池交叉对比，看是否有重合
