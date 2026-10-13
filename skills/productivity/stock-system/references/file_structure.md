# 文件结构

## 目录布局

```
~/Pictures/选股/
├── stock_screener.py      # 第一池选股脚本
├── pool2_screener.py      # 第二池选股脚本
├── risk_assessment.py     # 风险评估模块
├── capture_execution.py   # 执行价采集
├── update_feishu_sheet.py # 飞书表格更新
├── 指标体系.md            # 指标文档
├── data/                  # 缓存数据
│   ├── kline_year.json    # 年度K线缓存
│   ├── quarterly.json     # 季度财务数据
│   ├── weekly.json        # 周度数据
│   └── history.json       # 历史排名
├── results/               # 选股结果
│   ├── weekly_YYYYMMDD_HHMM.csv  # 评分结果
│   ├── risk_YYYYMMDD_HHMM.json   # 风险详情
│   └── pool2_*.csv        # 第二池结果
└── state/                 # 追踪状态
    └── watchlist_*.csv    # 持仓追踪
```

## 关键文件说明

### stock_screener.py
第一池选股，输出Top20排名。**不跑风险评估**，只在对比最早历史记录时触发诊断。

### pool2_screener.py
第二池选股，输出Top30排名。**不跑风险评估**，只在对比最早历史记录时触发诊断。

### risk_assessment.py
**诊断工具**（不是门卫），按指标体系文档检查8类指标：
- 均线跌破（MA20/60/120）
- 成交量风险（放量下跌/缩量）
- 高位回调（从高点回调幅度）
- 利润增长率
- 资产负债率
- 股东人数变化
- 北向资金流向
- 重大公告

**触发条件**：评分掉≥5分 或 股价跌≥10%
**判断逻辑**：看具体是哪个指标导致的，那个指标本身是好是坏

### history.json 结构
```json
{
  "last_run": {
    "date": "2026-06-27 15:47",
    "ranks": {"600961": 1, "601168": 2, ...},
    "scores": {"600961": 59.0, "601168": 55.0, ...},
    "top5": ["600961", "601168", ...],
    "version": "2.1"
  },
  "recent": [
    {
      "date": "2026-06-22 09:42",
      "top5": ["600961", "001210", ...],
      "top5_scores": [63.0, 60.0, ...],
      "top20": ["600961", "601168", ...],
      "top20_scores": {"600961": 59.0, ...}
    },
    ...
  ]
}
```

**重要**：风险诊断对比 `recent[0]`（最早记录），不是 `recent[-2]`（上一次运行）

### capture_execution.py
采集执行价（周一/周二09:35运行）。
