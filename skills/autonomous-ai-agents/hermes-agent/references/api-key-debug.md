# API Key 调试参考

## 识别 .env 中的占位符 vs 真实 key

终端显示 `***` 可能是两种情况：

1. **真实 key 被 mask** — `MINIMAX_API_KEY=***`（真实 key 存在，Hermes 出于安全隐藏显示）
2. **占位符 literal 值** — `XIAOMI_API_KEY=***`（三个星号就是文件里的实际值，key 未写入）

**区分方法**：`cat -A` 能看到原始字符（包括不可见字符），直接判断值是 `*` 还是被 mask 的真实内容。

```bash
# 快速判断 key 是否真实存在
grep "^XIAOMI_API_KEY" ~/.hermes/.env | cat -A
# 有真实内容：XIAOMI_API_KEY=sk-xxxx...（cat -A 显示完整字符）
# 占位符：    XIAOMI_API_KEY=***   （三个星号就是 literal 值）
```

## 常见 .env key 格式

| Provider | Key 名 | Base URL |
|---|---|---|
| MiniMax (全球) | `MINIMAX_API_KEY` | `https://api.minimax.io/v1` |
| MiniMax (中国) | `MINIMAX_CN_API_KEY` | `https://api.minimaxi.com/anthropic` |
| Xiaomi MiMo | `XIAOMI_API_KEY` | `https://api.xiaomimimo.com/v1` |

## 写入 key 的正确方式

不要直接编辑 `.env`，用 Hermes CLI：

```bash
hermes config set secrets.minimax.api_key 你的key
hermes config set secrets.xiaomi.api_key 你的key
```

直接编辑 `.env` 可能不生效（配置文件优先级可能覆盖 `.env`）。

## API Key 真实性验证（curl 测试）

```bash
# Xiaomi
curl -s -X POST "https://api.xiaomimimo.com/v1/chat/completions" \
  -H "Authorization: Bearer 你的key" \
  -H "Content-Type: application/json" \
  -d '{"model":"minimaxi/m2.2-thinking","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'

# MiniMax 中国
curl -s -X POST "https://api.minimaxi.com/v1/text/chatcompletion_v2" \
  -H "Authorization: Bearer 你的key" \
  -H "Content-Type: application/json" \
  -d '{"model":"minimaxi/m2.2-thinking","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

预期：`{"error":{"message":"Invalid API Key"...}}` 表示 key 格式正确但无效；`"status_code":1004` + `"login fail"` 表示 key 格式/传入方式错误。
