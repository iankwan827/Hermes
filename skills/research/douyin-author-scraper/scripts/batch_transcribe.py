#!/usr/bin/env python3
"""批量转录视频为文字稿 - 一次加载Whisper模型，逐个处理。
用法: cd D:/hermes-agent && unset PYTHONHOME && /e/Python/python.exe -u scripts/batch_transcribe.py
输出: D:/videos/authors_transcripts/<author>/<vid>.txt
"""
import os, subprocess

INPUT_DIR = "D:/videos/authors"
OUTPUT_DIR = "D:/videos/authors_transcripts"
TEMP_AUDIO = "D:/videos/temp_audio.wav"

def main():
    import whisper
    
    print("加载Whisper模型...")
    model = whisper.load_model("small")
    print("模型加载完成")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    videos = []
    for author in os.listdir(INPUT_DIR):
        author_dir = os.path.join(INPUT_DIR, author)
        if not os.path.isdir(author_dir):
            continue
        out_author = os.path.join(OUTPUT_DIR, author)
        os.makedirs(out_author, exist_ok=True)
        
        for f in os.listdir(author_dir):
            if f.endswith(".mp4"):
                vid_path = os.path.join(author_dir, f)
                vid_name = f[:-4]
                transcript = os.path.join(out_author, f"{vid_name}.txt")
                if os.path.exists(transcript) and os.path.getsize(transcript) > 0:
                    continue
                videos.append((author, vid_name, vid_path, transcript))
    
    total = len(videos)
    print(f"待转录: {total} 个视频")
    
    ok = fail = 0
    for i, (author, vid_name, vid_path, transcript) in enumerate(videos):
        print(f"[{i+1}/{total}] {author}/{vid_name}", end=" ", flush=True)
        try:
            subprocess.run([
                "ffmpeg", "-i", vid_path, "-vn",
                "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                TEMP_AUDIO, "-y"
            ], capture_output=True, timeout=60)
            
            if not os.path.exists(TEMP_AUDIO) or os.path.getsize(TEMP_AUDIO) == 0:
                print("FAIL(音频)")
                fail += 1
                continue
            
            result = model.transcribe(TEMP_AUDIO, language="zh")
            with open(transcript, "w", encoding="utf-8") as f:
                f.write(result["text"])
            print(f"OK({len(result['text'])}字)")
            ok += 1
            os.remove(TEMP_AUDIO)
        except Exception as e:
            print(f"FAIL({e})")
            fail += 1
        
        if (i + 1) % 10 == 0:
            print(f"  --- 进度: {ok}/{i+1} 成功, {fail} 失败 ---")
    
    print(f"\n=== 完成 === 成功: {ok}, 失败: {fail}, 总计: {total}")
