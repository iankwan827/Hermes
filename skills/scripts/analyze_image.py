#!/usr/bin/env python3
"""
图片分析脚本 - 通过 Xiaomi Vision API 分析图片
用法: python analyze_image.py <图片路径> [提示词]

自动尝试多种API格式，找到能用的那个。
"""
import sys
import json
import base64
import os
import urllib.request
import urllib.error

API_KEY = os.environ.get("XIAOMI_API_KEY", "")
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
MODEL = "mimo-v2.5"
DEFAULT_PROMPT = "请提取图片中的所有文字内容，如果没有文字则描述图片内容。"


def get_mime(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif",
        ".webp": "image/webp", ".bmp": "image/bmp",
    }.get(ext, "image/jpeg")


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    mime = get_mime(path)
    return f"data:{mime};base64,{b64}"


def call_api(messages) -> dict:
    """调用API，返回 {'success': bool, 'text': str, 'error': str}"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "api-key": API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 4000,
        "temperature": 0.1,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=data, headers=headers, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
            result = json.loads(body)
            text = result["choices"][0]["message"]["content"]
            return {"success": True, "text": text}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"success": False, "error": f"HTTP {e.code}: {body[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def try_formats(data_url: str, prompt: str) -> dict:
    """尝试多种消息格式，返回第一个成功的"""

    # 格式1: 标准 OpenAI 多模态 (list content)
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]
    }]
    r = call_api(messages)
    if r["success"]:
        return r

    # 格式2: Responses 风格 (input_text + input_image)
    messages = [{
        "role": "user",
        "content": [
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image_url": data_url},
        ]
    }]
    r = call_api(messages)
    if r["success"]:
        return r

    # 格式3: 图片作为单独user消息 (有些API支持)
    messages = [
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": data_url}},
        ]},
        {"role": "user", "content": prompt},
    ]
    r = call_api(messages)
    if r["success"]:
        return r

    return {"success": False, "error": "所有格式均失败"}


def main():
    if len(sys.argv) < 2:
        print("用法: python analyze_image.py <图片路径> [提示词]")
        print("示例: python analyze_image.py photo.png '提取文字'")
        sys.exit(1)

    image_path = sys.argv[1].strip('"').strip("'")
    prompt = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PROMPT

    if not API_KEY:
        print("错误: 环境变量 XIAOMI_API_KEY 未设置")
        sys.exit(1)

    if not os.path.isfile(image_path):
        print(f"错误: 文件不存在: {image_path}")
        sys.exit(1)

    size_kb = os.path.getsize(image_path) // 1024
    print(f"图片: {os.path.basename(image_path)} ({size_kb} KB)", file=sys.stderr)

    data_url = encode_image(image_path)
    result = try_formats(data_url, prompt)

    if result["success"]:
        print(result["text"])
    else:
        print(f"分析失败: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
