# PyInstaller Advanced Tips

## Hidden Imports

Some packages need explicit `--hidden-import`:
```bash
uv run pyinstaller --onefile --hidden-import qrcode --hidden-import PIL script.py
```

## Common DLL Issues

### pyzbar
Needs `libiconv.dll` and `libzbar-64.dll` from the pyzbar package directory.
Location: `.venv/Lib/site-packages/pyzbar/libiconv.dll`

### OpenCV
Usually bundles correctly, but if cv2 fails:
```bash
--hidden-import cv2
--collect-all cv2
```

## Onefile vs Onedir

- `--onefile`: Single EXE, extracts to temp dir on run. Slower startup, larger file.
- `--onedir`: Folder with EXE + DLLs. Faster startup, easier debugging.

For distribution, `--onefile` is preferred. For development, `--onedir` is faster to rebuild.

## Console vs Windowed

- Default: Console window shows (good for debugging)
- `--windowed` or `-w`: No console window (for GUI apps)
- Note: With `--windowed`, print() output goes nowhere. Use logging to file instead.
