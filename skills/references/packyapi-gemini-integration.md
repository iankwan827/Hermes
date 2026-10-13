# PackyAPI Gemini 集成参考

## 端点信息

| 接口 | 端点 | 方法 |
|------|------|------|
| 模型列表 | `/v1/models` | GET |
| OpenAI 生图 | `/v1/images/generations` | POST |
| Gemini 生图 | `/v1beta/models/{model}:generateContent` | POST |

**Base URL:** `https://www.packyapi.com`（注意是 www，不是 api）

## 认证方式

```python
# OpenAI 端点
headers = {"Authorization": f"Bearer {api_key}"}

# Gemini 端点
headers = {"x-goog-api-key": api_key}
```

## Gemini 请求格式

```json
{
  "contents": [{
    "parts": [
      {"text": "Generate an image: ..."},
      {"inlineData": {"mimeType": "image/jpeg", "data": "<base64>"}}
    ]
  }],
  "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}
```

- `inlineData` 可选，传入原图用于图生图
- `responseModalities` 必须包含 `"IMAGE"` 才会返回图片
- 返回图片在 `candidates[0].content.parts[].inlineData.data`（base64）

## 可用生图模型

用户分组（gemini-slb）下的模型可能不同，需要在控制台确认。

已确认可用：
- `gemini-3-pro-image-preview` — 高质量
- `gemini-2.5-flash-image` — 快速

## 环境变量

```bash
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://www.packyapi.com/v1
```

## 注意事项

1. **SSL 问题：** 如果机器跑了 Clash（fake IP 模式），DNS 会解析到 198.18.0.44 导致 SSL 握手失败。解决：Clash 规则里加 `DOMAIN-SUFFIX,packyapi.com,DIRECT`
2. **分组限制：** 不同分组支持的模型不同，503 错误通常是模型不在当前分组
3. **Gemini 文字渲染：** 比 MiniMax 好很多，复杂中文也能正确渲染
4. **图生图保真度：** Gemini banana 的图生图保真度远超 MiniMax subject_ref
