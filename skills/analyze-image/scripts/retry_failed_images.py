#!/usr/bin/env python3
"""
重试docx提取中失败的图片
用法: python retry_failed_images.py <docx路径> <失败图片索引，逗号分隔>

示例:
    python retry_failed_images.py "E:/path/to/file.docx" "2,15"
"""
import os, sys, zipfile, json, base64, urllib.request, time
from PIL import Image
import io, warnings, shutil
warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)
Image.MAX_IMAGE_PIXELS = None

env_path = os.path.expanduser("~/AppData/Local/hermes/.env")
api_key = ""
with open(env_path) as f:
    for line in f:
        if line.strip().startswith("XIAOMI_API_KEY"):
            api_key = line.strip().split("=", 1)[1]
            break

BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
MODEL = "mimo-v2.5"

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
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_image_dimensions(img_path):
    try:
        with Image.open(img_path) as img: return img.size
    except: return None, None

def downscale_image(img_path, max_pixels=20_000_000):
    try: img = Image.open(img_path)
    except: return None
    w, h = img.size
    total = w * h
    if total <= max_pixels: return img
    scale = (max_pixels / total) ** 0.5
    new_w, new_h = max(int(w * scale), 1), max(int(h * scale), 1)
    print(f" [downscale {w}x{h}->{new_w}x{new_h}]", end="", flush=True)
    return img.resize((new_w, new_h), Image.LANCZOS)

def process_image(img_path):
    w, h = get_image_dimensions(img_path)
    if w is None or w == 0 or h == 0: return None
    ratio = h / w if w > 0 else 0
    need_split = ratio > 3 or h > 8000
    if not need_split:
        file_size = os.path.getsize(img_path)
        if file_size > 20 * 1024 * 1024:
            img = downscale_image(img_path)
            data_url = encode_pil_image(img)
            img.close()
        else:
            with open(img_path, 'rb') as f: raw = f.read()
            b64 = base64.b64encode(raw).decode()
            data_url = f"data:image/png;base64,{b64}"
        prompt = "请完整提取图片中的所有文字内容，保持原始排版结构。不要遗漏任何内容。"
        messages = [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]}]
        r = call_api(messages, max_tokens=16000)
        return r["text"] if r["success"] else None
    else:
        img = downscale_image(img_path)
        if img is None: img = Image.open(img_path)
        w, h = img.size
        segments = []
        y = 0
        while y < h:
            y_end = min(y + 1500, h)
            segments.append(img.crop((0, y, w, y_end)))
            y = y_end
        all_texts = []
        for i, seg_img in enumerate(segments):
            data_url = encode_pil_image(seg_img)
            prompt = f"这是长图的第{i+1}/{len(segments)}段。请完整提取这段图片中的所有文字，保持排版。"
            messages = [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]}]
            r = call_api(messages, max_tokens=16000)
            if r["success"]: all_texts.append(r["text"])
            time.sleep(0.5)
        img.close()
        return "\n\n---\n\n".join(all_texts) if all_texts else None

def main():
    if len(sys.argv) < 3:
        print("用法: python retry_failed_images.py <docx路径> <失败图片索引，逗号分隔>")
        print("示例: python retry_failed_images.py file.docx '2,15'")
        sys.exit(1)
    
    docx_path = sys.argv[1]
    failed_indices = [int(x.strip()) - 1 for x in sys.argv[2].split(',')]  # 转为0-indexed
    
    temp_dir = os.path.join(os.path.dirname(docx_path), "_retry_temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    images = []
    with zipfile.ZipFile(docx_path, 'r') as z:
        for name in z.namelist():
            if name.startswith('word/media/') and name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                img_data = z.read(name)
                img_path = os.path.join(temp_dir, os.path.basename(name))
                with open(img_path, 'wb') as f: f.write(img_data)
                images.append(img_path)
    
    print(f"Total images: {len(images)}")
    results = {}
    
    for idx in failed_indices:
        if idx >= len(images):
            print(f"Index {idx+1} out of range, skipping")
            continue
        img_path = images[idx]
        print(f"\n--- Retry image {idx+1} ---")
        text = process_image(img_path)
        if text:
            print(f"  OK: {len(text)} chars")
            results[idx+1] = text
        else:
            print(f"  FAIL again")
        time.sleep(1)
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    if results:
        print(f"\n成功重试 {len(results)}/{len(failed_indices)} 张")
        print("结果:")
        for idx, text in sorted(results.items()):
            print(f"\nImage {idx}:")
            print(text[:200] + "..." if len(text) > 200 else text)
    else:
        print("\n全部重试失败")

if __name__ == "__main__":
    main()
