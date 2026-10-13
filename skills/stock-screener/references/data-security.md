# 数据安全机制

## 核心文件保护

以下文件在写入前自动备份（保留最近3版本）：
- `stocklist.json`
- `quarterly.json`
- `weekly.json`
- `kline_year.json`
- `history.json`
- `score_history.json`

## 备份目录

`data/backups/` 目录下，文件名格式：
```
{原文件名}_{时间戳}.json
例：stocklist_20260622_101015.json
```

## 自动恢复

读取JSON时如果文件损坏，自动从最新备份恢复。

## 使用方法

```python
from data_security import safe_write_json, safe_read_json

# 安全写入（自动备份）
safe_write_json("stocklist.json", data)

# 安全读取（损坏时自动恢复）
data = safe_read_json("stocklist.json")

# 查看备份
from data_security import list_backups
backups = list_backups("stocklist.json")

# 从备份恢复
from data_security import restore_from_backup
restore_from_backup("stocklist_20260622_101015.json")
```

## 集成方式

`stock_screener.py` 和 `pool2_screener.py` 的 `save_json()` 和 `load_json()` 已集成安全层，无需手动调用。

## 注意事项

- 只保护核心数据文件，结果文件（CSV、JSON报告）不受保护
- 备份最多保留3个版本，自动清理旧备份
- 恢复时会先备份当前文件（以防万一）
