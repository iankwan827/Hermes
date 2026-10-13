# PackyAPI images/edits 接口备忘

## 发现时间：2026-06-05

## 背景
PackyAPI 的 OpenAI 格式 key（`OPENAI_API_KEY`）走的是 "image channel"，
不支持 Gemini 的 `/v1beta/models/{model}:generateContent` 端点。
报错：`image channel does not support gemini chat`

## 正确的调用方式

### 端点
```
POST https://www.packyapi.com/v1/images/edits
```

### 认证
```
Authorization: Bearer <OPENAI_API_KEY>
```
（不是 `x-goog-api-key`）

### 请求格式
`multipart/form-data`，字段：
- `model` — 模型名（如 `gpt-image-2`）
- `prompt` — 描述想要的背景/效果
- `image` — 输入图片文件（multipart file upload）

### 响应
```json
{
  "data": [{
    "url": "https://..."
  }]
}
```
需要再 GET 下载图片。

## 模型可用性
- 模型列表通过 `GET https://www.packyapi.com/v1beta/models` 查询（用 `x-goog-api-key` header）
- 但列表中的模型名不一定都能用于 `images/edits`，需要逐个测试
- `gpt-image-2` 可用于 `images/edits`（2026-06-05 验证）
- `gemini-3-pro-image-preview` 曾可用但已下架
- 模型可用性会变，脚本应支持用户手动选择

## 独立脚本
`D:/hermes-agent/电商/gemini_ecommerce.py` — 封装了完整流程：
- 首次运行输入 key，自动保存
- 查询模型列表供选择，选完保存
- 自动创建 `image/` 文件夹读取图片
- 输出到 `output/` 文件夹
