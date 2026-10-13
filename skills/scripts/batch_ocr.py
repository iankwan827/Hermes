#!/usr/bin/env python3
"""
批量图片文字提取 - 将imge/目录下所有图片转为markdown文档
用法: 先通过run_batch.py设置环境变量，再调用此脚本
输出: D:/hermes-agent/imge/docs/*.md + _report.json
"""
import os, sys, json, base64, urllib.request, urllib.error, struct, time

API_KEY=os.environ.get("XIAOMI_API_KEY", "")
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
MODEL = "mimo-v2.5"
IMG_DIR = "D:/hermes-agent/imge"
OUT_DIR = "D:/hermes-agent/imge/docs"


def get_png_size(path):
    try:
        with open(path, 'rb') as f:
            f.read(16)
            w = struct.unpack('>I', f.read(4))[0]
            h = struct.unpack('>I', f.read(4))[0]
        return w, h
    except:
        return 0, 0


def encode_image(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].lower()
    mime = {".jpg":"image/jpeg",".jpeg":"image/jpeg",".png":"image/png",
            ".gif":"image/gif",".webp":"image/webp",".bmp":"image/bmp"}.get(ext,"image/jpeg")
    return f"data:{mime};base64,{b64}"


def call_api(messages):
    headers = {"Authorization": f"Bearer {API_KEY}", "api-key": API_KEY, "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": messages, "max_tokens": 8000, "temperature": 0.1}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/chat/completions", data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "text": result["choices"][0]["message"]["content"]}
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}: {e.read().decode('utf-8',errors='replace')[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_text(image_path, prompt):
    data_url = encode_image(image_path)
    # Format 1: Standard OpenAI multimodal
    messages = [{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": data_url}},
    ]}]
    r = call_api(messages)
    if r["success"]: return r
    # Format 2: Responses style
    messages = [{"role": "user", "content": [
        {"type": "input_text", "text": prompt},
        {"type": "input_image", "image_url": data_url},
    ]}]
    return call_api(messages)


def process_image(filename):
    image_path = os.path.join(IMG_DIR, filename)
    w, h = get_png_size(image_path)
    ratio = h / w if w > 0 else 0
    size_kb = os.path.getsize(image_path) // 1024
    if ratio > 4:
        prompt = "这是一张非常长的滚动截图。请完整提取图片中的所有文字内容，保持原始排版结构（标题、段落、表格、列表等）。不要遗漏任何内容，不要编造任何内容。"
    elif ratio > 2.5:
        prompt = "这是一张较长的截图。请完整提取图片中的所有文字内容，保持原始排版结构。不要遗漏任何内容，不要编造任何内容。"
    else:
        prompt = "请完整提取图片中的所有文字内容，保持原始排版结构。不要遗漏任何内容，不要编造任何内容。"
    print(f"  [{filename[:12]}...] {w}x{h} ratio={ratio:.1f} {size_kb}KB", flush=True)
    result = extract_text(image_path, prompt)
    if result["success"]:
        out_file = os.path.join(OUT_DIR, filename.replace(".png", ".md"))
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(result["text"])
        print(f"    OK -> {len(result['text'])} chars", flush=True)
        return {"file": filename, "success": True, "chars": len(result["text"]), "ratio": ratio}
    else:
        print(f"    FAIL: {result['error'][:80]}", flush=True)
        return {"file": filename, "success": False, "error": result["error"], "ratio": ratio}


def main():
    if not API_KEY:
        print("错误: XIAOMI_API_KEY 未设置"); sys.exit(1)
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted([f for f in os.listdir(IMG_DIR) if f.endswith(".png")])
    print(f"共 {len(files)} 张图片待处理, 输出: {OUT_DIR}")
    results = []
    for i, f in enumerate(files):
        print(f"[{i+1}/{len(files)}]", end="", flush=True)
        results.append(process_image(f))
        if i < len(files) - 1: time.sleep(1)
    ok = sum(1 for r in results if r["success"])
    fail = sum(1 for r in results if not r["success"])
    total_chars = sum(r.get("chars", 0) for r in results)
    print(f"\n{'='*50}\n完成: {ok} 成功, {fail} 失败, 总字符: {total_chars:,}")
    with open(os.path.join(OUT_DIR, "_report.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
