---
name: stock-screener
description: A股双池选股系统操作指南。运行选股评分、生成买卖提示、回测策略。触发词：「选股」「跑选股」「买卖信号」「回测」「选股结果」
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [stock, screener, trading, A股, 选股, alerts]
    related_skills: [astock-data]
---

# A股双池选股系统 — 操作指南

## Overview

两套选股体系**独立运行、独立持仓、独立追踪**。
- **第一池（稳健池）**：`stock_screener.py` — 稳定盈利，长期持有。排除科创+北交。
- **第二池（成长池）**：`pool2_screener.py` — 资金启动，捕捉爆发。**同样排除科创+北交**（门槛50万+）。

**⚠️ 两个池子是独立的**：各自评分、各自Top5买入、各自追踪。不要混在一起。
**⚠️ 两个池子都排除科创+北交**：688xxx（科创）和8xxxxx/92xxx（北交）门槛50万+，大部分人没资格买。

数据获取和API细节见 `astock-data` skill。本skill聚焦于：怎么跑、怎么用、怎么解读结果。

## 附加数据源
- **社保基金持仓** → `references/akshare-social-security.md`（akshare查询社保持仓，按季度披露）

## When to Use

- 用户要求运行选股、查看选股结果
- 用户问"本周选了什么股"、"有没有买入/卖出信号"
- 用户要求回测选股策略的历史表现
- 设置定时选股任务
- 解读选股结果、解释评分逻辑

## 文件位置

所有脚本在 `~/Pictures/选股/`：

| 文件 | 用途 |
|------|------|
| `stock_screener.py` | 第一池（稳健池）v2.1 |
| `pool2_screener.py` | 第二池（成长池） |
| `risk_assessment.py` | **风险评估模块（三类信号分级）** |
| `backtest.py` | 回测脚本 |
| `alerts.py` | 买卖提示系统 |
| `cache_year_data.py` | 缓存一年K线数据（回测用） |
| `backtest_12month.py` | 12个月回测脚本（生成月度报告） |
| `update_watchlist.py` | 周度追踪（获取本周K线数据） |
| `capture_execution.py` | 采集执行价（周一/二开盘价）— **同时追踪第一池Top5+第二池Top5** |
| `risk_monitor.py` | 风险监控（每日扫描重大事件） |
| `指标体系.md` | **三类信号分级指标体系文档** |
| `results/backtest_reports/` | 12份月度回测报告 |
| `data/stocklist.json` | 股票列表缓存（当天有效） |
| `data/quarterly.json` | 季度财务数据缓存 |
| `data/weekly.json` | 周数据缓存（K线/龙虎榜/大宗交易） |
| `data/kline_year.json` | 一年K线数据（回测用） |
| `data/score_history.json` | 历史评分记录（提示系统用） |
| `data/portfolio.json` | 当前持仓建议 |
| `state/watchlist.json` | **持久化追踪表（只增不减，无上限）** |
| `state/watchlist_*.csv` | 周度追踪结果（CSV格式，供飞书同步） |
| `state/execution_*.csv` | 执行价采集结果 |
| `state/risk_*.json` | 风险监控结果 |
| `data_security.py` | 数据安全层（备份+恢复） |
| `data/backups/` | 核心数据备份（保留最近3版本） |
| `results/` | 历史选股结果CSV |
| `results/risk_*.json` | **风险评估详情（Top20的信号）** |

## 运行命令

### 第一池（稳健池）

```bash
cd ~/Pictures/选股 && python3 stock_screener.py --weekly
```

评分权重：资金35% + 趋势25% + 成长20% + 估值15%（**风险不参与评分**）

**评分与风险分离（V3）**：评分反映股票综合质量，风险反映操作建议，两者独立。

输出格式示例：
```
5. 001210 金房能源 | ¥23.83 | PE:28 | 深市主板
   综合:48.0 = 资金:13(35) + 趋势:18(25) + 成长:7(20) + 估值:10(15)
   🔴 风险等级: risk | 暂停新建仓，已有仓位考虑减仓
   ⚠️ 触发: 均线跌破(跌破MA60(24.44)) | 高位回调(从高点37.95回调37.9%) | 利润增速放缓(增长率2.1%)
```

**四级风险等级**：
- 🟢 normal：正常交易
- 🟡 watch：暂停新建仓，已有仓位继续观察
- 🔴 risk：暂停新建仓，已有仓位考虑减仓
- 🚨 sell：建议卖出，核心逻辑已破坏

筛选条件：
- 初筛：PE<150, 市值>50亿, 非ST
- 二次筛选：ROE>8%, 负债率<75%（有数据才筛）
- 主升浪排除：250日涨幅>200%自动剔除
- 板块：沪市主板+深市主板+创业板（排除科创板+北交所）

