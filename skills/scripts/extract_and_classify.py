#!/usr/bin/env python3
"""
提取图片 -> 检查内容里的课程编号/内容类型 -> 分类
用法: python extract_and_classify.py
"""
import os, sys, json, base64, urllib.request, urllib.error, struct, time, re, io

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
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "D:/hermes-agent/imge/docs_classified"
SEG_HEIGHT = 3000

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

def classify_content(text):
    text_lower = text[:2000]
    categories = [
        (r'案例|问题描述|命盘表格|八字：', '案例课'),
        (r'五行|金木水火土|天干|地支', '五行课'),
        (r'婚姻|夫妻|配偶|桃花|婚外情', '婚姻课'),
        (r'事业|职业|工作|官杀|升职', '事业课'),
        (r'财运|财星|发财|投资|理财', '财运课'),
        (r'子女|孩子|生育|怀孕|流产', '子女课'),
        (r'健康|疾病|心脏|肝胆|肾', '健康课'),
        (r'风水|阳宅|方位|床下', '风水课'),
        (r'格局|从格|化气格|专旺格', '格局课'),
    ]
    for pattern, name in categories:
        if re.search(pattern, text_lower): return name
    return '其他'

def get_png_size(path):
    try:
        with open(path, 'rb') as f:
            f.read(16)
            w = struct.unpack('>I', f.read(4))[0]
            h = struct.unpack('>I', f.read(4))[0]
        return w, h
    except: return 0, 0

def encode_image(path):
    with open(path, "rb") as f: b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].lower()
    mime = {".jpg":"image/jpeg",".jpeg":"image/jpeg",".png":"image/png"}.get(ext,"image/png")
    return f"data:{mime};base64,{b64}"

def encode_pil_image(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

def call_api(messages, max_tokens=16000):
    headers = {"Authorization": f"Bearer {api_key}", "api-key": api_key, "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.1}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/chat/completions", data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "text": result["choices"][0]["message"]["content"]}
    except Exception as e: return {"success": False, "error": str(e)}

def split_image(img_path, seg_height):
    from PIL import Image
    img = Image.open(img_path)
    w, h = img.size
    segments = []
    y = 0
    while y < h:
        y_end = min(y + seg_height, h)
        segments.append((y, y_end, img.crop((0, y, w, y_end))))
        y = y_end
    return segments

def process_image(filename):
    img_path = os.path.join(IMG_DIR, filename)
    w, h = get_png_size(img_path)
    ratio = h / w if w > 0 else 0
    need_split = ratio > 3 or h > 8000
    print(f"  {filename[:16]}... {w}x{h} ratio={ratio:.1f} {'[cut]' if need_split else '[full]'}", flush=True)

    if not need_split:
        prompt = "请完整提取图片中的所有文字内容，保持原始排版结构。不要遗漏任何内容。"
        data_url = encode_image(img_path)
        r = call_api([{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": data_url}}]}])
        return r["text"] if r["success"] else None
    else:
        segments = split_image(img_path, SEG_HEIGHT)
        print(f"    split into {len(segments)} segments", flush=True)
        all_texts = []
        for i, (y_s, y_e, seg_img) in enumerate(segments):
            print(f"    seg {i+1}/{len(segments)}...", flush=True, end="")
            r = call_api([{"role": "user", "content": [{"type": "text", "text": f"这是长图的第{i+1}/{len(segments)}段。请完整提取文字。"}, {"type": "image_url", "image_url": {"url": encode_pil_image(seg_img)}}]}])
            if r["success"]: all_texts.append(r["text"]); print(f" OK {len(r['text'])}chars", flush=True)
            else: print(" FAIL", flush=True)
            time.sleep(1)
        return "\n\n---\n\n".join(all_texts)

def main():
    if not api_key: print("Error: XIAOMI_API_KEY not set"); sys.exit(1)
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted([f for f in os.listdir(IMG_DIR) if f.endswith(".png")])
    print(f"Total {len(files)} images")

    rename_map = {}
    for i, f in enumerate(files):
        print(f"[{i+1}/{len(files)}]", flush=True)
        text = process_image(f)
        if text:
            out_file = os.path.join(OUT_DIR, f.replace(".png", ".md"))
            with open(out_file, "w", encoding="utf-8") as fh: fh.write(text)
            course_num = extract_course_number(text)
            if course_num: key = course_num; label = f"第{course_num}课"
            else: key = classify_content(text); label = key
            print(f"    -> {label} ({len(text)} chars)", flush=True)
            if key not in rename_map: rename_map[key] = []
            rename_map[key].append(f)
        time.sleep(1)

    with open(os.path.join(OUT_DIR, "_rename_map.json"), "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in rename_map.items()}, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 50)
    print("Classification results:")
    print("=" * 50)
    for k in sorted([x for x in rename_map.keys() if isinstance(x, int)]):
        print(f"\n第{k}课 ({len(rename_map[k])} images):")
        for fn in rename_map[k]: print(f"  {fn}")
    for k in sorted([x for x in rename_map.keys() if isinstance(x, str)]):
        print(f"\n{k} ({len(rename_map[k])} images):")
        for fn in rename_map[k]: print(f"  {fn}")
    print(f"\nTotal: {sum(len(v) for v in rename_map.values())} files classified")

if __name__ == "__main__": main()
