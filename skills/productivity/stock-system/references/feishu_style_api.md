# 飞书表格样式API

## 设置字体颜色

```python
style_data = {
    "data": [
        {
            "ranges": "sheet_id!A21:Q21",  # 范围
            "style": {
                "fontColor": "#FF0000"  # 红色字体
            }
        }
    ]
}
req = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{SPREADSHEET}/styles_batch_update",
    data=json.dumps(style_data).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="PUT")
```

## 注意事项

- 外层键是 `data`（数组），不是 `appendStyle`
- 字体颜色用 `fontColor`，不是 `foreColor`
- 背景色用 `backgroundColor`
- 加粗用 `bold: true`
- 可以同时设置多个范围：`"ranges": "sheet_id!A21:Q21,sheet_id!A22:Q22"`

## 常用颜色

| 颜色 | hex |
|------|-----|
| 红色 | #FF0000 |
| 绿色 | #008000 |
| 橙色 | #FF8C00 |
| 蓝色 | #0000FF |
