<div align="center">

# 🎵 AIAudio

### *Audio Processing Meets Audio Intelligence*

An open-source Python library that starts as a lightweight audio toolkit and evolves into a full AI-powered audio intelligence platform — covering everything from format conversion to transcription, noise removal, speaker detection, and semantic search.

[![Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat-square)](https://github.com/shubham10divakar/aiaudio/releases)
[![PyPI](https://img.shields.io/pypi/v/aiaudio?style=flat-square&logo=pypi&label=PyPI&color=blue)](https://pypi.org/project/aiaudio)
[![Downloads](https://img.shields.io/pypi/dm/aiaudio?style=flat-square&label=downloads%2Fmonth&color=brightgreen)](https://pypi.org/project/aiaudio)
[![Total Downloads](https://img.shields.io/pepy/dt/aiaudio?style=flat-square&label=total%20downloads&color=green)](https://pypi.org/project/aiaudio)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-48%20passing-brightgreen?style=flat-square)](#running-tests)
[![Phase](https://img.shields.io/badge/Phase-2%20of%2010-orange?style=flat-square)](#roadmap)

</div>

---

## Table of Contents

- [What is AIAudio?](#what-is-aiaudio)
- [Current Features](#current-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Library API](#library-api)
  - [Loading Audio](#loading-audio)
  - [Audio Properties](#audio-properties)
  - [Slicing](#slicing)
  - [Concatenation](#concatenation)
  - [Volume Control](#volume-control)
  - [Resampling](#resampling)
  - [Channel Conversion](#channel-conversion)
  - [Exporting](#exporting)
  - [Chaining Operations](#chaining-operations)
- [CLI Reference](#cli-reference)
  - [info](#aiaudio-info)
  - [slice](#aiaudio-slice)
  - [volume](#aiaudio-volume)
  - [concat](#aiaudio-concat)
  - [convert](#aiaudio-convert)
- [Roadmap](#roadmap)
- [Project Structure](#project-structure)
- [Design Principles](#design-principles)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

---

## What is AIAudio?

AIAudio is a Python library designed to grow with you. At its core it is a simple, clean alternative to Pydub for audio manipulation — no heavy dependencies, just `numpy` and `scipy`. As it matures it becomes an AI-powered platform that can transcribe speech, remove background noise, detect speakers, search audio archives by meaning, and generate meeting summaries — all behind the same consistent API.

```python
from aiaudio import Audio

# today
audio = Audio.load("meeting.mp3")
audio.slice(0, 60).export("intro.wav")

# tomorrow (coming phases)
audio.clean()
audio.transcribe()
audio.identify_speakers()
audio.summarize()
audio.export_report("meeting_report.md")
```

---

## Current Features

| # | Feature | Status |
|---|---------|--------|
| ✅ | Load and export WAV files (native, zero extra deps) | **Available** |
| ✅ | Load and export MP3, FLAC, OGG, AAC, M4A via FFmpeg | **Available** |
| ✅ | Slice audio by time | **Available** |
| ✅ | Concatenate multiple audio files | **Available** |
| ✅ | Volume control (increase / decrease in dB) | **Available** |
| ✅ | Resampling (change sample rate) | **Available** |
| ✅ | Channel conversion (mono ↔ stereo) | **Available** |
| ✅ | CLI — `aiaudio` command with subcommands | **Available** |
| ✅ | Fade in / fade out / reverse / normalize / speed / silence removal | **Available** |
| 🔜 | AI noise removal, echo reduction, audio cleanup | Phase 4 |
| 🔜 | Speech-to-text transcription | Phase 5 |
| 🔜 | Language detection | Phase 5 |
| 🔜 | Speaker diarization | Phase 5 |
| 🔜 | Audio embeddings and semantic search | Phase 6 |
| 🔜 | Summarization, topic extraction, action items | Phase 7 |
| 🔜 | Real-time streaming and live transcription | Phase 8 |
| 🔜 | Plugin architecture | Phase 9 |
| 🔜 | Agentic end-to-end audio pipelines | Phase 10 |
| ✅ | GUI — drag-and-drop format converter | Phase 2.5 |

---

## Installation

**Core — WAV support, zero heavy dependencies:**

```bash
pip install aiaudio
```

**With multi-format support (MP3, FLAC, OGG, AAC, M4A):**

> Requires [FFmpeg](https://ffmpeg.org/download.html) installed on your system.

```bash
# Install FFmpeg first:
winget install ffmpeg          # Windows
brew install ffmpeg            # macOS
sudo apt install ffmpeg        # Ubuntu / Debian

# Then:
pip install aiaudio
```

**With GUI (drag-and-drop format converter):**

```bash
pip install "aiaudio[gui]"
```

**With AI features (transcription, noise removal, embeddings):**

```bash
pip install "aiaudio[ai]"
```

**For development / contributing:**

```bash
git clone https://github.com/shubham10divakar/aiaudio.git
cd aiaudio
pip install -e ".[dev]"
pytest   # 48 tests, all green
```

---

## Quick Start

```python
from aiaudio import Audio

# Load any format
audio = Audio.load("podcast.mp3")

print(audio)
# Audio(duration=1823.40s, sample_rate=44100Hz, channels=2)

# Trim to the first 5 minutes
intro = audio.slice(0, 300)

# Boost volume by 3 dB
intro = intro.increase_volume(3)

# Export as FLAC
intro.export("intro.flac")
```

---

## Library API

### Loading Audio

```python
from aiaudio import Audio

# WAV — native, no FFmpeg needed
audio = Audio.load("song.wav")

# Any other format — requires FFmpeg
audio = Audio.load("podcast.mp3")
audio = Audio.load("interview.flac")
audio = Audio.load("recording.m4a")
audio = Audio.load("track.ogg")
audio = Audio.load("voice.aac")
```

---

### Audio Properties

```python
audio = Audio.load("song.wav")

audio.duration      # 183.42  (float, seconds)
audio.sample_rate   # 44100   (int, Hz)
audio.channels      # 2       (int, 1=mono / 2=stereo)

print(audio)
# Audio(duration=183.42s, sample_rate=44100Hz, channels=2)
```

---

### Slicing

Extract any segment by start and end time in seconds.

```python
audio = Audio.load("song.wav")

# Extract seconds 10–20
clip = audio.slice(10, 20)

# Extract the first 30 seconds
intro = audio.slice(0, 30)

# Extract the last 60 seconds
outro = audio.slice(audio.duration - 60, audio.duration)

clip.export("clip.wav")
```

> **Note:** All operations return a **new Audio object** — the original is never modified.

---

### Concatenation

Join any number of Audio objects using the `+` operator. Both sides must have the same sample rate.

```python
intro = Audio.load("intro.wav")
main  = Audio.load("main.wav")
outro = Audio.load("outro.wav")

full = intro + main + outro

print(full.duration)  # sum of all three
full.export("full_episode.wav")
```

Mismatched sample rates raise a clear error:

```python
a = Audio.load("44100hz.wav")   # 44100 Hz
b = Audio.load("22050hz.wav")   # 22050 Hz

a + b
# ValueError: Sample rates must match: 44100 vs 22050
# Fix: b = b.resample(44100)
```

---

### Volume Control

Adjust loudness in decibels. Positive dB = louder, negative dB = quieter. Clipping is handled automatically.

```python
audio = Audio.load("quiet_recording.wav")

louder  = audio.increase_volume(6)    # +6 dB  (~2× louder)
quieter = audio.decrease_volume(3)    # -3 dB  (~half as loud)

# Or pass a negative number directly
softer = audio.increase_volume(-6)

louder.export("louder.wav")
```

---

### Resampling

Change the sample rate — useful before export or when concatenating clips with different rates.

```python
audio = Audio.load("hifi.wav")   # 48000 Hz

# Downsample for voice / podcast use
voice = audio.resample(16000)
web   = audio.resample(22050)
cd    = audio.resample(44100)

voice.export("voice.wav")
```

---

### Channel Conversion

Convert between mono and stereo.

```python
stereo = Audio.load("stereo.wav")

# Stereo → mono (averages both channels)
mono = stereo.set_channels(1)

# Mono → stereo (duplicates the single channel)
back = mono.set_channels(2)

mono.export("mono.wav")
```

---

### Exporting

Export to any supported format. The format is inferred from the file extension. WAV works with no extra dependencies; all other formats require FFmpeg.

```python
audio = Audio.load("input.mp3")

audio.export("output.wav")    # native, no FFmpeg
audio.export("output.mp3")    # requires FFmpeg
audio.export("output.flac")   # requires FFmpeg
audio.export("output.ogg")    # requires FFmpeg
audio.export("output.aac")    # requires FFmpeg
audio.export("output.m4a")    # requires FFmpeg
```

---

### Chaining Operations

All methods return a new `Audio` object, so you can chain freely:

```python
from aiaudio import Audio

result = (
    Audio.load("raw_interview.mp3")
    .slice(30, 1800)           # skip intro, take 30 min
    .set_channels(1)           # convert to mono
    .resample(16000)           # downsample for speech processing
    .decrease_volume(2)        # slightly quieter
)

result.export("interview_processed.wav")
```

---

## CLI Reference

After installing AIAudio the `aiaudio` command is available globally in your terminal.

```bash
aiaudio --help
aiaudio --version
```

---

### `aiaudio info`

Display metadata about an audio file.

```bash
aiaudio info <file>
```

```bash
$ aiaudio info podcast.mp3

File:        podcast.mp3
Duration:    1823.40s
Sample rate: 44100 Hz
Channels:    2
```

---

### `aiaudio slice`

Extract a segment of audio by start and end time in seconds.

```bash
aiaudio slice <file> <start> <end> -o <output>
```

```bash
# Extract seconds 60–120
aiaudio slice podcast.mp3 60 120 -o segment.wav

# Extract the first 30 seconds
aiaudio slice podcast.mp3 0 30 -o intro.wav

# Extract minutes 5–10
aiaudio slice podcast.mp3 300 600 -o middle.wav
```

---

### `aiaudio volume`

Increase or decrease volume in decibels.

```bash
aiaudio volume <file> <db> -o <output>
```

```bash
# Louder (+5 dB)
aiaudio volume quiet.wav 5 -o louder.wav

# Quieter (-3 dB)
aiaudio volume loud.wav -3 -o quieter.wav
```

---

### `aiaudio concat`

Join two or more audio files in order.

```bash
aiaudio concat <file1> <file2> ... -o <output>
```

```bash
# Join two files
aiaudio concat intro.wav main.wav -o full.wav

# Join three or more
aiaudio concat intro.wav part1.wav part2.wav outro.wav -o episode.wav
```

---

### `aiaudio convert`

Convert audio to a different format. Requires FFmpeg. The output format is inferred from the output file's extension.

```bash
aiaudio convert <file> -o <output> [--sample-rate HZ] [--channels {1,2}]
```

```bash
# MP3 → FLAC
aiaudio convert podcast.mp3 -o podcast.flac

# WAV → MP3, downsampled to 22050 Hz
aiaudio convert recording.wav -o recording.mp3 --sample-rate 22050

# Stereo FLAC → mono WAV at 16 kHz (ready for speech processing)
aiaudio convert stereo.flac -o mono_16k.wav --sample-rate 16000 --channels 1

# M4A → OGG
aiaudio convert audiobook.m4a -o audiobook.ogg
```

### `aiaudio` effects — `fade` / `normalize` / `reverse` / `speed` / `silence`

Audio effects (Phase 3). Each reads a file, applies the effect, and writes the result. Output format follows the output extension (non-WAV needs FFmpeg).

```bash
# Fade in 500 ms and fade out 800 ms
aiaudio fade song.wav --in 500 --out 800 -o faded.wav

# Peak-normalize (optionally leave 3 dB of headroom)
aiaudio normalize quiet.wav -o loud.wav
aiaudio normalize quiet.wav --headroom 3 -o loud.wav

# Reverse
aiaudio reverse song.wav -o backwards.wav

# 1.5× faster, pitch preserved (use <1 to slow down)
aiaudio speed lecture.mp3 1.5 -o quick.mp3

# Remove silent gaps longer than 200 ms below -30 dBFS
aiaudio silence interview.wav --threshold -30 --min-silence 200 -o tight.wav
```

### `aiaudio gui`

Launch the browser-based drag-and-drop format converter. Requires the GUI extra (`pip install "aiaudio[gui]"`); multi-format output still needs FFmpeg.

```bash
aiaudio gui                  # open the converter in your browser
aiaudio gui --port 8080      # serve on a specific port
aiaudio gui --share          # create a public shareable link

python -m aiaudio.gui        # equivalent, without the CLI
```

Drop one or more files, pick a target format (plus optional sample rate / channels), and click **Convert all**. A single file downloads directly; a batch downloads as a ZIP. One bad file reports its error inline without aborting the rest of the batch.

---

## Roadmap

AIAudio is built in phases. Each phase is independently useful and ships as a working release.

| Phase | Feature | Description |
|-------|---------|-------------|
| ✅ **1** | Core Audio Engine | Load, slice, concat, volume, export (WAV) |
| ✅ **1.1** | CLI | `aiaudio` command with 5 subcommands |
| ✅ **2** | Multi-Format Support | MP3, FLAC, OGG, AAC, M4A via FFmpeg |
| ✅ **2.5** | GUI | Drag-and-drop browser-based format converter |
| ✅ **3** | Audio Effects | Fade in/out, speed change, reverse, normalize, silence removal |
| 🔜 **4** | AI Enhancement | Noise removal, echo reduction, voice cleanup |
| 🔜 **5** | Speech Intelligence | Transcription, language detection, speaker diarization |
| 🔜 **6** | Embeddings & Search | Semantic audio search — find content by meaning |
| 🔜 **7** | AI Workflows | Summarization, topic extraction, action items, meeting minutes |
| 🔜 **8** | Streaming | Live mic input, real-time transcription and noise reduction |
| 🔜 **9** | Plugin Architecture | Custom effects, models, and exporters via `@plugin` decorator |
| 🔜 **10** | Agentic Platform | Full pipeline: clean → transcribe → diarize → summarize → report |

### Phase 3 — Audio Effects ✅

Like every operation, effects return a **new** `Audio` (the original is untouched) and chain freely:

```python
audio = Audio.load("recording.wav")

audio = (
    audio
    .normalize()              # peak-normalize to 0 dBFS (normalize(headroom_db=3) leaves 3 dB)
    .fade_in(2000)            # 2-second fade in
    .fade_out(3000)           # 3-second fade out
    .remove_silence()         # strip silent gaps (threshold_db / min_silence_ms tunable)
)

faster   = audio.speed(1.5)   # 1.5× faster — pitch preserved (overlap-add time stretch)
backward = audio.reverse()    # reverse in time

audio.export("polished.wav")
```

### Phase 4 preview — AI Enhancement

```python
audio = Audio.load("noisy_podcast.mp3")

clean = audio.remove_noise()    # deep learning noise suppression
clean = audio.remove_echo()     # echo / reverb reduction
clean = audio.clean()           # full pipeline: noise + echo + background

clean.export("podcast_clean.mp3")
```

### Phase 5 preview — Speech Intelligence

```python
audio = Audio.load("interview.mp3")

transcript = audio.transcribe()
# "Welcome to the show. Today we are talking about..."

lang = audio.detect_language()
# "en"

speakers = audio.identify_speakers()
# [{"speaker": "A", "start": 0.0, "end": 12.4},
#  {"speaker": "B", "start": 12.4, "end": 28.1}, ...]
```

### Phase 6 preview — Embeddings & Search

```python
audio = Audio.load("podcast.mp3")

# Semantic search across your audio
audio.search("discussion about climate change")
# [{"start": 342.1, "end": 398.6, "score": 0.94}, ...]

# Generate an embedding vector for downstream ML
embedding = audio.embed()   # numpy array
```

### Phase 7 preview — AI Workflows

```python
audio = Audio.load("team_meeting.mp3")

print(audio.summarize())
# "The team discussed Q3 targets, identified a blocker in the
#  API integration, and agreed to reconvene Thursday."

print(audio.extract_actions())
# ["John to send API docs by Wednesday",
#  "Sarah to review the staging environment",
#  "Team sync scheduled for Thursday 10am"]

audio.generate_minutes()   # returns structured markdown
```

### Phase 10 preview — Agentic Pipeline

```python
audio = Audio.load("board_meeting.mp3")

audio.clean()
audio.transcribe()
audio.identify_speakers()
audio.extract_actions()
audio.summarize()
audio.export_report("board_meeting_report.md")

# Produces a complete markdown report:
# - Full transcript with speaker labels
# - Executive summary
# - Action items by owner
# - Key topics and timestamps
```

---

## Project Structure

```
aiaudio/
│
├── core/
│   ├── audio.py        # Audio class — the main user-facing object
│   ├── loader.py       # Format detection, WAV read, FFmpeg decode
│   ├── exporter.py     # WAV write, FFmpeg encode
│   └── ffmpeg.py       # FFmpeg subprocess bridge (probe, load, export)
│
├── cli/
│   └── main.py         # aiaudio CLI — argparse subcommands
│
├── gui/
│   ├── converter.py    # Phase 2.5 — conversion core + Gradio app
│   └── __main__.py     # python -m aiaudio.gui entry point
│
├── effects/
│   ├── fade.py         # Phase 3 — fade in / out
│   ├── normalize.py    # Phase 3 — peak normalization
│   ├── silence.py      # Phase 3 — silence removal
│   └── timestretch.py  # Phase 3 — speed (pitch-preserving)
│
├── ai/                 # Phases 4–7 — enhancer, whisper, diarization, LLM
├── plugins/            # Phase 9 — plugin registry
└── utils/

tests/
├── test_core.py        # Phase 1 — 22 tests
├── test_cli.py         # Phase 1.1 — 9 tests
├── test_phase2.py      # Phase 2 — 17 tests (8 skipped if FFmpeg absent)
├── test_gui.py         # Phase 2.5 — 16 tests (GUI conversion core)
└── test_phase3.py      # Phase 3 — 31 tests (audio effects)

setup.py
pyproject.toml
README.md
AIAUDIO_PLAN.md         # full phased plan with API sketches and UI mockups
```

---

## Design Principles

**Immutable API**
Every method returns a new `Audio` object. The original is never modified, so you can branch freely without defensive copying.

```python
original = Audio.load("song.wav")
louder   = original.increase_volume(6)   # new object
clip     = original.slice(10, 20)        # original still untouched
```

**Lean core, optional extras**
The core library installs in seconds — only `numpy` and `scipy`. Heavy ML dependencies (PyTorch, Whisper, Demucs) only arrive when you opt in:

```bash
pip install aiaudio           # core only (~10 MB)
pip install "aiaudio[ai]"     # adds torch + whisper + more
```

**One code path**
The CLI and GUI are thin orchestration layers. All logic lives in the `Audio` class. There is no special-casing for how a request arrived.

**Float32 internally**
Samples are normalised to `[-1.0, 1.0]` on load regardless of source bit depth. All DSP math operates in float32. Conversion back to `int16` happens only on WAV export.

**Format-transparent**
`Audio.load("file.mp3")` and `Audio.load("file.wav")` have identical return types and behave identically. The format routing is invisible to the caller.

---

## Running Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# With coverage report
pytest --cov=aiaudio --cov-report=term-missing

# Core only (no FFmpeg needed)
pytest tests/test_core.py tests/test_cli.py -v
```

FFmpeg integration tests skip automatically if FFmpeg is not installed — they do not fail.

```
95 passed, 8 skipped   ← skipped = FFmpeg not present
103 passed, 0 skipped   ← when FFmpeg is installed
```

---

## Contributing

Contributions are welcome. The project follows a phase-by-phase build order — see [AIAUDIO_PLAN.md](./AIAUDIO_PLAN.md) for the full roadmap and API design for upcoming phases.

1. Fork the repo and create a branch from `main`
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Open a pull request

---

## License

MIT — free to use, modify, and distribute.

---

<div align="center">

Built with ❤️ — *AIAudio: Audio Processing Meets Audio Intelligence*

</div>
