# Xiaomi Token Plan Vision API 行为记录

## 已知限制

### 1. 单张图片处理能力
- **短图** (高宽比<2, 高度<6000px): 通常能完整提取，输出3000-8000字符
- **中等图** (高宽比2-3, 高度6000-10000px): 可能截断，输出2000-5000字符（应更多）
- **长图** (高宽比>3, 高度>10000px): 严重截断，输出可能只有应有量的30-50%

### 2. Base64编码体积
- 3MB PNG → ~4MB base64
- 5MB PNG → ~6.7MB base64
- API可能对请求体大小有限制

### 3. 空响应问题
- 约10-15%的图片可能返回空内容
- 常见于环境变量未正确加载时（重试时需确保API KEY已设置）
- 也可能是API临时限流

### 4. max_tokens影响
- max_tokens=8000: 短图够用，长图截断
- max_tokens=16000: 推荐值，覆盖绝大多数情况
- 更大的值可能被API拒绝

## 已验证的格式

标准OpenAI多模态格式可用：
```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "提示词"},
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
  ]
}
```

## 推荐的API调用参数
```python
{
    "model": "mimo-v2.5",
    "messages": [...],
    "max_tokens": 16000,
    "temperature": 0.1
}
```
