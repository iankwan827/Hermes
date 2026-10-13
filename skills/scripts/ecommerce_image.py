#!/usr/bin/env python3
"""
E-commerce Product Image Generator using MiniMax API
Generate product images for e-commerce platforms with variations from a reference image.
"""
import os
import sys
import json
import base64
import urllib.request
import ssl
import argparse
from pathlib import Path

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


def get_base_url():
    """Get MiniMax base URL from .env"""
    env_path = os.path.expanduser("~/AppData/Local/hermes/.env")
    base_url = "https://api.minimaxi.com"
    with open(env_path) as f:
        for line in f:
            if line.strip().startswith("MINIMAX_CN_BASE_URL"):
                base_url = line.strip().split("=", 1)[1]
                if base_url.endswith("/anthropic"):
                    base_url = base_url[:-len("/anthropic")]
                break
    return base_url


def image_to_base64(image_path):
    """Convert image file to base64 data URL"""
    with open(image_path, "rb") as f:
        data = f.read()
    
    # Determine MIME type
    ext = Path(image_path).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime = mime_map.get(ext, "image/jpeg")
    
    b64 = base64.b64encode(data).decode()
    return f"data:{mime};base64,{b64}"


def generate_ecommerce_image(
    reference_image,
    prompt,
    platform="general",
    aspect_ratio="1:1",
    style="clean"
):
    """
    Generate e-commerce product image with reference image
    
    Args:
        reference_image: Path to reference product image
        prompt: Description of desired output
        platform: Target platform (taobao, jd, pdd, general)
        aspect_ratio: Image aspect ratio
        style: Product image style (clean, lifestyle, minimalist)
    
    Returns:
        dict with success status and image URL
    """
    api_key = get_api_key()
    if not api_key:
        return {"success": False, "error": "MINIMAX_CN_API_KEY not found"}
    
    # Convert reference image to base64
    try:
        ref_b64 = image_to_base64(reference_image)
    except Exception as e:
        return {"success": False, "error": f"Failed to load reference image: {e}"}
    
    # Platform-specific style prompts
    platform_styles = {
        "taobao": "淘宝主图风格，白底或浅色背景，突出产品，商业摄影",
        "jd": "京东商品图风格，专业产品摄影，高清细节，商业级",
        "pdd": "拼多多商品图风格，性价比感，清晰展示，促销氛围",
        "general": "电商平台产品图，专业商业摄影风格",
    }
    
    style_prompts = {
        "clean": "简洁干净背景，产品居中，专业商业摄影",
        "lifestyle": "生活场景展示，使用场景，温馨自然",
        "minimalist": "极简风格，大量留白，高端质感",
        "gradient": "渐变背景，现代感，科技感",
    }
    
    # Build full prompt
    platform_style = platform_styles.get(platform, platform_styles["general"])
    style_prompt = style_prompts.get(style, style_prompts["clean"])
    
    full_prompt = f"{prompt}, {platform_style}, {style_prompt}, 高清4K，商业级品质"
    
    base_url = get_base_url()
    url = f"{base_url}/v1/image_generation"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "image-01",
        "prompt": full_prompt,
        "aspect_ratio": aspect_ratio,
        "response_format": "url",
        "subject_ref": {
            "image_file": {
                "file_data": ref_b64
            }
        }
    }
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        
        base_resp = result.get("base_resp", {})
        if base_resp.get("status_code") != 0:
            return {"success": False, "error": base_resp.get("status_msg", "Unknown error")}
        
        image_urls = result.get("data", {}).get("image_urls", [])
        if not image_urls:
            return {"success": False, "error": "No image URLs in response"}
        
        return {"success": True, "url": image_urls[0]}
    
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if hasattr(e, "read") else ""
        return {"success": False, "error": f"HTTP {e.code}: {error_body[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="E-commerce Product Image Generator")
    parser.add_argument("reference", help="Path to reference product image")
    parser.add_argument("prompt", help="Description of desired output")
    parser.add_argument("--platform", "-p", default="general",
                       choices=["taobao", "jd", "pdd", "general"],
                       help="Target e-commerce platform (default: general)")
    parser.add_argument("--aspect-ratio", "-a", default="1:1",
                       choices=["1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16"],
                       help="Image aspect ratio (default: 1:1)")
    parser.add_argument("--style", "-s", default="clean",
                       choices=["clean", "lifestyle", "minimalist", "gradient"],
                       help="Product image style (default: clean)")
    parser.add_argument("--output", "-o", help="Save image to file")
    parser.add_argument("--default-output", "-d", action="store_true",
                       help="Save to default output directory")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.reference):
        print(json.dumps({"success": False, "error": f"Reference image not found: {args.reference}"}))
        sys.exit(1)
    
    # Generate output path if default-output is specified
    output_path = args.output
    if args.default_output or not output_path:
        output_dir = "D:/hermes-agent/imge_v3/ecommerce_output"
        os.makedirs(output_dir, exist_ok=True)
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"ecommerce_{timestamp}.jpg")
    
    result = generate_ecommerce_image(
        args.reference,
        args.prompt,
        args.platform,
        args.aspect_ratio,
        args.style
    )
    
    if result["success"]:
        if output_path:
            # Download and save
            req = urllib.request.Request(result["url"])
            with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                with open(output_path, "wb") as f:
                    f.write(resp.read())
            print(json.dumps({"success": True, "file": output_path}))
        else:
            print(json.dumps(result))
    else:
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
