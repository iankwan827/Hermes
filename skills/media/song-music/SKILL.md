---
name: song-music
description: "Complete music creation pipeline: songwriting craft, AI music generation (HeartMuLa, Suno), and audio analysis (spectrograms, features). Unified entry point for all music-related tasks."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [music, songwriting, audio, generation, suno, heartmula, spectrogram, lyrics]
    related_skills: [audiocraft-audio-generation, youtube-content]
---

# Song & Music

Complete music creation and analysis pipeline. From songwriting craft to AI generation to audio visualization.

## When to Use

- Writing song lyrics or adapting existing songs
- Generating music with AI (HeartMuLa, Suno)
- Analyzing audio files (spectrograms, features)
- Creating music prompts for AI tools

---

## 1. Songwriting Craft

### Song Structure

Common skeletons:
```
ABABCB  Verse/Chorus/Verse/Chorus/Bridge/Chorus    (most pop/rock)
AABA    Verse/Verse/Bridge/Verse                    (jazz, ballads)
ABAB    Verse/Chorus alternating                    (simple, direct)
AAA     Verse/Verse/Verse (strophic)                (folk, storytelling)
```

Building blocks: Intro, Verse, Pre-Chorus, Chorus, Bridge, Outro

### Rhyme & Meter

- **Perfect:** lean/mean — tight, can sound nursery-rhyme if overused
- **Family:** crate/braid — looser, more natural
- **Assonance:** had/glass — same vowels, different endings
- **Slant/near:** enough to suggest connection without locking down
- **Internal rhyme:** rhyming within a line, not just at ends

### Emotional Arc (Energy Mapping)

```
Intro: 2-3  |  Verse: 5-6  |  Pre-Chorus: 7
Chorus: 8-9  |  Bridge: varies  |  Final Chorus: 9-10
```

**Key trick: CONTRAST.** Whisper before a scream hits harder than just screaming. Silence is an instrument.

### Writing Lyrics

- **Show, don't tell:** "Your hoodie's still on the hook by the door" > "I was sad"
- **The hook:** Line people remember, hum, repeat. Usually title or core phrase.
- **Prosody:** Stable feelings → settled melodies + perfect rhymes. Unstable feelings → wandering melodies + near-rhymes.

### Parody & Adaptation

1. Map original structure (syllables, rhyme scheme, stressed beats)
2. Match stressed syllables to same beats as original
3. On held notes, match vowel sound of original
4. Keep some original lines for recognizability

---

## 2. AI Music Generation

### Suno AI

**Style field formula:** Genre + Mood + Era + Instruments + Vocal Style + Production + Dynamics

```
BAD:  "sad rock song"
GOOD: "Cinematic orchestral spy thriller, 1960s Cold War era, smoky
       sultry female vocalist, big band jazz, brass section, minor key"
```

**Metatags (in lyrics field):**
- Structure: `[Intro]` `[Verse]` `[Chorus]` `[Bridge]` `[Outro]`
- Performance: `[Whispered]` `[Belted]` `[Falsetto]` `[Spoken Word]`
- Dynamics: `[High Energy]` `[Building Energy]` `[Explosive]`
- Atmosphere: `[Melancholic]` `[Euphoric]` `[Dreamy]`

**Tips:**
- Always use Custom Mode for serious work
- Describe the dynamic ARC, not just genre
- No artist names — describe the sound instead
- Generate 3-5 variations minimum

### HeartMuLa (Open-Source Suno Alternative)

**Installation:**
```bash
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib && uv venv --python 3.10 .venv && . .venv/bin/activate
uv pip install -e .
uv pip install --upgrade datasets transformers  # Fix dependency conflicts
```

**Download models:**
```bash
hf download --local-dir './ckpt' 'HeartMuLa/HeartMuLaGen'
hf download --local-dir './ckpt/HeartMuLa-oss-3B' 'HeartMuLa/HeartMuLa-oss-3B-happy-new-year'
hf download --local-dir './ckpt/HeartCodec-oss' 'HeartMuLa/HeartCodec-oss-20260123'
```

**Generate:**
```bash
python ./examples/run_music_generation.py \
  --model_path=./ckpt --version="3B" \
  --lyrics="./assets/lyrics.txt" --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" --lazy_load true
```

**Hardware:** 8GB VRAM minimum with `--lazy_load true`, 16GB+ recommended. CPU possible but extremely slow.

**Pitfalls:**
- Do NOT use bf16 for HeartCodec — degrades audio quality
- Tags may be ignored — lyrics tend to dominate
- GPU required for reasonable speed (RTF ≈ 1.0 on GPU)

### AudioCraft (Meta — MusicGen/AudioGen)

```python
from audiocraft.models import MusicGen
model = MusicGen.get_pretrained('facebook/musicgen-medium')
model.set_generation_params(duration=30)
wav = model.generate(["epic orchestral soundtrack"])
torchaudio.save("output.wav", wav[0].cpu(), sample_rate=32000)
```

**Models:** small (300M), medium (1.5B), large (3.3B), melody, stereo variants.

---

## 3. Audio Analysis

### songsee — Spectrograms & Feature Visualization

```bash
# Install
go install github.com/steipete/songsee/cmd/songsee@latest

# Basic spectrogram
songsee track.mp3 -o spectrogram.png

# Multi-panel visualization
songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux

# Time slice
songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg
```

**Visualization types:** spectrogram, mel, chroma, hpss, selfsim, loudness, tempogram, mfcc, flux

**Styles:** classic, magma, inferno, viridis, gray

---

## Phonetic Tricks for AI Singers

AI vocalists pronounce, not read. Help them:

- **Respell:** "through" → "thru", "Nous" → "Noose"
- **Hyphenate syllables:** "Re-search", "bio-engineering"
- **ALL CAPS** = louder/more intense
- **Vowel extension:** "lo-o-o-ove" = sustained
- **Spell numbers:** "24/7" → "twenty four seven"
- **Space acronyms:** "AI" → "A I"

---

## Pitfalls

1. **Style arc > genre listing** — "whisper to roar to whisper" gives AI a performance map
2. **Keep some original lines** in parodies — adds recognizability
3. **Bridge is for transformation** — swap references while keeping emotional function
4. **Generate 3-5x** — revision is normal, ~1 good result per 3-5 generations
5. **HeartMuLa tags may be ignored** — experiment with ordering
6. **Suno: no artist names** — describe the sound instead
