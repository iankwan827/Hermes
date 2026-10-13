#!/usr/bin/env python3
"""
从docx文件中提取嵌入的图片，然后用Xiaomi Vision API识别文字
输出按日期命名的md文件

用法:
    python extract_from_docx.py

配置:
    - NOTES_DIR: docx源文件夹（walk搜索所有子目录）
    - OUTPUT_DIR: 输出md文件的目录
    - 图片提取后自动判断是否需要切割（高宽比>3 或 h>8000）
"""
import os, sys, zipfile, json, base64, urllib.request, struct, time, re
from PIL import Image, UnidentifiedImageError
import io, warnings
warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)
Image.MAX_IMAGE_PIXELS = None

# ====== 配置 ======
env_path = os.path.expanduser("~/AppData/Local/hermes/.env")
api_key = ""
with open(env_path) as f:
    for line in f:
        if line.strip().startswith("XIAOMI_API_KEY"):
            api_key = line.strip().split("=", 1)[1]
            break

BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
MODEL = "mimo-v2.5"
NOTES_DIR = "E:/SD/skill/recording/notes"  # 源文件夹
OUTPUT_DIR = "D:/hermes-agent/imge_v3/docs"  # 输出目录
SEG_HEIGHT = 1500  # 切割段高

CN_NUMS = {
    '二十五': 25, '二十四': 24, '二十三': 23, '二十二': 22, '二十一': 21,
    '二十': 20, '十九': 19, '十八': 18, '十七': 17, '十六': 16,
    '十五': 15, '十四': 14, '十三': 13, '十二': 12, '十一': 11,
    '十': 10, '九': 9, '八': 8, '七': 7, '六': 6,
    '五': 5, '四': 4, '三': 3, '二': 2, '一': 1,
}

def cn_to_ar(cn_str):
    for key, val in CN_NUMS.items():
        if cn_str.endswith(key):
            return val
    return None

def extract_course_number(text):
    patterns = [r'拾易八字课([一二三四五六七八九十百]+)', r'第(\d+)课']
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1)
            try: return int(num_str)
            except: pass
            ar = cn_to_ar(num_str)
            if ar: return ar
    return None

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

def extract_images_from_docx(docx_path, output_dir):
    images = []
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            for name in z.namelist():
                if name.startswith('word/media/') and name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    img_data = z.read(name)
                    img_name = os.path.basename(name)
                    img_path = os.path.join(output_dir, img_name)
                    with open(img_path, 'wb') as f: f.write(img_data)
                    images.append(img_path)
    except Exception as e:
        print(f"  Error extracting from {docx_path}: {e}")
    return images

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
    if w is None or w == 0 or h == 0:
        print(" [skip:bad-dim]", end="", flush=True)
        return None
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
            y_end = min(y + SEG_HEIGHT, h)
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
    if not api_key:
        print("Error: XIAOMI_API_KEY not set")
        sys.exit(1)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    docx_files = []
    for root, dirs, files in os.walk(NOTES_DIR):
        for f in files:
            if f.endswith('.docx') and '转写结果' in f:
                docx_files.append(os.path.join(root, f))
    print(f"Found {len(docx_files)} docx files")
    results = []
    for i, docx_path in enumerate(docx_files):
        print(f"\n[{i+1}/{len(docx_files)}] {os.path.basename(docx_path)}")
        path_parts = docx_path.replace('\\', '/').split('/')
        date_folder = None
        for part in path_parts:
            if re.match(r'\d{4}-\d{2}-\d{2}', part):
                date_folder = part
                break
        temp_dir = os.path.join(OUTPUT_DIR, f"temp_{date_folder}")
        os.makedirs(temp_dir, exist_ok=True)
        images = extract_images_from_docx(docx_path, temp_dir)
        print(f"  Extracted {len(images)} images")
        if not images: continue
        all_texts = []
        for j, img_path in enumerate(images):
            print(f"    Image {j+1}/{len(images)}...", end="", flush=True)
            try:
                text = process_image(img_path)
                if text:
                    all_texts.append(text)
                    print(f" OK {len(text)} chars")
                else:
                    print(" FAIL")
            except Exception as e:
                print(f" ERROR: {e}")
            time.sleep(0.5)
        if all_texts:
            combined_text = "\n\n---\n\n".join(all_texts)
            course_num = extract_course_number(combined_text)
            if course_num:
                out_name = f"第{course_num}课_{date_folder}.md"
            else:
                out_name = f"{date_folder}_{os.path.basename(docx_path).replace('.docx', '')}.md"
            out_path = os.path.join(OUTPUT_DIR, out_name)
            with open(out_path, 'w', encoding='utf-8') as f: f.write(combined_text)
            print(f"  -> Saved as {out_name} ({len(combined_text)} chars)")
            results.append({"file": docx_path, "date": date_folder, "course": course_num, "chars": len(combined_text)})
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    with open(os.path.join(OUTPUT_DIR, "_extraction_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n{'='*50}")
    print(f"Extraction complete: {len(results)} files processed")

if __name__ == "__main__":
    main()
