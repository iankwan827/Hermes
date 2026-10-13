#!/usr/bin/env python3
"""
MiniMax Image Generation API Client
"""
import os
import sys
import json
import base64
import urllib.request
import ssl
import argparse

# SSL context for Windows
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_api_key():
    """Get MiniMax API key from .env"""
    env_path = os.path.expanduser("~/AppData/Local/hermes/.env")
    api_key = ""
    with open(env_path) as f:
        for line in f:
            if line.strip().startswith("MINIMAX_CN_API_KEY"):
                api_key = line.strip().split("=", 1)[1]
                break
    return api_key

def generate_image(prompt, aspect_ratio="1:1", response_format="url"):
    """
    Generate image using MiniMax API
    
    Args:
        prompt: Text description of the image
        aspect_ratio: Image aspect ratio (1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16)
        response_format: Response format (url or base64)
    
    Returns:
        dict with success status and image URL or base64 data
    """
    api_key = get_api_key()
    if not api_key:
        return {"success": False, "error": "MINIMAX_CN_API_KEY not found"}
    
    url = "https://api.minimaxi.com/v1/image_generation"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "image-01",
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "response_format": response_format
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            result = json.loads(resp.read())
            
            if result.get("base_resp", {}).get("status_code") == 0:
                image_urls = result.get("data", {}).get("image_urls", [])
                if image_urls:
                    return {"success": True, "url": image_urls[0]}
                else:
                    return {"success": False, "error": "No image URLs in response"}
            else:
                return {"success": False, "error": result.get("base_resp", {}).get("status_msg", "Unknown error")}
    
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if hasattr(e, "read") else ""
        return {"success": False, "error": f"HTTP {e.code}: {error_body[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="MiniMax Image Generation")
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("--aspect-ratio", "-a", default="1:1", 
                       choices=["1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16"],
                       help="Image aspect ratio (default: 1:1)")
    parser.add_argument("--format", "-f", default="url", choices=["url", "base64"],
                       help="Response format (default: url)")
    parser.add_argument("--output", "-o", help="Save image to file (URL only)")
    
    args = parser.parse_args()
    
    result = generate_image(args.prompt, args.aspect_ratio, args.format)
    
    if result["success"]:
        if args.output and "url" in result:
            # Download and save image
            req = urllib.request.Request(result["url"])
            with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                with open(args.output, "wb") as f:
                    f.write(resp.read())
            print(json.dumps({"success": True, "file": args.output}))
        else:
            print(json.dumps(result))
    else:
        print(json.dumps(result))
        sys.exit(1)

if __name__ == "__main__":
    main()
