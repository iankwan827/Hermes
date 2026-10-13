---
name: web-design
description: "HTML artifact design: design process/taste (claude-design), design token specs (design-md), and 54 ready-to-paste design systems (popular-web-designs)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, prototype, design-systems, tokens, ux, ui, creative]
---

# Web Design — HTML Artifact Design Skills

Three complementary skills for designing HTML artifacts, each serving a different phase of the design workflow.

## Skill Decision Table

| Need | Skill | What it gives you |
|------|-------|-------------------|
| From-scratch designed artifact (landing page, prototype, deck, component lab) | **claude-design** | Design process and taste — how to scope a brief, gather context, produce variants, verify, avoid AI-design slop |
| Match a known brand's look (Stripe, Linear, Vercel, Notion, etc.) | **popular-web-designs** | 54 ready-to-paste design systems — exact colors, typography, components, CSS values |
| Author a formal, persistent design-system spec file | **design-md** | Google's DESIGN.md format — tokens, WCAG contrast, Tailwind/DTCG export |

## How they compose

1. Use **popular-web-designs** for the visual vocabulary (colors, fonts, components from a real product)
2. Use **claude-design** for how to turn a brief into a thoughtful local HTML file
3. Use **design-md** when the output is a token file rather than a rendered artifact

## claude-design — Process & Taste

Design workflow for one-off HTML artifacts. Covers:
- Brief scoping and context gathering
- Design system definition (colors, type, spacing, radii, shadows, motion)
- Variant generation (conservative / strong-fit / divergent)
- HTML artifact creation (single self-contained file)
- Anti-slop rules (no glassmorphism, no emoji, no generic SaaS cards)
- Deck rules (1920×1080, keyboard nav, localStorage persistence)
- Prototype rules (clickable paths, key states, in-page Tweaks panel)

**When NOT to use:** For a token spec file → use `design-md`. For a known brand → load `popular-web-designs` alongside.

## popular-web-designs — 54 Design Systems

Ready-to-paste design systems for real products. Each template includes:
- Color palette (exact hex values)
- Typography hierarchy (font families, sizes, weights)
- Component styles (buttons, cards, inputs, nav)
- Spacing system
- Shadows and elevation
- Responsive behavior
- Agent prompts with exact CSS values

### Catalog highlights
- **Developer tools:** Linear, Vercel, Supabase, Raycast, Sentry, Cursor
- **Marketing:** Stripe, Framer, Apple, SpaceX
- **Dark mode:** Linear, ElevenLabs, Warp, Superhuman
- **Light/clean:** Vercel, Stripe, Notion, Cal.com

### Usage
```bash
skill_view(name="popular-web-designs", file_path="templates/stripe.md")
```

## design-md — Token Spec Files

Google's DESIGN.md spec (Apache-2.0) for describing visual identity to coding agents. One file combines:
- YAML front matter — machine-readable design tokens
- Markdown body — human-readable rationale

### CLI
```bash
npx -y @google/design.md lint DESIGN.md           # Validate + WCAG contrast
npx -y @google/design.md diff DESIGN.md DESIGN-v2.md  # Regression check
npx -y @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json
npx -y @google/design.md export --format dtcg DESIGN.md > tokens.json
```

### Pitfalls
- Don't nest component variants (`button-primary.hover` is wrong; `button-primary-hover` is right)
- Hex colors must be quoted strings in YAML
- Section order is enforced: Overview → Colors → Typography → Layout → Elevation → Shapes → Components → Do's/Don'ts
