---
name: creative-coding
description: "Browser-based creative coding: p5.js generative art, pretext text-as-geometry demos, and Manim mathematical animations."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative-coding, generative-art, p5js, pretext, manim, animation, canvas, math]
---

# Creative Coding — Browser-Based Visual Art

Three complementary skills for creative coding output: p5.js for generative art, pretext for text-as-geometry demos, and Manim for mathematical animations.

## When to use

- User wants generative art, interactive sketches, or canvas animations
- User wants text flowing around shapes, kinetic typography, or text-as-geometry games
- User wants 3Blue1Brown-style math animations or algorithm visualizations
- User wants a creative browser demo or interactive experience

## Skill Selection

| Need | Skill | Stack | Output |
|------|-------|-------|--------|
| Generative art, interactive sketches, data viz, 3D, shaders | **p5js** | p5.js 1.x via CDN | Single HTML file |
| Text reflow around obstacles, text-as-geometry, kinetic type | **pretext** | @chenglou/pretext via esm.sh | Single HTML file |
| Math animations, algorithm walkthroughs, equation derivations | **manim-video** | Manim CE + LaTeX + ffmpeg | MP4 video |

## p5.js — Generative Art & Interactive Sketches

### Modes
| Mode | Input | Output |
|------|-------|--------|
| Generative art | Seed/params | Procedural composition |
| Data visualization | Dataset/API | Interactive charts |
| Interactive experience | User input | Mouse/keyboard-driven |
| Animation | Timeline | Timed sequences |
| 3D scene | Concept | WebGL geometry |
| Audio-reactive | Audio/mic | Sound-driven visuals |

### Critical Rules
- **Disable FES:** `p5.disableFriendlyErrors = true;` before setup (10x overhead)
- **Always seed:** `randomSeed(CONFIG.seed); noiseSeed(CONFIG.seed);`
- **Use HSB:** `colorMode(HSB, 360, 100, 100, 100)` for intuitive color
- **Layer with createGraphics():** Flat single-pass rendering looks flat
- **Vectorize:** Use `beginShape(POINTS)` for thousands of elements

### Export
| Format | Method |
|--------|--------|
| PNG | `saveCanvas('output', 'png')` |
| GIF | `saveGif('output', 5)` |
| MP4 | `saveFrames()` + ffmpeg, or `scripts/render.sh` |
| SVG | p5.js-svg plugin |

### References
11 reference files covering: core API, shapes, visual effects, animation, typography, color, WebGL/3D, interaction, export, troubleshooting.

## pretext — Text-as-Geometry Demos

### The Two Use Cases
1. **Measure, then render with CSS/DOM** — virtualized lists, masonry heights
2. **Measure AND render yourself** — canvas, SVG, WebGL, per-glyph transforms

### Key API
```js
import { prepareWithSegments, layoutWithLines, layoutNextLineRange, materializeLineRange } from "https://esm.sh/@chenglou/pretext@0.0.6";

// Variable-width text flow around a shape
let cursor = { segmentIndex: 0, graphemeIndex: 0 };
let y = 0;
while (true) {
  const lineWidth = widthAtY(y);  // how wide is the corridor at this y?
  const range = layoutNextLineRange(prepared, cursor, lineWidth);
  if (!range) break;
  const line = materializeLineRange(prepared, range);
  ctx.fillText(line.text, leftEdgeAtY(y), y);
  cursor = range.end;
  y += lineHeight;
}
```

### Demo Patterns
- Reflow around obstacle, text-as-geometry game, shatter/particles, editorial multi-column, kinetic type, multiline shrink-wrap

## Manim — Mathematical Animations

### Modes
| Mode | Use Case |
|------|----------|
| Concept explainer | Animated explanation with geometric intuition |
| Equation derivation | Step-by-step animated proof |
| Algorithm visualization | Step-by-step execution with data structures |
| Data story | Animated charts, comparisons |
| 3D visualization | Rotating surfaces, parametric curves |

### Critical Rules
- **Raw strings for LaTeX:** `MathTex(r"\frac{1}{2}")` not `MathTex("\frac{1}{2}")`
- **Monospace fonts:** Manim's Pango renderer breaks kerning with proportional fonts
- **Wait after animations:** `self.wait(1.0)` after every key reveal
- **Iterate at -ql:** Only render -qh for final output
- **One class per scene:** Each scene independently renderable

### Stack
Python script → Manim CE → LaTeX → ffmpeg. No browser, no GPU required.

### References
14 reference files covering: animations, mobjects, visual design, equations, graphs, camera/3D, scene planning, rendering, troubleshooting.