其他参数：
- `--force`：强制刷新所有数据
- `--refresh-quarterly`：只刷新季度财务数据
- `--daily`：每日检查持仓异常

### 第二池（成长池）

```bash
cd ~/Pictures/选股 && python3 pool2_screener.py
```

评分权重：资金35% + 成长30% + 趋势20% + 行业15% + **风险调整**

同样应用风险调整机制，输出包含风险信号。

筛选条件：
- **排除科创板+北交所**（门槛50万+）
- 市值30-800亿优先
- 热门行业加分（AI/半导体/机器人/医药/新能源/消费电子）
- 关注资金启动信号（放量/龙虎榜/换手率）

### 风险评估模块（V2 - 评分与风险分离）

```bash
# 单独测试某只股票的风险评估
cd ~/Pictures/选股 && python3 -c "
from risk_assessment import run_risk_assessment
import pandas as pd, json
with open('data/kline_year.json') as f:
    klines = json.load(f)
kline_df = pd.DataFrame(klines.get('001210'))
result = run_risk_assessment('001210', kline_df)
print(f'风险等级: {result[\"level\"]}')
print(f'风险事件: {result[\"events\"]}')
print(f'操作建议: {result[\"action\"]}')
"
```

**评估的8类指标（只检测不扣分）：**

| 指标 | 数据源 | 🟢 normal | 🟡 watch | 🔴 risk | 🚨 sell |
|------|--------|-----------|----------|---------|---------|
| 股东人数 | 东方财富API | 持平 | 小幅增加 | 大幅增加 | - |
| 北向资金 | 东方财富API | 正常 | 连续流出 | 持续大幅流出 | - |
| 均线跌破 | K线数据 | 均线上方 | 跌破20日线 | 跌破60/120日线 | - |
| 成交量 | K线数据 | 正常 | 持续缩量 | 放量下跌 | - |
| 高位回调 | K线数据 | - | 回调20-30% | 回调>30% | - |
| 公告风险 | 东方财富API | 正常公告 | 风险提示 | - | 立案/造假/暴雷 |
| 负债率 | 财务数据 | <65% | 65-80% | >80% | - |
| 利润增长 | 财务数据 | 正增长 | 增速放缓(<10%) | 负增长 | 大跌(<-30%) |

**⚠️ V2改动说明**：
1. 风险评估不再参与评分（消除双重扣分）
2. 风险等级只影响操作建议，不影响股票排名
3. 突破位计算改用60日高点（而非120日），并增加回调幅度判断
4. K线数据列名兼容中英文（d/o/c/h/l/v vs 日期/开盘/收盘/最高/最低/成交量）

### 回测

```bash
cd ~/Pictures/选股 && python3 backtest.py --top 10
```

### 买卖提示

```bash
cd ~/Pictures/选股 && python3 alerts.py
```

详见 `references/trading-rules.md`。

### 缓存一年数据

```bash
cd ~/Pictures/选股 && python3 cache_year_data.py
```

支持断点续传，中断后再跑会接着来。

## 仓位分配（每池独立）

**每个池子独立分配仓位，互不影响：**

| 池子 | 买入规则 | 仓位 |
|------|----------|------|
| 第一池（稳健） | Top5 | 等额各20% |
| 第二池（成长） | Top5 | 分级：A级10-15%, B级5-10%, C级2-5% |

**第二池分级规则：**
- 第1-2名：A级（最强）→ 10-15%
- 第3-4名：B级 → 5-10%
- 第5名：C级 → 2-5%

**输出标注：**
- 🟢 买入建议（前5名，标注仓位级别）
- 🟡 观察（6-10名）
- ⚪ 备选（11-20名）

CSV包含「池子」和「建议」列，方便追踪。

## 数据架构

```
数据层（共享）
├── stocklist.json (6000+只，已去重)
├── quarterly.json (基本面)
├── weekly.json (K线/龙虎榜/大宗)
└── kline_year.json (年线备选)

规则层（独立）
├── 第一池规则：资金35%+趋势25%+成长20%+估值15%+分红5%
└── 第二池规则：资金35%+成长30%+趋势20%+行业15%

结果层（独立）
├── 第一池Top20 → 买入前5（等额20%）
└── 第二池Top20 → 买入前5（分级A/B/C）

执行层（统一）
└── 周五出信号 → 周一开盘执行
```

