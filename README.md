# AIAudio

> **Audio Processing Meets Audio Intelligence.**

An open-source Python library that starts as a lightweight audio manipulation toolkit and evolves into an AI-powered audio intelligence platform.

---

## Features

| Phase | Capability | Status |
|-------|-----------|--------|
| 1 | Core audio engine — load, slice, concat, volume, export (WAV) | **Available** |
| 1.1 | CLI — `aiaudio info / slice / volume / concat` | **Available** |
| 2 | Multi-format support via FFmpeg (MP3, FLAC, OGG, AAC, M4A) | Planned |
| 2.5 | GUI — drag-and-drop format converter | Planned |
| 3 | Audio effects — fade, normalize, reverse, silence removal | Planned |
| 4 | AI enhancement — noise removal, echo reduction | Planned |
| 5 | Speech intelligence — transcription, speaker detection | Planned |
| 6 | Audio search via embeddings | Planned |
| 7 | AI workflows — summarize, extract topics, meeting minutes | Planned |
| 8 | Real-time streaming | Planned |
| 9 | Plugin architecture | Planned |
| 10 | Agentic audio platform | Planned |

---

## Installation

**Core (WAV support, zero heavy deps):**
```bash
pip install aiaudio
```

**With multi-format support (FFmpeg bridge):**
```bash
pip install aiaudio[formats]
```

**With GUI:**
```bash
pip install aiaudio[gui]
```

**With AI features:**
```bash
pip install aiaudio[ai]
```

**For development:**
```bash
git clone <repo>
cd aiaudio
pip install -e ".[dev]"
```

---

## Quick Start

```python
from aiaudio import Audio

# Load
audio = Audio.load("song.wav")
print(audio)
# Audio(duration=183.42s, sample_rate=44100Hz, channels=2)

# Properties
print(audio.duration)     # seconds (float)
print(audio.sample_rate)  # Hz (int)
print(audio.channels)     # 1 or 2

# Slice (times in seconds)
clip = audio.slice(10, 20)

# Concatenate
merged = clip + audio.slice(30, 40)

# Volume (in dB)
louder  = audio.increase_volume(5)
quieter = audio.decrease_volume(3)

# Export
audio.export("output.wav")
```

> All operations are **immutable** — every method returns a new `Audio` object.
> The original is never modified.

---

## CLI

Install the package and the `aiaudio` command becomes available immediately.

### Show file info
```bash
aiaudio info song.wav
```
```
File:        song.wav
Duration:    183.42s
Sample rate: 44100 Hz
Channels:    2
```

### Slice audio
```bash
aiaudio slice song.wav 10 20 -o clip.wav
```

### Adjust volume
```bash
aiaudio volume song.wav 5 -o louder.wav    # +5 dB
aiaudio volume song.wav -3 -o quieter.wav  # -3 dB
```

### Concatenate files
```bash
aiaudio concat intro.wav main.wav outro.wav -o full.wav
```

---

## Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=aiaudio --cov-report=term-missing
```

---

## Project Structure

```
aiaudio/
├── core/
│   ├── audio.py       # Audio class — main user-facing object
│   ├── loader.py      # WAV loading + PCM normalisation
│   └── exporter.py    # WAV export
├── cli/
│   └── main.py        # aiaudio CLI entry point
├── effects/           # Phase 3 — fade, normalize, silence (coming)
├── ai/                # Phases 4–7 — AI features (coming)
├── plugins/           # Phase 9 — plugin registry (coming)
└── utils/
tests/
├── test_core.py
└── test_cli.py
setup.py
pyproject.toml
README.md
XENAUDIO_PLAN.md
```

---

## Design Decisions

- **Immutable API** — every operation returns a new `Audio` object. Chain freely; no hidden side effects.
- **Lean core** — Phase 1 depends only on `numpy` and `scipy` (both tiny). Heavy ML deps (`torch`, `whisper`, etc.) live in optional extras.
- **One code path** — CLI, GUI, and library all call the same `Audio` methods. No logic lives in the CLI or GUI layers.
- **Float32 internally** — samples are normalised to `[-1.0, 1.0]` on load, converted back to `int16` on WAV export. This makes all DSP math simple and consistent.

---

## Roadmap

See [AIAUDIO_PLAN.md](./AIAUDIO_PLAN.md) for the full phased plan with API sketches, technology choices, and UI mockups.

---

## License

MIT
