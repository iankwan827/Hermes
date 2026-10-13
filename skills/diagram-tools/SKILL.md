---
name: diagram-tools
description: "Visual diagram creation: architecture diagrams (SVG/HTML), hand-drawn Excalidraw diagrams (flow, seq, arch)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagrams, architecture, excalidraw, flowcharts, SVG, visualization]
---

# Diagram Tools

Create visual diagrams in two complementary formats: dark-themed SVG architecture diagrams as standalone HTML, and hand-drawn Excalidraw JSON diagrams.

## When to use

- User asks for an architecture diagram, system diagram, cloud infrastructure diagram
- User asks for a flowchart, sequence diagram, concept map
- User asks for a hand-drawn or sketch-style diagram
- User wants a shareable `.excalidraw` file or a standalone `.html` diagram

## Format Decision

| Need | Tool | Output |
|------|------|--------|
| Dark, polished tech architecture | **Architecture Diagram** | `.html` (standalone, SVG inline) |
| Hand-drawn, sketchy, whiteboard feel | **Excalidraw** | `.excalidraw` (JSON, open at excalidraw.com) |
| Infographic / visual summary image | **baoyu-infographic** skill | `.png` (generated image) |

## Architecture Diagram (dark-themed SVG as HTML)

Best for: software architecture, cloud infrastructure, microservice topology, deployment diagrams.

### Design System
- **Background:** Slate-950 (`#020617`) with 40px grid pattern
- **Font:** JetBrains Mono (Google Fonts)
- **Colors by component type:**
  - Frontend: cyan (`#22d3ee`)
  - Backend: emerald (`#34d399`)
  - Database: violet (`#a78bfa`)
  - AWS/Cloud: amber (`#fbbf24`)
  - Security: rose (`#fb7185`)
  - Message Bus: orange (`#fb923c`)
  - External: slate (`#94a3b8`)

### Output Requirements
- Single self-contained `.html` file
- No external dependencies (except Google Fonts)
- No JavaScript — pure CSS animations
- Four-part layout: Header → Main SVG → Summary Cards → Footer

## Excalidraw (hand-drawn JSON diagrams)

Best for: flowcharts, sequence diagrams, concept maps, whiteboard-style sketches.

### Key Patterns
- Save as `.excalidraw` JSON envelope: `{ "type": "excalidraw", "version": 2, "elements": [...] }`
- Use **container binding** for labeled shapes (NOT `"label"` property — that's invalid)
- Z-order = array order; emit: background → shape → bound text → arrows → next shape
- Minimum font size: 16px body, 20px titles
- Minimum shape size: 120×60 for labeled rectangles

### Upload for sharing
```bash
python skills/creative/excalidraw/scripts/upload.py ~/diagrams/my_diagram.excalidraw
```

## Pitfalls

1. **Architecture diagrams:** Legend must be placed OUTSIDE all boundary boxes. Calculate the lowest Y-coordinate of all boundaries and place legend 20px below.
2. **Excalidraw:** Do NOT use `"label": { "text": "..." }` on shapes — it's silently ignored. Always use container binding.
3. **Excalidraw:** Do NOT use emoji in text — they don't render in Excalidraw's font.
4. **Both:** Always verify the output visually before delivering.
