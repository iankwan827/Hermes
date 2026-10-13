---
name: astock-data
description: >
  A股选股系统：双池架构（稳健池+成长爆发池）。数据获取（akshare/新浪API）、
  评分系统、缓存策略、回测、买卖信号。龙虎榜、大宗交易、股东人数、财务指标等。
  触发词：「选股」「股票数据」「龙虎榜」「大宗交易」「股东人数」「财务数据」「akshare」「第二池」「回测」
triggers:
  - 选股
  - 股票数据
  - 龙虎榜
  - 大宗交易
  - 股东人数
  - 财务数据
  - akshare
  - A股
  - 第二池
  - 成长爆发池
  - pool2
  - 回测
  - backtest
---

# A股数据获取 (akshare)

通过 `akshare` Python库获取A股各类数据，用于选股系统和股票分析。

## 安装

```bash
uv pip install akshare
```

venv环境中需要在venv内安装，`--user` 安装不会被venv的python看到。

## 核心函数映射

### 龙虎榜（机构买卖）
```python
import akshare as ak
df = ak.stock_lhb_detail_em()
# 列名: 序号, 代码, 名称, 上榜日, 解读, 收盘价, 涨跌幅, 龙虎榜净买额, 龙虎榜买入额, 龙虎榜卖出额, ...
# "解读"字段包含机构买卖信息，如 "1家机构买入，成功率46.03%"
```

### 大宗交易（机构接盘）
```python
df = ak.stock_dzjy_mrmx()
# 列名: 序号, 交易日期, 证券代码, 证券简称, 成交价, 成交量, 成交额, 买方营业部, 卖方营业部
# 买方营业部可判断是否机构接盘
```

### 股东人数（持股集中度）
```python
df = ak.stock_circulate_stock_holder(symbol="000001")
# 列名: 截止日期, 公告日期, 编号, 股东名称, 持股数量, 占流通股比例, 股本性质
# 通过不同日期的持股数量变化判断筹码集中度
```

### 财务指标（ROE、净利润增长率、现金流等）
```python
df = ak.stock_financial_abstract(symbol="000001")
# 列名: 选项, 指标, 20260331, 20251231, ...
# 关键指标行:
#   净资产收益率(ROE)
#   归属母公司净利润增长率
#   经营现金流量净额
#   资产负债率
#   营业总收入增长率
```

### 北向资金
```python
# 函数名待确认，akshare版本迭代快，可能需要搜索:
funcs = [f for f in dir(ak) if 'north' in f.lower() or 'hgt' in f.lower()]
```

### 其他有用函数
```python
# 融资融券
ak.stock_margin_detail_info()  # 或搜索 'margin'

# 排行榜
ak.stock_rank_*  # 搜索 rank 相关函数
```

## 函数搜索技巧

akshare版本迭代快，函数名可能变化。搜索方法：
```python
# 按关键词搜索函数
funcs = [f for f in dir(ak) if 'lhb' in f.lower()]  # 龙虎榜
funcs = [f for f in dir(ak) if 'dz' in f.lower()]    # 大宗交易
funcs = [f for f in dir(ak) if 'holder' in f.lower()] # 股东
funcs = [f for f in dir(ak) if 'financ' in f.lower()] # 财务
```

## 选股系统10大核心指标对应

| 指标 | akshare函数 | 关键字段 |
|------|------------|---------|
| 龙虎榜机构净买入 | `stock_lhb_detail_em()` | 解读 |
| 大宗交易机构接盘 | `stock_dzjy_mrmx()` | 买方营业部 |
| 股东人数下降 | `stock_circulate_stock_holder()` | 持股数量变化 |
| ROE | `stock_financial_abstract()` | 净资产收益率(ROE) |
| 净利润增长率 | `stock_financial_abstract()` | 归属母公司净利润增长率 |
| 经营现金流 | `stock_financial_abstract()` | 经营现金流量净额 |
| 股价/均线/成交量 | 行情接口 | 待确认具体函数 |
| PE估值 | `stock_financial_abstract()` | 可计算 |
| 连续分红 | `stock_financial_abstract()` | 每股分红数据 |
| 资产负债率 | `stock_financial_abstract()` | 资产负债率 |

## 同花顺网页数据

同花顺数据页面（data.10jqka.com.cn）返回200但内容JS动态渲染，curl无法直接获取。
浏览器工具连接CDP超时时，可用AppleScript提取：
```bash
osascript -e 'tell application "Google Chrome" to execute active tab of front window javascript "document.body.innerText"'
```
前提：Chrome需开启「查看→开发者→允许Apple事件中的JavaScript」。

