#!/usr/bin/env python3
"""小米MIMO视频理解脚本"""

import os
import sys
import json
import base64
import ssl
from pathlib import Path
from urllib.request import Request, urlopen


def load_env():
    """加载.env文件"""
    env_path = os.path.expanduser('~/AppData/Local/hermes/.env')
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()


def analyze_video(video_path: str, question: str, fps: int = 2) -> str:
    """
    分析视频内容
    
    Args:
        video_path: 视频文件路径
        question: 要问的问题
        fps: 帧率（每秒采样帧数，默认2）
    
    Returns:
        分析结果文本
    """
    load_env()
    
    # 读取视频文件
    with open(video_path, 'rb') as f:
        video_b64 = base64.b64encode(f.read()).decode()
    
    # 获取视频MIME类型
    ext = Path(video_path).suffix.lower()
    mime_map = {
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.mkv': 'video/x-matroska',
    }
    mime_type = mime_map.get(ext, 'video/mp4')
    
    # 构建data URL
    video_data_url = f"data:{mime_type};base64,{video_b64}"
    
    # API配置 - 使用小米MIMO Token Plan
    api_key = os.environ.get('XIAOMI_API_KEY', '')
    base_url = 'https://token-plan-cn.xiaomimimo.com'
    
    url = f"{base_url}/v1/chat/completions"
    
    # 构建请求
    payload = json.dumps({
        "model": "mimo-v2.5",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    },
                    {
                        "type": "video_url",
                        "video_url": {
                            "url": video_data_url
                        },
                        "fps": fps,
                        "media_resolution": "default"
                    }
                ]
            }
        ],
        "max_tokens": 4000
    }).encode()
    
    # 发送请求
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = Request(url, data=payload, headers={
        'Content-Type': 'application/json',
        'api-key': api_key
    })
    
    with urlopen(req, timeout=300, context=ctx) as resp:
        result = json.loads(resp.read())
    
    # 提取回复
    for choice in result.get('choices', []):
        message = choice.get('message', {})
        content = message.get('content', '')
        if content:
            return content
    
    return "无法获取视频分析结果"


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python mimo_video.py <视频路径> <问题> [fps]")
        print("示例: python mimo_video.py video.mp4 '分析这个口播视频的节奏和语气' 2")
        sys.exit(1)
    
    video_path = sys.argv[1]
    question = sys.argv[2]
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    result = analyze_video(video_path, question, fps)
    print(result)