---
name: generative-media
description: "Generate music, sound, images, video, and 3D content: AudioCraft (text-to-music/sound) and ComfyUI (Stable Diffusion, Flux, video, audio workflows)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [generative, audio, music, image, video, stable-diffusion, flux, comfyui, audiocraft]
---

# Generative Media — AI Content Generation

Two complementary skills for AI-generated media: AudioCraft for music/sound, ComfyUI for images/video/audio via node-based workflows.

## When to use

- User wants to generate music or sound effects from text descriptions
- User wants to generate images with Stable Diffusion, SDXL, Flux, SD3
- User wants to generate video (AnimateDiff, Wan, Hunyuan)
- User wants to run a ComfyUI workflow
- User wants audio-reactive visuals or music visualizers

## Skill Selection

| Need | Skill | Stack |
|------|-------|-------|
| Text-to-music, text-to-sound, melody conditioning | **audiocraft-audio-generation** | Meta AudioCraft (MusicGen, AudioGen, EnCodec) |
| Image/video/audio generation via node workflows | **comfyui** | ComfyUI + comfy-cli + REST/WebSocket API |

## audiocraft-audio-generation — Text-to-Music & Sound

### Quick Start
```python
from audiocraft.models import MusicGen
import torchaudio

model = MusicGen.get_pretrained('facebook/musicgen-medium')
model.set_generation_params(duration=30, top_k=250, temperature=1.0)
wav = model.generate(["epic cinematic orchestral music"])
torchaudio.save("output.wav", wav[0].cpu(), sample_rate=32000)
```

### Model Variants
| Model | Size | Use Case |
|-------|------|----------|
| `musicgen-small` | 300M | Quick generation |
| `musicgen-medium` | 1.5B | Balanced |
| `musicgen-large` | 3.3B | Best quality |
| `musicgen-melody` | 1.5B | Melody conditioning |
| `musicgen-stereo-*` | Varies | Stereo output |
| `musicgen-style` | 1.5B | Style transfer |
| `audiogen-medium` | 1.5B | Sound effects |

### GPU Requirements
| Model | FP16 VRAM |
|-------|-----------|
| musicgen-small | ~2GB |
| musicgen-medium | ~4GB |
| musicgen-large | ~8GB |

## comfyui — Node-Based Image/Video/Audio Generation

### Two-Layer Architecture
```
Layer 1: comfy-cli → Setup, server lifecycle, custom nodes, models
Layer 2: REST/WebSocket API + skill scripts → Workflow execution, param injection
```

### Quick Start
```bash
python3 scripts/hardware_check.py                    # Check GPU/VRAM
bash scripts/comfyui_setup.sh                        # Install + launch
python3 scripts/run_workflow.py \
  --workflow workflows/flux_dev.json \
  --args '{"prompt": "a beautiful sunset"}' \
  --output-dir ./outputs
```

### Key Scripts
| Script | Purpose |
|--------|---------|
| `hardware_check.py` | Probe GPU → recommend local vs Cloud |
| `run_workflow.py` | Inject params, submit, monitor, download |
| `run_batch.py` | N variations with parallel execution |
| `check_deps.py` | Check workflow nodes/models installed |
| `health_check.py` | Full verification checklist |

### Setup Decision
- **Cloud:** Zero install, API key required, paid subscription for API access
- **Local:** NVIDIA ≥6GB VRAM, AMD ROCm, or Apple Silicon ≥16GB unified

### Pitfalls
1. Workflow JSON must be in API format (not editor format)
2. Model names are exact and case-sensitive
3. Cloud free-tier cannot run workflows via API (403)
4. Video/audio workflows need longer timeouts (--timeout 1800)