**关键点：**
- 数据是共享的，两个池子用同一套缓存
- 规则是独立的，不同权重和筛选条件
- 结果是独立的，各自Top20
- 执行是统一的，都是周一开盘买
- **数据安全**：核心文件写入前自动备份（见 `references/data-security.md`）

pool2_screener.py复用第一池的stocklist缓存（已去重），不需要单独获取股票列表。

| 数据 | 频率 | 说明 |
|------|------|------|
| 股票列表 | 当天有效 | 缓存在 stocklist.json |
| K线/龙虎榜/大宗交易 | 每周刷新 | `--force` 强制刷新 |
| 季度财务数据 | 每季度刷新 | `--refresh-quarterly` |
| 一年K线 | 手动缓存 | cache_year_data.py |

## 定时任务（Cron Jobs）

```
周五 15:30    stock_screener.py --weekly（第一池）+ pool2_screener.py（第二池）+ update_watchlist.py（出信号）
周一 09:35    capture_execution.py（采集执行价）
周二 09:35    capture_execution.py（对比采集）
每天 09:00    risk_monitor.py（风险监控）
```

**注意**：周五需要分别运行两个池子的脚本，不要只跑一个。

**⚠️ 报告格式**：两个池子的报告必须分开出，不要合并成一份。用户原话："我觉得报告可以分两份，卡池1一份报告，卡池2一份报告"。

不要设每日价格更新——这是周频策略，日更会导致频繁交易。

## 行业集中度限制（Portfolio Construction Rule）

选股Top5可能高度集中在同一行业（如第一池4只有色金属），板块轮动时一起跌。行业集中度限制强制每个行业最多N只，分散风险。

### 选股逻辑（必须按此顺序）

1. 按综合分数从高到低排序
2. 遍历排序列表，检查该股票行业已被选入几只
3. 如果该行业 < 限制数 → 选入，行业计数+1
4. 如果该行业 = 限制数 → 跳过，看下一只
5. 选满5只为止

**⚠️ 不能简单用分数替补**：不能因为某只股票分数高就直接补上，必须先检查行业。用户原话："你替补的就是按分数排名啊"——正确做法是在其他行业中找分数最高的替补。

### 回测结果（2026-06-22 ~ 2026-07-03，两周数据）

| 池子 | 无限制 | 行业≤2 | 行业≤3 |
|------|--------|--------|--------|
| 第一池(稳健) | -5.56% | **-2.99%** | -5.44% |
| 第二池(成长) | -6.23% | +0.79%* | -6.23% |

*花园生物+31.34%是偶然（60分低分高风险），不代表规则本身有效。

### 关键发现

1. **行业≤2在第一池有效**：分散到公用事业/化工/新能源，减少集中风险
2. **行业≤2在第二池有风险**：替补股票分数低（60分），单只暴涨不能复制
3. **行业≤3几乎没效果**：第二池电子元器件占10/30只，≤3还是选了3只电子
4. **核心问题**：某行业占比过高时，≤3根本分散不了，需要≤2甚至≤1

### 使用建议

- 行业≤2是保守但有效的规则
- 接受低分替补的风险（可能更差也可能更好）
- 单只股票暴涨是偶然，不能作为规则有效性的依据
- 需要更长时间回测验证（建议至少4-8周）

详细回测脚本见 `references/portfolio-construction.md`。

## 回测方法论

回测必须模拟真实使用场景：**每月重跑评分 → 出提示 → 按提示操作 → 追踪收益**

❌ 错误做法：选Top10然后持有12个月不动
✅ 正确做法：每月重新评分，跌出Top20就卖，新进Top10就买，用真实股价算盈亏

回测脚本：
- `backtest_full_system.py` — 完整交易模拟（每月重评+买卖+资产追踪）
- `backtest_monthly_reports.py` — 12份月度报告（每月Top10的排名变化轨迹）
- `backtest_60d.py` — 60天短期回测（用完整数据含龙虎榜/大宗交易）
- `backtest_hold12m.py` — 简化版（只看选股日Top10持有不动，有未来数据偏差）

回测报告在 `results/monthly_reports/` 和 `results/backtest_60d_reports/`。

## 买卖提示系统

`alerts.py` 同时输出 **B规则（推荐）** 和 **A规则（对照）** 两套建议：

```bash
cd ~/Pictures/选股 && python3 alerts.py
```

输出格式：
```
【B规则（推荐）】
  买入候选：10只  卖出候选：0只

【A规则（对照）】
  买入候选：10只  卖出候选：5只

--- A规则额外卖出（B规则暂不卖）---
  ⚡ XXXXX — 跌出Top20
```

需要至少2周数据才能出完整提示。第一周只出买入候选。

详见 `references/trading-rules.md`。

## 数据缓存策略

