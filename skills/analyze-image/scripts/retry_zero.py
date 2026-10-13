#!/usr/bin/env python3
"""
重试0字节的图片文件
用法: python retry_zero.py [目录路径]
默认重试 D:/hermes-agent/imge/docs/ 中的0字节.md文件
"""
import os, sys, json, base64, urllib.request, urllib.error, struct, time

def load_api_key():
    env_path = os.path.expanduser("~/AppData/Local/hermes/.env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("XIAOMI_API_KEY"):
                return line.split("=", 1)[1]
    return ""

API_KEY = load_api_key()
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
MODEL = "mimo-v2.5"

def get_mime(path):
    ext = os.path.splitext(path)[1].lower()
    return {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
            ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp"}.get(ext, "image/jpeg")

def encode_image(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{get_mime(path)};base64,{b64}"

def call_api(messages):
    headers = {"Authorization": f"Bearer {API_KEY}", "api-key": API_KEY, "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": messages, "max_tokens": 8000, "temperature": 0.1}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/chat/completions", data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "text": result["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def find_zero_files(docs_dir):
    """找到0字节或极小的.md文件，返回对应的图片路径"""
    img_dir = os.path.dirname(docs_dir.rstrip("/"))
    zero_files = []
    for f in os.listdir(docs_dir):
        if not f.endswith(".md") or f.startswith("_") or f == "INDEX.md":
            continue
        md_path = os.path.join(docs_dir, f)
        if os.path.getsize(md_path) < 100:  # 小于100字节视为失败
            img_file = f.replace(".md", ".png")
            img_path = os.path.join(img_dir, img_file)
            if os.path.exists(img_path):
                zero_files.append((img_path, md_path))
    return zero_files

def retry_file(img_path, md_path):
    """重试单个文件"""
    print(f"重试: {os.path.basename(img_path)}", flush=True)
    data_url = encode_image(img_path)
    messages = [{"role": "user", "content": [
        {"type": "text", "text": "请完整提取图片中的所有文字内容，保持原始排版结构。不要遗漏任何内容。"},
        {"type": "image_url", "image_url": {"url": data_url}},
    ]}]
    r = call_api(messages)
    if r["success"] and len(r["text"]) > 10:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(r["text"])
        print(f"  OK -> {len(r['text'])} chars", flush=True)
        return True
    else:
        print(f"  FAIL: {r.get('error', 'empty')[:80]}", flush=True)
        return False

def main():
    if not API_KEY:
        print("错误: XIAOMI_API_KEY 未设置")
        sys.exit(1)

    docs_dir = sys.argv[1] if len(sys.argv) > 1 else "D:/hermes-agent/imge/docs"
    zero_files = find_zero_files(docs_dir)
    
    if not zero_files:
        print("没有需要重试的文件")
        return
    
    print(f"找到 {len(zero_files)} 个需要重试的文件")
    success = 0
    for img_path, md_path in zero_files:
        if retry_file(img_path, md_path):
            success += 1
        time.sleep(2)
    
    print(f"\n重试完成: {success}/{len(zero_files)} 成功")

if __name__ == "__main__":
    main()
