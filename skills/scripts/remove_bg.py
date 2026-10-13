#!/usr/bin/env python3
"""
Background removal using rembg
"""
import os
import sys
import argparse
from pathlib import Path

def remove_background(input_path, output_path=None):
    """Remove background from image"""
    from rembg import remove
    from PIL import Image
    import io
    
    if not os.path.exists(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    
    # Default output path
    if not output_path:
        p = Path(input_path)
        output_path = str(p.parent / f"{p.stem}_nobg{p.suffix}")
    
    try:
        with open(input_path, "rb") as f:
            input_data = f.read()
        
        output_data = remove(input_data)
        
        with open(output_path, "wb") as f:
            f.write(output_data)
        
        return {"success": True, "file": output_path}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Background Removal")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("--output", "-o", help="Output image path")
    
    args = parser.parse_args()
    
    result = remove_background(args.input, args.output)
    
    import json
    print(json.dumps(result))
    
    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