- **股票列表**：当天有效（`data/stocklist.json`），含科创板用 `pool2_stocklist.json`
- **K线/龙虎榜/大宗交易**：每周刷新（`data/weekly.json`）
- **季度财务**：每季度刷新（`data/quarterly.json`）
- **一年K线**：手动缓存（`data/kline_year.json`），用 `cache_year_data.py`，支持断点续传

## 买卖规则（B规则 — 当前默认）

### 稳健池卖出
1. **连续2周跌出Top20** → 第1周观察，第2周触发B规则卖出（保留1周在表里），第3周移除
2. **评分暴跌>15分**（绝对分数变化）
3. 连续4周评分下降

### 成长池卖出
1. 评分<70
2. 连续两周评分下降
3. 连续2周跌出Top20（同上，第3周移除）

### A规则已淘汰
A规则（跌出Top20立刻卖）因交易148次/3个月太频繁被淘汰。alerts.py同时输出A/B两套供对比。

详见 `references/trading-rules.md`。

### 实盘追踪流程（周频策略）

**核心原则**：这是周频策略（Weekly Strategy），不是日频。每日更新会导致频繁交易。

### 完整流程

| 时间 | 动作 | 脚本 |
|------|------|------|
| 周五 15:30 | 第一池评分 | `stock_screener.py --weekly` |
| 周五 15:30 | 第二池评分 | `pool2_screener.py` |
| 周五 15:30 | 周度追踪 | `update_watchlist.py` |
| 周六 | 用户review | - |
| 周一 09:35 | 采集开盘价（执行价） | `capture_execution.py` |
| 周一 11:35 | 采集上午收盘价 | `capture_execution.py` |
| 周一 13:35 | 采集下午价格 | `capture_execution.py` |
| 周二 09:35 | 对比采集 | `capture_execution.py` |
| 周二 11:35/13:35 | 对比采集 | `capture_execution.py` |
| 周一/二 | 用户执行买入/卖出 | - |
| 每天 09:00 | 风险监控 | `risk_monitor.py` |

**⚠️ capture_execution.py采集范围**：同时采集两个池子的Top20（共40只），不只是买入建议的前5只。第一池和第二池的执行价都要记录。

### 价格区分

- **信号价**（周五收盘价）：选股依据
- **执行价**（周一/二开盘价）：实际买入价
- **滑点**：执行价 - 信号价，用于以后优化买入区间

### 为什么周一+周二都采集

对比两天开盘价，验证"等一天是否更划算"。积累几周数据后分析规律。

**⚠️ 初步结论（2026-06-23数据）**：75%的股票（30/40只）周一开盘价更便宜，等待一天平均多付+3.54%。追高最严重：花园生物+29.41%、株冶集团+20.99%、南大光电+15.44%。**信号产生后应当日立即挂单**，等待次日买入平均多付3-4%。仅少数电子/材料类个股（矩子科技-6%、顺络电子-5.65%）周二低开，等待有小幅收益。

**⚠️ 两池滑点差异（2026-06-29数据）**：第一池(稳健)滑点普遍±1%以内，执行质量好；第二池(成长)滑点波动显著更大（国瓷材料+6.99%、南大光电+6.09%）。**执行策略应区分池子**：稳健池可直接挂单，成长池需设价格上限（如信号价+3%以内）或分批买入，避免开盘追高。

### 风险监控（每日）

```bash
cd ~/Pictures/选股 && python3 risk_monitor.py
```

扫描Top20持仓的重大风险事件（证监会立案/财务造假/暴雷/减持）。
关键词粗筛 + LLM判断（过滤正常公告如"董事会决议"）。

### 追踪脚本

```bash
# 周五15:30自动运行（cron job已设置）
cd ~/Pictures/选股 && python3 update_watchlist.py

# 周一/二09:35采集执行价（cron job已设置）
cd ~/Pictures/选股 && python3 capture_execution.py
```

**⚠️ 追踪表机制（v2 - 持久化JSON）**：

追踪表存为 `state/watchlist.json`，核心原则：**只增不减，除非第3周才删除**。

| weeks_out | 状态 | 说明 |
|-----------|------|------|
| 0 | ✅在Top20 | 正常持有 |
| 1 | 🟡观察 | 第1周掉出Top20，不操作 |
| 2 | 🚨触发B规则卖出 | **保留1周在表里，因为持股客户需要看到卖出信号才能操作** |
| 3 | 🗑️移除 | 从追踪表和飞书表格中删除 |

- 回归Top20的股票 `weeks_out` 重置为0
- **无上限**，自然淘汰控制大小（最坏情况约60只峰值，之后稳定~40）
- 新进Top20的股票自动加入追踪表
- 掉出Top20的不删除，只递增weeks_out

