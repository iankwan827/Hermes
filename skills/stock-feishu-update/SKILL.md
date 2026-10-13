---
name: stock-feishu-update
description: "This skill should be used when the weekly stock report is ready and needs to be synced to the Feishu spreadsheet. Covers OAuth token management, data fetching, KLM column formatting, and dropped-stock highlighting."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [stock, feishu, spreadsheet, weekly-update]
    created_by: agent
---

# 选股飞书表格更新

## Purpose

Sync weekly stock screening results to the user's Feishu spreadsheet. Run this after the weekly report is generated (every Friday).

## When to Use

- After `stock_screener.py` and `pool2_screener.py` complete
- After `risk_monitor.py` finishes
- When user says "更新表格" or "选股表格"

## Spreadsheet Location

**飞书云盘 → 「三板斧」文件夹 → `选股Top20·双池独立`**

- Token: `APv3sZM02h4DQrt8Bcrclin4nfW`
- 第一池(稳健): sheet_id `4df71e`
- 第二池(成长): sheet_id `LVwKQ`

## Prerequisites

- user_access_token in `~/.hermes/profiles/main/feishu_user_token.json`
- Weekly CSV files in `~/Pictures/选股/results/`
- Risk monitor output in `~/Pictures/选股/state/`

## Update Procedure

### Step 1: Verify OAuth Token

```python
# Read token
with open(os.path.expanduser("~/.hermes/profiles/main/feishu_user_token.json")) as f:
    user_token = json.load(f)["access_token"]

# Test with a read request
GET /open-apis/sheets/v2/spreadsheets/{TOKEN}/values/4df71e!A1:A1
# If 400/401 → token expired → run OAuth flow (see feishu-integration skill)
```

### Step 2: Load CSV Data

```python
import csv
# Handle BOM
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    stocks = list(reader)
```

### Step 3: Fetch Weekly Prices

```python
# For each stock in Top20
prefix = "sh" if code.startswith("6") else "sz"
url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={prefix}{code}&scale=240&ma=no&datalen=5"
# Returns last 5 trading days → map to F-J columns (周一~周五)
```

### Step 4: Write to Spreadsheet

```python
# Write Top20 rows
PUT /open-apis/sheets/v2/spreadsheets/{TOKEN}/values
body: {"valueRange": {"range": "4df71e!A2:Q21", "values": rows}}

# Write dropped stocks (row 21+)
# Highlight in red
PUT /open-apis/sheets/v2/spreadsheets/{TOKEN}/styles_batch_update
body: {"data": [{"ranges": "4df71e!A21:Q21", "style": {"fontColor": "#FF0000"}}]}
```

## Column Structure (A-Q)

| Col | Content | Source |
|-----|---------|--------|
| A | 代码 | CSV |
| B | 名称 | CSV |
| C | 综合评分 | CSV |
| D | 风险等级 | CSV |
| E | 风险建议 | CSV |
| F-J | 周一~周五收盘价 | Sina API |
| K | 扣分指标1 | See KLM Rules |
| L | 扣分指标2 | See KLM Rules |
| M | 扣分指标3 | See KLM Rules |
| N | 建议 | CSV |
| O-Q | 开盘价/当前价/滑点 | Leave empty |

## KLM Rules (Critical)

**Each column = ONE specific indicator that caused score drop. Write as many columns as there are weak indicators. Leave empty if none.**

Format: `Indicator name + score (max) + problem description`

Correct:
```
K: 成长指标仅7分(满分20)，拖累综合评分
L: 资金面13分(满分35)，龙虎榜无机构买入
M: 估值10分(满分15)偏低，PE 27.8偏高
```

Wrong:
```
K: 上周#5本周跌出Top30  ← describes event, not indicator
L: 资金面偏弱  ← no specific score
M: 无重大风险公告  ← risk system result, not score component
```

**Scoring dimensions:**
- 第一池: 资金(35) + 趋势(25) + 成长(20) + 估值(15)
- 第二池: 资金(35) + 成长(30) + 趋势(25) + 行业(15)

## Dropped Stocks

1. Read `~/Pictures/选股/state/watchlist.json` — stocks with `weeks_out >= 1` are dropped
   - `weeks_out: 1` = 观察中（第1周），写入行21+，标黄
   - `weeks_out: 2` = 触发B规则卖出，写入行21+，**标红并保留1周**（客户需要看到卖出信号才能操作）
   - `weeks_out: 3` = 从追踪表和飞书表格中移除
2. Write to row 21+ (after Top20)
3. Highlight: red for weeks_out>=2 (卖出), yellow for weeks_out=1 (观察)
4. Fill KLM with specific weak indicators (same rules as above)

## ⚠️ 飞书更新铁律

**绝对不能删除处于观察或触发B规则状态的股票！** 客户持股需要看到数据才能操作。只有 weeks_out>=3 才能从飞书表格移除。

**更新飞书表格前，必须先读取当前追踪表（watchlist.json），把所有 weeks_out>=1 的股票一起写入，不能只写Top20。**

## OAuth Flow (when token expires)

1. Start OAuth server: `python3 ~/.hermes/profiles/main/skills/productivity/feishu-integration/scripts/feishu_oauth_server.py`
2. Navigate to auth URL via `browser_navigate`
3. Click "授权" button via `browser_click`
4. Wait for callback, token auto-saved

**Do NOT ask user to manually authorize. Execute automatically.**

## Pitfalls

1. **tenant_token read-only** — must use user_access_token for writes
2. **CSV has BOM** — use `encoding='utf-8-sig'`
3. **KLM = one indicator per column** — not descriptions or risk events
4. **Dropped stocks need KLM too** — specific weak indicators, not "fell out"
5. **Red via fontColor** — not backgroundColor
6. **risk_monitor.py scans both pools** — includes dropped stocks from last week