## ⚠️ 板块过滤（重要）

新浪API的 `node=hs_a` 会包含北交所（92xxx）股票，排在最前面，导致数据偏科。

**正确做法：分板块获取，排除科创板+北交所**

```python
# 板块节点映射
boards = [
    ("sh_a", "沪市主板"),   # 60xxxx
    ("sz_a", "深市主板"),   # 00xxxx  
    ("cyb", "创业板"),      # 30xxxx
]

# 排除的板块
# - 科创板 (688xxx)：门槛50万+
# - 北交所 (92xxx/8xxx)：门槛50万+
```

**验证数据（2026-06-21）：**
- sh_a: 2313只
- sz_a: 2320只
- cyb: 1399只
- 总计: 6032只（剔除后）

**注意：** Top20可能偏主板，因为大盘股更容易满足"市值>50亿+机构关注"条件。创业板小盘股如果没达到条件，就不应入选——这是评分机制的自然结果，不是数据缺失。

## ⚠️ 代理绕过（重要）

macOS系统代理（如Clash 127.0.0.1:7897）会导致东方财富API请求失败（服务器主动断开连接）。
akshare的requests库会自动读取系统代理，即使设置 `trust_env=False` 也无法绕过。

**解决方案：用curl + `--noproxy '*'` 直接请求API，或用新浪API替代。**

### curl绕过代理示例
```python
import subprocess, json
cmd = ["curl", "-sL", "--noproxy", "*", "--max-time", "10",
       "-H", "User-Agent: Mozilla/5.0",
       "https://push2his.eastmoney.com/api/qt/stock/kline/get?..."]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
data = json.loads(result.stdout)
```

### 新浪API替代（完全绕过代理）
新浪API不受代理影响，可直接用requests或curl访问：

```python
# 股票列表（分页，每页80只）
url = f"https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={page}&num=80&sort=symbol&asc=1&node=hs_a"

# K线数据（日线）
symbol = "sz000001"  # 深圳=sz, 上海=sh
url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=no&datalen=300"
# 返回: [{"day":"2025-01-02","open":"10.77","high":"10.81","low":"10.43","close":"10.47","volume":"1819597"}, ...]
```

**注意：新浪K线API只返回最近约300天数据（scale=240=日线），不是全量历史。**

### 选股脚本推荐数据源组合
| 数据 | 首选 | 备选 |
|------|------|------|
| 股票列表 | 新浪API | akshare(curl绕过代理) |
| K线行情 | 新浪API | akshare(curl绕过代理) |
| 实时行情 | **腾讯API**（最稳定） | 新浪API、东方财富API |
| 龙虎榜 | akshare(需绕过代理) | curl直连东方财富 |
| 大宗交易 | akshare(需绕过代理) | curl直连东方财富 |
| 财务数据 | akshare(走代理可能OK) | — |
| 北向资金 | akshare(需绕过代理) | — |

### 腾讯实时行情API（最稳定）
```python
# 格式: v_sh600961="1~株冶集团~600961~31.70~28.82~..."
# 字段: 0=市场 1=名称 2=代码 3=最新价 4=昨收 5=开盘 ... 33=最高 34=最低
url = f"https://qt.gtimg.cn/q={symbol}"
# ⚠️ 返回GBK编码，需 decode('gbk')
r = subprocess.run(["curl", "-s", "--noproxy", "*", url], capture_output=True)
text = r.stdout.decode('gbk', errors='ignore')
```

## 已验证的北向资金函数

```python
# 个股北向资金持仓历史
df = ak.stock_hsgt_individual_em(symbol="000001")
# 列名: 持股日期, 当日收盘价, 当日涨跌幅, 持股数量, 持股市值,
#        持股数量占A股百分比, 今日增持股数, 今日增持资金, 今日持股市值变化
# 用于判断北向资金是否持续增持

# 北向资金历史流向
df = ak.stock_hsgt_hist_em(symbol="沪股通")
# 列名: 日期, 当日成交净买额, 买入成交额, 卖出成交额, 历史累计净买额, ...
```

## 选股系统架构（双池 + 分层缓存）

系统分为两个池，策略和评分完全不同：
- **第一池（稳健池）**：`stock_screener.py` — 稳定盈利、长期复利
- **第二池（成长爆发池）**：`pool2_screener.py` — 资金启动、捕捉爆发

详见 `references/stock-screening-architecture.md`（第一池v2.1）、`references/pool2-rules.md`（第二池规则）和 `references/trading-signals.md`（买卖提示规则）