**⚠️ 3周生命周期的原因**：持股客户需要看到卖出信号才能操作，所以触发B规则后必须保留一周给他们看。

### 飞书文件夹
- token: `G3sFfLWiYlb7Z5dGUAbcNVotnqc`

#### 上传CSV到飞书
```python
# 读token
with open(os.path.expanduser('~/.hermes/profiles/main/feishu_user_token.json')) as f:
    token = json.load(f)['access_token']

# multipart上传
boundary = "----FormBoundary"
body = [
    f"--{boundary}".encode(),
    b'Content-Disposition: form-data; name="file_name"', b'', filename.encode(),
    f"--{boundary}".encode(),
    b'Content-Disposition: form-data; name="parent_type"', b'', b'explorer',
    f"--{boundary}".encode(),
    b'Content-Disposition: form-data; name="parent_node"', b'', FOLDER_TOKEN.encode(),
    f"--{boundary}".encode(),
    b'Content-Disposition: form-data; name="size"', b'', str(len(file_data)).encode(),
    f"--{boundary}".encode(),
    f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode(),
    b'Content-Type: text/csv', b'', file_data,
    f"--{boundary}--".encode()
]
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/drive/v1/files/upload_all",
    data=b"\r\n".join(body),
    headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"}
)
```

#### 创建飞书电子表格并写入数据
```python
# 1. 创建表格
create_body = json.dumps({"title": "选股Top20-双池独立", "folder_token": FOLDER_TOKEN}).encode()
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets',
    data=create_body,
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
    method='POST'
)
result = json.loads(urllib.request.urlopen(req).read())
spreadsheet_token = result['data']['spreadsheet']['spreadsheet_token']

# 2. 获取sheet ID
req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query',
    headers={'Authorization': f'Bearer {token}'}
)
sheets = json.loads(urllib.request.urlopen(req).read())['data']['sheets']
sheet_id = sheets[0]['sheet_id']

# 3. 重命名sheet
rename_body = json.dumps({"requests": [{"updateSheet": {"properties": {"sheetId": sheet_id, "title": "第一池(稳健)"}}}]}).encode()
req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update',
    data=rename_body, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}, method='POST'
)
urllib.request.urlopen(req)

# 4. 写入数据（CSV行 → 二维数组）
import csv, io
with open(csv_file, encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))
write_body = json.dumps({"valueRange": {"range": f"{sheet_id}!A1:L21", "values": rows[:21]}}).encode()
req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values',
    data=write_body, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}, method='PUT'
)
urllib.request.urlopen(req)

# 5. 添加第二池sheet（同理）
add_body = json.dumps({"requests": [{"addSheet": {"properties": {"title": "第二池(成长)", "index": 1}}}]}).encode()
req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update',
    data=add_body, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}, method='POST'
)
new_sheet_id = json.loads(urllib.request.urlopen(req).read())['data']['replies'][0]['addSheet']['properties']['sheetId']
# 写入第二池数据...
```

#### Token过期处理
- 详见 `feishu-token-refresh` skill
- 一键刷新：`python3 -c "..."` (见该skill)
- refresh_token有效期30天

#### ⚠️ 每次采集执行价后必须更新飞书表格
采集完数据后，必须同步更新飞书电子表格，否则表格数据会过时。

```python
# 采集后更新飞书表格的流程：
# 1. 刷新token（如果401）
# 2. 读取execution_*.csv
# 3. 读取飞书表格现有数据
# 4. 添加开盘价、当前价、滑点三列
# 5. 写回飞书

# 注意：第二池有"热门"列是布尔值(True/False)，飞书API不支持
# 必须先转成字符串：str(v) if isinstance(v, bool) else v
```

### ⚠️ Cron Job Prompt必须包含明确的卖出判断规则

**问题**：cron job prompt只说"列出卖出候选"，但没有告诉agent怎么判断卖出。agent看到累计跌就自己判断卖出，而不是按B规则。（见Pitfall #28）

**正确做法**：cron job prompt中必须写出B规则卖出条件：
- 稳健池：连续2周跌出Top20 → 才卖
- 成长池：评分<70 或 连续两周评分下降 或 连续2周跌出Top20
- 其他情况（如累计跌）不触发卖出
- 不满足条件就写"无卖出候选"

**教训**：agent不会自动知道B规则，必须在prompt中明确写出。验证方法：如果一只股票评分还在Top20，不可能同时满足卖出条件（见Pitfall #29）。

### ⚠️ 执行价采集后必须同步飞书表格

