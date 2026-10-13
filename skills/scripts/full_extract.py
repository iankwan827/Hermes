#!/usr/bin/env python3
"""
完整提取脚本 - 切割长图 + 大max_tokens + 分段合并
用法: python full_extract.py [图片目录] [输出目录]
默认: 图片目录=D:/hermes-agent/imge  输出目录=D:/hermes-agent/imge/docs_v2
"""
import os, sys, json, base64, urllib.request, urllib.error, struct, time, io

# 加载API KEY
env_path = os.path.expanduser("~/AppData/Local/hermes/.env")
api_key = ""
with open(env_path) as f:
    for line in f:
        if line.strip().startswith("XIAOMI_API_KEY"):
            api_key = line.strip().split("=", 1)[1]
            break

BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
MODEL = "mimo-v2.5"
IMG_DIR = sys.argv[1] if len(sys.argv) > 1 else "D:/hermes-agent/imge"
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "D:/hermes-agent/imge/docs_v2"
SEG_HEIGHT = 3000  # 每段切割高度（像素）

os.makedirs(OUT_DIR, exist_ok=True)

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
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}.get(ext, "image/png")
    return f"data:{mime};base64,{b64}"

def encode_pil_image(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

def call_api(messages, max_tokens=16000):
    headers = {"Authorization": f"Bearer {api_key}", "api-key": api_key, "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.1}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/chat/completions", data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "text": result["choices"][0]["message"]["content"]}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"success": False, "error": f"HTTP {e.code}: {body[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def split_image(img_path, seg_height):
    from PIL import Image
    img = Image.open(img_path)
    w, h = img.size
    segments = []
    y = 0
    while y < h:
        y_end = min(y + seg_height, h)
        segment = img.crop((0, y, w, y_end))
        segments.append((y, y_end, segment))
        y = y_end
    return segments

def extract_from_image(img_path, prompt, max_tokens=16000):
    data_url = encode_image(img_path)
    messages = [{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": data_url}},
    ]}]
    return call_api(messages, max_tokens)

def extract_from_segment(seg_img, seg_idx, total, max_tokens=16000):
    data_url = encode_pil_image(seg_img)
    prompt = f"这是长图的第{seg_idx+1}/{total}段（从上到下）。请完整提取这段图片中的所有文字，保持排版。"
    messages = [{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": data_url}},
    ]}]
    return call_api(messages, max_tokens)

def process_image(filename):
    img_path = os.path.join(IMG_DIR, filename)
    w, h = get_png_size(img_path)
    ratio = h / w if w > 0 else 0
    size_kb = os.path.getsize(img_path) // 1024
    need_split = ratio > 3 or h > 8000

    print(f"  {filename[:16]}... {w}x{h} ratio={ratio:.1f} {size_kb}KB {'[切割]' if need_split else '[整张]'}", flush=True)

    if not need_split:
        prompt = "请完整提取图片中的所有文字内容，保持原始排版结构（标题、段落、表格、列表等）。不要遗漏任何内容。"
        r = extract_from_image(img_path, prompt, max_tokens=16000)
        if r["success"]:
            return r["text"]
        else:
            print(f"    FAIL: {r['error'][:60]}", flush=True)
            return None
    else:
        segments = split_image(img_path, SEG_HEIGHT)
        print(f"    切割为{len(segments)}段", flush=True)
        all_texts = []
        for i, (y_start, y_end, seg_img) in enumerate(segments):
            print(f"    段{i+1}/{len(segments)} (y:{y_start}-{y_end})...", flush=True, end="")
            r = extract_from_segment(seg_img, i, len(segments), max_tokens=16000)
            if r["success"]:
                all_texts.append(r["text"])
                print(f" OK {len(r['text'])}字", flush=True)
            else:
                print(f" FAIL: {r['error'][:40]}", flush=True)
            time.sleep(1)
        return "\n\n---\n\n".join(all_texts)

def main():
    if not api_key:
        print("错误: XIAOMI_API_KEY 未设置")
        sys.exit(1)

    files = sorted([f for f in os.listdir(IMG_DIR) if f.endswith(".png")])
    print(f"共 {len(files)} 张图片")
    print(f"输出目录: {OUT_DIR}")
    print(f"切割阈值: 高宽比>3 或 高度>8000px")
    print()

    results = []
    for i, f in enumerate(files):
        print(f"[{i+1}/{len(files)}]", flush=True)
        text = process_image(f)
        if text:
            out_file = os.path.join(OUT_DIR, f.replace(".png", ".md"))
            with open(out_file, "w", encoding="utf-8") as fh:
                fh.write(text)
            results.append({"file": f, "success": True, "chars": len(text)})
            print(f"    -> {len(text)} 字", flush=True)
        else:
            results.append({"file": f, "success": False})
        time.sleep(1)

    ok = sum(1 for r in results if r["success"])
    fail = sum(1 for r in results if not r["success"])
    total_chars = sum(r.get("chars", 0) for r in results)
    print()
    print(f"="*50)
    print(f"完成: {ok} 成功, {fail} 失败")
    print(f"总字符: {total_chars:,}")

if __name__ == "__main__":
    main()
