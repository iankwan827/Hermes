---
name: ascii-creative
description: "ASCII creative output: text banners, cowsay, boxes, image-to-ascii (ascii-art) and video/audio-to-colored-ASCII-video conversion (ascii-video)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ASCII, art, video, creative, text-art, pyfiglet, cowsay, boxes]
---

# ASCII Creative — Text Art & ASCII Video

Two complementary skills for ASCII-based creative output: static text art and animated ASCII video.

## When to use

- User wants ASCII art banners, text decorations, or image-to-ASCII conversion
- User wants video or audio converted to colored ASCII animation (MP4/GIF)
- User wants terminal-style visual effects, matrix-style text, or retro text visualization

## Skill Selection

| Need | Skill | Stack |
|------|-------|-------|
| Static text art, banners, cowsay, image-to-ASCII | **ascii-art** | pyfiglet, cowsay, boxes, toilet, ascii-image-converter, curl APIs |
| Video/audio to ASCII video, generative ASCII animation | **ascii-video** | Python + NumPy + SciPy + Pillow + ffmpeg |

## ascii-art — Static Text Art

Nine tools for different ASCII art needs. All local CLI or free REST APIs — no API keys.

### Tool Selection
1. **Text banners** → `pyfiglet` (571 fonts, local) or asciified API (curl, no install)
2. **Message art** → `cowsay` (50+ characters, speech/thought bubbles)
3. **Decorative borders** → `boxes` (70+ designs, combine with pyfiglet)
4. **Colored text** → `toilet` (ANSI colors + filters: gay, metal, border)
5. **Image to ASCII** → `ascii-image-converter` (color, dimensions, Braille) or `jp2a` (lightweight, JPEG only)
6. **Pre-made art** → ascii.co.uk via curl (animals, objects, nature, characters)
7. **QR codes** → `qrenco.de` via curl
8. **Weather art** → `wttr.in` via curl
9. **Custom** → LLM generation with Unicode box/block/geometric characters

### Quick examples
```bash
python3 -m pyfiglet "HERMES" -f doom | boxes -d stone    # Banner in stone box
curl -s "qrenco.de/https://example.com"                   # QR code
curl -s "wttr.in/London"                                   # Weather ASCII
cowsay -f dragon "Rawr!"                                   # Dragon message
```

## ascii-video — Animated ASCII Video

Full production pipeline for converting video/audio to colored ASCII character video. Six modes:

| Mode | Input | Use Case |
|------|-------|----------|
| Video-to-ASCII | Video file | Recreate source footage in ASCII |
| Audio-reactive | Audio file | Generative visuals driven by audio FFT |
| Generative | None | Procedural ASCII animation |
| Hybrid | Video + audio | ASCII video with audio-reactive overlays |
| Lyrics/text | Audio + SRT | Timed text with visual effects |
| TTS narration | Text + TTS API | Narrated quote video with typed text |

### Stack
Single Python script per project: NumPy, SciPy, Pillow, ffmpeg. No GPU required.

### Critical: Use `tonemap()`, Not Linear Multipliers
ASCII on black is inherently dark. Never use `canvas * N` — it clips highlights. Use adaptive tonemap:
```python
def tonemap(canvas, gamma=0.75):
    f = canvas.astype(np.float32)
    lo, hi = np.percentile(f[::4, ::4], [1, 99.5])
    if hi - lo < 10: hi = lo + 10
    f = np.clip((f - lo) / (hi - lo), 0, 1) ** gamma
    return (f * 255).astype(np.uint8)
```

### Per-Section Variation
Never use the same config for the entire video. Each scene needs different: background effect, character palette, color strategy, shader intensity.

## Creative Standard (ascii-video)

This is visual art. ASCII characters are the medium; cinema is the standard.
- First-render excellence is non-negotiable
- Go beyond the reference vocabulary — the catalog is a palette, you write the painting
- Be proactively creative — include at least one visual moment the user didn't ask for
- Dense, layered, considered — every frame should reward viewing