`capture_execution.py` 采集完数据后，**必须**将结果同步到飞书电子表格，否则表格数据过时无意义。

**飞书表格Token**：`APv3sZM02h4DQrt8Bcrclin4nfW`
**Sheet结构**：Sheet1=第一池(稳健), Sheet2=第二池(成长)

**同步流程**（在capture_execution.py采集完成后立即执行）：
1. 先跑 `date` 确认当前日期（触发date-check skill）
2. 刷新飞书token（如过期）
3. 读取 `state/execution_YYYY-MM-DD_HHMM.csv`
4. 将开盘价、当前价、滑点三列更新到飞书表格对应行
5. 确认写入成功

**⚠️ date-check**：执行任何日期相关操作前，必须先加载 `date-check` skill 并运行 `date` 确认。不要凭记忆猜日期，不要从文件名推断日期。

**⚠️ 执行价数据不能覆盖**：飞书表格中已有的历史执行价数据（如周一的开盘价/当前价/滑点）不能被新数据覆盖。正确做法：
- 第一次写入：列名为 `开盘价`、`当前价`、`滑点`
- 后续写入（如周二数据）：追加新列，列名改为 `周一开盘价`、`周二开盘价` 等，保留所有历史数据
- 飞书表格列结构随采集次数动态扩展，不覆盖旧列

### Cron Jobs

| Job ID | 名称 | 时间 | 说明 |
|--------|------|------|------|
| `ef5fd4661f3a` | 选股周报-周五出信号 | 周五 15:30 | 评分+追踪+信号 |
| `fd972743a70e` | 执行价采集-周一开盘 | 周一/二 09:35 | 采集开盘价（第一池+第二池）+ 同步飞书表格 |
| `a9d6260641b5` | 风险监控-每日 | 每天 09:00 | 扫描风险事件 |

## Common Pitfalls

