#!/usr/bin/env python3
"""
Xiaomi Token Plan Vision - 直接调用 API 测试多模态格式
用法: python xiaomi_vision.py <图片路径> <提示词>
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


def call_api(messages, label=""):
    """调用 API 并打印详细信息"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "api-key": API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.1,
    }

    print(f"\n{'='*60}")
    print(f"尝试格式: {label}")
    print(f"API Key: {API_KEY[:8]}...")
    print(f"Messages count: {len(messages)}")
    for i, msg in enumerate(messages):
        role = msg.get("role", "?")
        content = msg.get("content", "")
        if isinstance(content, str):
            print(f"  msg[{i}] role={role} content=string({len(content)} chars)")
        elif isinstance(content, list):
            print(f"  msg[{i}] role={role} content=list({len(content)} parts)")
            for j, part in enumerate(content):
                ptype = part.get("type", "?")
                if ptype == "text":
                    print(f"    part[{j}] type=text text={part.get('text', '')[:50]}...")
                elif ptype == "image_url":
                    url = part.get("image_url", {})
                    if isinstance(url, dict):
                        url_str = url.get("url", "")[:60]
                    else:
                        url_str = str(url)[:60]
                    print(f"    part[{j}] type=image_url url={url_str}...")
                else:
                    print(f"    part[{j}] type={ptype} ...")
        else:
            print(f"  msg[{i}] role={role} content={type(content)}")
    print(f"Payload size: ~{len(json.dumps(payload)) // 1024} KB")

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
            print(f"Status: {resp.status}")
            print(f"Response: {body[:500]}")
            result = json.loads(body)
            content = result["choices"][0]["message"]["content"]
            return {"success": True, "analysis": content}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Status: {e.code}")
        print(f"Response: {body[:500]}")
        return {"success": False, "error": f"HTTP {e.code}: {body[:200]}", "label": label}
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "error": str(e), "label": label}


def main():
    if len(sys.argv) < 3:
        print("用法: python xiaomi_vision.py <图片路径> <提示词>")
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2]

    if not API_KEY:
        print("错误: XIAOMI_API_KEY 环境变量未设置")
        sys.exit(1)

    if not os.path.isfile(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        sys.exit(1)

    data_url = encode_image(image_path)
    print(f"图片: {image_path} ({os.path.getsize(image_path) // 1024} KB)")
    print(f"Base64 长度: {len(data_url) // 1024} KB")

    # ── 格式1: 标准 OpenAI 多模态 (text + image_url list) ──
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]
    }]
    r = call_api(messages, "标准OpenAI格式 (list content)")
    if r.get("success"):
        print(f"\n✅ 格式1成功!")
        print(r["analysis"])
        return

    # ── 格式2: content 为 string ──
    messages = [{
        "role": "user",
        "content": prompt,
    }]
    r = call_api(messages, "纯文本 (无图片, 测试API连通性)")
    if r.get("success"):
        print(f"\n✅ 格式2成功 (纯文本)!")
        print(r["analysis"])
        print("\n⚠️ 纯文本可以通，多模态格式不通。")
        return

    # ── 格式3: content 为 list，但用 input_image ──
    messages = [{
        "role": "user",
        "content": [
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image_url": data_url},
        ]
    }]
    r = call_api(messages, "input_text + input_image (Responses风格)")
    if r.get("success"):
        print(f"\n✅ 格式3成功!")
        print(r["analysis"])
        return

    print("\n❌ 所有格式都失败了")


if __name__ == "__main__":
    main()