### 核心思路
- **每周更新40%**：龙虎榜、大宗交易、K线趋势、均线（数据变化快）
- **每季度更新60%**：ROE、利润增长、现金流、负债率、股东人数（数据变化慢）
- **每天1分钟**：检查停牌/暴雷/减持（纯监控，不评分）

### 文件结构
```
~/Pictures/选股/
├── stock_screener.py      # 主脚本（每周评分）
├── daily_check.py         # 每日检查
├── data/
│   ├── quarterly.json     # 季度数据缓存
│   ├── weekly.json        # 周数据缓存
│   └── portfolio.json     # 当前持仓Top5
└── results/               # 历史结果
```

### 使用方法
```bash
# 每周运行（首次约25分钟，后续读缓存约3分钟）
python3 stock_screener.py --weekly

# 每天运行（1分钟）
python3 stock_screener.py --daily
# 或
python3 daily_check.py

# 强制刷新季度数据
python3 stock_screener.py --refresh-quarterly
```

## 东方财富API（curl绕过代理）

akshare的requests库无法绕过系统代理，但东方财富API本身可用curl直接访问：

### 龙虎榜数据
```python
url = ("https://datacenter-web.eastmoney.com/api/data/v1/get?"
       "sortColumns=TRADE_DATE,SECURITY_CODE&sortTypes=-1,-1&pageSize=500&pageNumber=1"
       "&reportName=RPT_DAILYBILLBOARD_DETAILSNEW&columns=ALL&source=WEB&client=WEB"
       "&filter=(TRADE_DATE>='2026-04-22')")
# 返回: SECURITY_CODE(代码), SECURITY_NAME_ABBR(名称), TRADE_DATE(日期), ...
```

### 大宗交易数据
```python
url = ("https://datacenter-web.eastmoney.com/api/data/v1/get?"
       "sortColumns=TRADE_DATE,SECURITY_CODE&sortTypes=-1,-1&pageSize=500&pageNumber=1"
       "&reportName=RPT_DATA_BLOCKTRADE&columns=ALL&source=WEB&client=WEB")
```

### 使用curl调用
```python
import subprocess, json
cmd = ["curl", "-sL", "--noproxy", "*", "--max-time", "15",
       "-H", "User-Agent: Mozilla/5.0",
       "-H", "Referer: https://quote.eastmoney.com/",
       url]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
data = json.loads(result.stdout)
```

## Pitfalls

- akshare安装到 `--user` 不会被venv的python看到，必须在venv内安装
- **系统代理会拦截东方财富API请求**，akshare无法自动绕过，必须用curl或新浪替代
- 同花顺网页数据是JS动态加载，curl只拿到空壳HTML
- `stock_financial_abstract()` 返回的指标名是中文，需要按中文匹配
- 北向资金函数名随版本变化，需搜索确认（`dir(ak)` 搜索 'hsgt' 或 'north'）
- akshare某些接口可能被反爬，返回空数据或报错
- 新浪K线API的symbol格式：深圳=`sz000001`，上海=`sh600519`
- **首次运行季度数据缓存需约15分钟**（887只×0.1秒/只），后续读缓存几秒完成
- **龙虎榜API偶尔失败**（东方财富服务器限制），失败时跳过不影响整体评分
- **score函数返回值类型**：评分函数如果返回`(score, details)`，details里的值是字符串（如"1.8x✓"），不能直接`sum()`。要用单独的计分变量（`cap_score`, `growth_score`等）分别累加，最后返回时一起带出。
- **pool2科创板重复**：新浪API科创板(`kcb`)可能返回重复代码，必须`drop_duplicates(subset="代码")`去重。
- **CSV读取代码前导零丢失**：pandas默认int64，`000426`变`426`。读取时必须`dtype={"代码": str}` + `str.zfill(6)`。
- **K线缓存不完整**：首次运行会缺K线（863/2187只），需用`cache_year_data.py`补全。断点续传，约60分钟。
- **龙虎榜数据可能为空**：缓存过期或API限制时为0条，选股质量下降但不影响运行。
- **股票列表需缓存**：6000+只每次拉取耗时5分钟，加stocklist.json缓存（当天有效）秒出。
- **东方财富日期过滤返回0条**：URL编码`filter=(TRADE_DATE>='2026-04-22')`会返回空结果。必须**不带filter拉全部数据**，拉到超过目标日期后本地筛选。分页拉取，每页500条，检查最后一条日期是否已过目标日期。
- **新浪API返回GBK编码**：`curl`拿到的字节流是GBK不是UTF-8。用`r.stdout.decode("gbk")`而非`text=True`。实时行情接口`hq.sinajs.cn`尤其如此。