1. **CSV代码丢失前导零**：pandas读CSV默认int64，`000426`变`426`。必须 `dtype={"代码": str}` + `.str.zfill(6)`
2. **系统代理阻断API**：macOS Clash代理(127.0.0.1:7897)会拦截东方财富API。所有curl调用用 `--noproxy '*'` 绕过，或用新浪API替代
3. **K线缓存不完整**：首次运行第二池会补全3000+只K线，约15分钟，耐心等待
4. **提示系统需要2周数据**：第一周只出买入候选，第二周开始有完整买入/卖出/换仓提示
5. **score函数返回值**：details里是字符串（如"1.8x✓"）不能sum()。必须用单独计分变量（cap_score, growth_score等）分别累加
6. **科创板重复代码**：新浪API科创板(kcb)可能返回重复代码，必须 `drop_duplicates(subset="代码")`
7. **股票列表缓存**：加了stocklist.json缓存（当天有效），避免每次都重新拉6000+只
8. **年数据缓存**：cache_year_data.py支持断点续传，约60分钟缓存全市场一年K线
9. **回测必须每月重评分**：不能选Top10持有不动，必须模拟每月重新评分+买卖，否则有未来数据偏差。第一月=默认已有持仓（不是空仓开始）
10. **龙虎榜数据可能为空**：缓存过期时为0条，选股质量下降但不影响运行
11. **龙虎榜/大宗交易API日期过滤失效**：东方财富API的 `filter=(TRADE_DATE>='...')` 用URL编码会返回0条。解决：不带filter拉全部数据，本地Python过滤日期
12. **回测脚本对比**：backtest_12month.py用简化评分（无龙虎榜/大宗交易历史数据），结果偏保守。backtest_b_default_hold.py用完整数据+B规则，结果更真实
13. **长任务进度汇报**：用户要求50%/80%/100%汇报，不要频繁报告（省tokens）
14. **调试时不要改规则**：修bug只改代码逻辑，不改评分权重/筛选阈值/买卖规则。用户明确纠正过"你先把规则改回去"。改了规则就不是在修bug了。
15. **风险监控关键词要精确**："董事"会匹配正常董事会公告，必须用"立案/财务造假/暴雷"等精确关键词。LLM负责过滤正常公告。
16. **新浪K线API可用，东方财富K线API被代理阻断**：push2his.eastmoney.com返回空响应。用 `money.finance.sina.com.cn` 的 `CN_MarketData.getKLineData` 接口。
17. **CSV有BOM头**：读取时用 `encoding='utf-8-sig'`，否则第一列列名会带 `﻿` 前缀导致 KeyError。
18. **实时行情API优先级**：腾讯 `qt.gtimg.cn` 最稳定（GBK编码需 `decode('gbk')`），东方财富 `push2.eastmoney.com` 经常返回空，新浪 `hq.sinajs.cn` 有时挂。capture_execution.py 已实现多API备用。
19. **脚本必须先测试再上cron**：手动跑通确认输出正确后再设定时任务。否则cron失败无声无息。
20. **交易时段检查**：采集开盘价脚本必须先判断是否在交易时段（9:30-11:30, 13:00-15:00），非交易时段运行会拿到空数据。
21. **日期不要凭记忆猜**：遇到日期相关问题先跑 `date` 命令确认。已创建 `date-check` skill 自动触发。
22. **stocklist.json有重复**：曾出现5410只但去重后只有4587只的情况。加载时必须 `drop_duplicates(subset="代码")`。
23. **kline_year.json格式不同**：年线用缩写键名（d/o/c/h/l/v），pool2_screener.py需要转换为标准格式（日期/开盘/收盘/最高/最低/成交量）才能用于评分。
24. **必须保护核心数据文件**：stocklist.json、weekly.json、quarterly.json、kline_year.json等核心缓存文件直接修改会丢失数据。已实现`data_security.py`模块，写入前自动备份（保留最近3版本），损坏时自动从备份恢复。`save_json()`和`load_json()`已集成安全层，无需手动备份。
25. **不要凭印象断言不存在**：用户说"之前创建过"时，必须先用session_search查历史记录+工具搜索飞书/文件系统，不能直接说"没找到"。上次因为没搜就说飞书没有选股表格，被用户用截图打脸。
26. **执行价数据不能覆盖**：飞书表格中已有的历史执行价不能被新数据覆盖。第一次写入用`开盘价/当前价/滑点`，后续追加新列（`周一开盘价/周二开盘价`等），保留所有历史数据便于对比。
27. **日期不要从文件名推断**：文件名如`execution_2026-06-23`不代表今天就是6/23。必须先加载`date-check` skill运行`date`确认。用户原话："你那个日期的skill，好像没有生效"。
28. **报告生成时不要自己判断卖出**：agent生成周报时，只按脚本输出的Top20排名判断买入建议。卖出候选必须严格按B规则判断，不能看到"累计跌"就列为卖出。B规则：稳健池连续2周跌出Top20才卖，成长池评分<70/连续两周评分下降/连续2周跌出Top20才卖。累计跌不触发卖出。脚本本身不生成卖出候选，卖出判断完全由cron job prompt控制。
29. **卖出判断要检查评分一致性**：如果一只股票评分还在Top20（如48分排第5），不可能同时满足卖出条件。用户原话：如果满足卖出标准，为啥评分还是48分，不可能那么高的。这是检验卖出逻辑是否正确的快速方法。
30. **K线数据列名中英文不同**：kline_year.json用缩写键名（d/o/c/h/l/v），而risk_assessment.py需要兼容中英文列名。代码中用 `close_col = "收盘" if "收盘" in kline_df.columns else "c"` 做兼容。不要假设列名一定是中文。
31. **风险评估会显著影响评分**：红色信号扣15分，可能导致排名大幅下降。例如原评分41分的股票，有两个红色信号（均线+突破）后调整为26分，从Top10掉到Top20外。这是预期行为，不是bug。
32. **飞书表格信息已存入memory**：表格token=APv3sZM02h4DQrt8Bcrclin4nfW，位于三板斧文件夹(G3sFfLWiYlb7Z5dGUAbcNVotnqc)。Sheet1=第一池(稳健)id=4df71e，Sheet2=第二池(成长)id=LVwKQ。A-L=基础数据，M-R=执行价。数据需手动更新。
33. **风险评估不能参与评分（双重扣分问题）**：评分系统已经因为均线跌破等因素扣分了，如果风险系统再扣分，同一个事件会被计算两次。例如：趋势模块因跌破MA60扣了5分，风险模块又扣15分，实际扣了20分。V3设计：评分反映股票质量，风险反映操作建议，两者独立。
34. **突破位计算要用近期高点而非120日绝对高点**：如果用120日最高价的95%作为突破位，对于从高位大幅回调的股票（如从37.95跌到23.55），突破位36.05和当前价差距太大不合理。V3改用60日高点，并增加回调幅度判断：回调>20%时标记为"大幅回调"而非"跌破突破位"。
35. **行业集中度限制不能简单用分数替补**：选Top5时加行业限制，不能因为某只股票分数高就直接补上，必须先检查该行业是否已满。正确做法：按分数降序遍历，跳过行业已满的股票，从其他行业中找分数最高的替补。用户原话："你替补的就是按分数排名啊"——指出了这个错误。见 `references/portfolio-construction.md`。
36. **低分替补的风险**：行业限制选出的替补股票分数可能更低（如花园生物60分 vs 被替换的快克智能62分），单只股票暴涨是偶然，不能作为规则有效性的依据。用户原话："花园生物是个例，一个评分太低的风险很高"。
37. **新浪API返回GBK编码**：用 `result.stdout.decode('gbk', errors='ignore')` 解码，不能用默认UTF-8。CSV文件用 `encoding='utf-8-sig'` 读取（处理BOM头）。
38. **平均分门槛在行业集中时无效**：先选Top3/4算平均分，低于平均分不能入选，选不够取消行业限制用最高分替补。但当某行业占比过高时（如第二池电子元器件53%），取消限制后替补还是同行业，平均分门槛形同虚设。需要配合行业限制使用，不能单独依赖。见 `references/portfolio-construction.md`。
39. **回测分析必须写日志**：完成后写日志到 `选股/logs/YYYY-MM-DD_主题.md`，记录背景、数据、过程、结论、待办。脚本保存到 `选股/scripts/`。用户原话："后面阅读知道今天发生的事情就可以了"。
40. **创建追踪表时必须保留已有的掉出股票**：watchlist.json不存在时首次创建，不能只放当前Top20。必须先查上周Top20中哪些已掉出，加回watchlist并设置正确的weeks_out。用户原话："你忘记了吗，就是这两只，这周没数据，你不会删掉了吧"。正确做法：对比上周和本周的Top20，找出差异，手动补入掉出的股票。
41. **weeks_out必须从实际掉出时间算起**：不能默认给weeks_out=1。要查历史数据确认股票是哪周掉出的。如：6/27在Top20，7/3掉出，7/10还在外面 → weeks_out=2（已触发B规则），不是1。用户原话："你看看这周这两只股票有没有触发规则b"。
42. **飞书表格卖出信号必须保留一周给客户看**：触发B规则卖出后不能立即从飞书表格删除，持股客户需要看到信号才能操作。weeks_out=2标记卖出，weeks_out=3才移除。用户原话："因为你这周更新了，卖出的信息，持股的客户是需要去看数据的，所以需要给他们看一周。"
40. **B规则追踪用持久化JSON，不要复杂化**：用户纠正了我最初设计的"检测消失股票+dropped_tracking"方案，改为最简单的方案——追踪表只增不减，掉出Top20的加weeks_out，连续2周触发B规则，第3周才删除。核心教训：**简单方案 > 复杂方案**，用户说"你首先最初的top20的表格，如果有一只掉出去，不能把他从表格剔除，除非触发规则b卖出"。
41. **触发B规则后必须保留1周给客户看**：持股客户需要看到卖出信号才能操作，所以weeks_out=2时标记"触发B规则卖出"但不删除，第3周（weeks_out=3）才从表里移除。用户原话："因为你这周更新了卖出的信息，持股的客户是需要去看数据的，所以需要给他们看一周"。
42. **重建追踪表时不能丢已有的追踪状态**：创建新的watchlist.json时必须先把已掉出的股票加回来。初始化前先检查上周哪些股票已掉出，手动补入并设置正确的weeks_out。计算weeks_out时要对比多周数据（不能只看最近两周），否则会算错（如金房能源只看7/3→7/10算成1，实际6/27就在Top20→7/3掉出→7/10还在外面=2）。
43. **更新飞书表格前必须先读追踪表**：不能只写Top20就覆盖，要先把watchlist.json里weeks_out>=1的股票一起写入。否则观察中和触发B规则的股票会被删掉，客户看不到卖出信号。
44. **追踪表不能人为设上限**：最坏情况（每周全部换新）需要60个槽位，第3周旧的才会被清除。用自然淘汰控制大小，不要加MAX_WATCHLIST之类的硬编码上限。
45. **创建新状态文件前必须检查历史数据**：不能凭空新建JSON就覆盖。如果之前有追踪状态（如Feishu表格里的观察/卖出标记），必须先读取再合并，不能丢失历史状态。
46. **飞书token刷新用tenant_token做Bearer**：refresh_access_token接口需要`Authorization: Bearer {tenant_token}`，不是user_token。标准流程：先获取tenant_access_token → 用它刷新user_access_token → 保存新token。

## Verification Checklist

- [ ] `stock_screener.py --weekly` 正常输出Top20（使用缓存时秒出）
- [ ] `pool2_screener.py` 正常输出Top30（无重复）
- [ ] `backtest.py` 能计算1周/2周/1月收益
- [ ] `alerts.py` 能导入评分并生成提示
- [ ] `cache_year_data.py` 支持断点续传
