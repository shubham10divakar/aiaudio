# AIAudio — Plan

> **Tagline:** *"Audio Processing Meets Audio Intelligence."*
> **Status:** Planning
> **Last updated:** 2026-06-13

---

## Vision

An open-source Python library that starts as a lightweight audio manipulation toolkit (a modern Pydub alternative) and evolves into an AI-powered audio intelligence platform, combining:

- Audio Editing
- Audio Analysis
- Speech Processing
- AI Audio Intelligence

---

## Roadmap Overview

| Phase | Title | Status |
|-------|-------|--------|
| 1 | Core Audio Engine | Done |
| 1.1 | CLI — Command Line Interface | Done |
| 2 | Multi-Format Support | Done |
| 2.5 | GUI — Audio Format Converter | Planned |
| 3 | Audio Effects | Planned |
| 4 | AI Audio Enhancement | Planned |
| 5 | Speech Intelligence | Planned |
| 6 | Audio Search & Embeddings | Planned |
| 7 | AI Workflows | Planned |
| 8 | Streaming Support | Planned |
| 9 | Plugin Architecture | Planned |
| 10 | Agentic Audio Platform | Planned |

---

## Phase 1 — Core Audio Engine

**Goal:** Lightweight WAV manipulation; the foundation everything else builds on.

### API

```python
from aiaudio import Audio

audio = Audio.load("song.wav")

# Info
audio.duration
audio.sample_rate
audio.channels

# Editing
clip   = audio.slice(10, 20)
merged = audio1 + audio2
audio.increase_volume(5)
audio.decrease_volume(5)

# Export
audio.export("output.wav")
```

### Supported Formats

- WAV (native, no FFmpeg needed)

### Technology Stack

| Package | Purpose |
|---------|---------|
| `wave` | WAV I/O |
| `numpy` | PCM sample manipulation |
| `scipy` | Signal math |

### Deliverable

```python
from aiaudio import Audio

audio = Audio.load("input.wav")
audio = audio.slice(5, 15)
audio.increase_volume(3)
audio.export("output.wav")
```

---

## Phase 1.1 — CLI: Command Line Interface

**Goal:** Expose every Phase 1 operation as a terminal command so the library is usable without writing Python. CLI, GUI, and library all share one code path — the CLI just parses arguments and calls `Audio`.

### Commands

```bash
# Show audio info
aiaudio info song.wav

# Slice audio (times in seconds)
aiaudio slice song.wav 10 20 -o clip.wav

# Adjust volume (+db louder, -db quieter)
aiaudio volume song.wav 5 -o louder.wav
aiaudio volume song.wav -5 -o quieter.wav

# Concatenate files
aiaudio concat a.wav b.wav c.wav -o merged.wav
```

### Output Examples

```
$ aiaudio info song.wav
File:        song.wav
Duration:    183.42s
Sample rate: 44100 Hz
Channels:    2
```

### Installation

```bash
pip install aiaudio
aiaudio --help   # available immediately after install
```

### Technology Stack

| Package | Purpose |
|---------|---------|
| `argparse` | Argument parsing (stdlib, no extra dep) |
| `aiaudio` core | All actual audio operations |

### Engineering Notes

- Registered as a `console_scripts` entry point in `setup.py` / `pyproject.toml`.
- Each subcommand maps 1:1 to a library call — no logic lives in the CLI layer.
- Future phases add new subcommands (`aiaudio convert`, `aiaudio transcribe`, etc.) without changing the CLI structure.

---

## Phase 2 — Multi-Format Audio Support

**Goal:** Support all common audio formats via FFmpeg.

### Supported Formats

- WAV, MP3, FLAC, OGG, AAC, M4A

### API

```python
audio = Audio.load("podcast.mp3")
audio.export("podcast.flac")
```

### Internal Workflow

```
Input File → FFmpeg Decode → PCM Samples → AIAudio Processing → FFmpeg Encode → Output File
```

### Additional API (added in Phase 2)

```python
# Resample to a different rate
audio = audio.resample(22050)

# Convert between mono and stereo
audio = audio.set_channels(1)   # stereo → mono
audio = audio.set_channels(2)   # mono → stereo
```

### Technology Stack

| Package | Purpose |
|---------|---------|
| FFmpeg | Encode / decode all formats |
| `subprocess` | FFmpeg process management |
| `scipy.signal.resample_poly` | High-quality resampling |

---

## Phase 2.5 — GUI: Audio Format Converter

**Goal:** A simple graphical app on top of Phase 1 + 2 so non-developers can convert audio without touching Python. First user-facing product surface; later grows into the front-end for all AI features (clean, transcribe, summarize) as additional tabs.

### Scope (v1)

- Single file upload → convert → download
- Multiple file (batch) upload → convert all → download as ZIP
- Target format dropdown: WAV / MP3 / FLAC / OGG / AAC / M4A
- Optional: target sample rate, channels (mono/stereo), bitrate
- Per-file progress + overall progress
- Per-file error reporting (corrupt / unsupported input doesn't abort the batch)
- Drag-and-drop support

### UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  AIAudio — Format Converter                                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌───────────────────────────────────────────────────┐     │
│   │                                                     │     │
│   │        Drag & drop audio files here                 │     │
│   │               or  [ Browse files ]                  │     │
│   │           (supports multiple files)                 │     │
│   │                                                     │     │
│   └───────────────────────────────────────────────────┘     │
│                                                               │
│   Convert to:  [ MP3  ▼ ]                                     │
│   Sample rate: [ Keep original ▼ ]   Channels: [ Keep ▼ ]    │
│   Bitrate:     [ 192 kbps ▼ ]                                 │
│                                                               │
│   ┌──────────────── Queue ─────────────────────────────┐    │
│   │  song1.wav    → mp3   ✓ done        [download]      │    │
│   │  voice.flac   → mp3   ▓▓▓▓░░ 64%                    │    │
│   │  meeting.m4a  → mp3   ✗ error: corrupt header       │    │
│   └────────────────────────────────────────────────────┘    │
│                                                               │
│        [ Convert all ]        [ Download all (.zip) ]         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Coding Approaches

All GUI options are thin orchestration layers — real work always delegates to `aiaudio.Audio`.

| Option | Tech | Pros | Cons | Verdict |
|--------|------|------|------|---------|
| **A** | **Gradio** | ~40 LOC, native multi-file + drag-drop, browser UI, same surface reused for AI phases, public link sharing | Needs a running Python process; not a true desktop exe | **★ Recommended for v1** |
| B | Streamlit | Clean dashboards, multi-file upload | Reruns whole script on each interaction; more code for per-file progress | Good for richer multi-page later |
| C | Tkinter | Zero extra dep, real desktop window, PyInstaller `.exe` | More boilerplate, manual worker thread for responsiveness | Good for offline desktop edition |
| D | PySide6/PyQt | Most polished native desktop, real drag-drop | Heaviest dep, most code | Overkill for v1 |
| E | Flask/FastAPI + HTML/JS | Full control, SaaS-ready | Most work (templates, JS, job queue) | Best for hosted web product later |

**Recommendation:**
- **v1:** Gradio — fastest path, reuses same surface for all upcoming AI phases
- **Later:** Tkinter + PyInstaller for users who want a standalone offline `.exe`

### Gradio Implementation Sketch

```python
import gradio as gr
import zipfile, tempfile, os
from aiaudio import Audio

def convert(files, target_fmt, sample_rate, channels):
    outputs = []
    for f in files:
        audio = Audio.load(f.name)
        if sample_rate != "Keep original":
            audio = audio.resample(int(sample_rate))
        if channels != "Keep":
            audio = audio.set_channels(1 if channels == "Mono" else 2)
        out = os.path.splitext(f.name)[0] + "." + target_fmt
        audio.export(out, format=target_fmt)
        outputs.append(out)

    if len(outputs) == 1:
        return outputs[0]
    zip_path = os.path.join(tempfile.gettempdir(), "converted.zip")
    with zipfile.ZipFile(zip_path, "w") as z:
        for o in outputs:
            z.write(o, arcname=os.path.basename(o))
    return zip_path

with gr.Blocks(title="AIAudio — Format Converter") as app:
    gr.Markdown("# AIAudio — Format Converter")
    files  = gr.File(file_count="multiple", label="Drop audio files here")
    target = gr.Dropdown(["wav","mp3","flac","ogg","aac","m4a"], value="mp3", label="Convert to")
    sr     = gr.Dropdown(["Keep original","16000","44100","48000"], value="Keep original", label="Sample rate")
    ch     = gr.Dropdown(["Keep","Mono","Stereo"], value="Keep", label="Channels")
    btn    = gr.Button("Convert all", variant="primary")
    result = gr.File(label="Download result")
    btn.click(convert, [files, target, sr, ch], result)

if __name__ == "__main__":
    app.launch()
```

### Engineering Notes

- All conversion logic lives in the core library; the GUI only orchestrates calls.
- Run batch conversion off the UI thread (Gradio queue / worker thread) so the UI stays responsive.
- Validate each file independently — one bad file must not abort the batch.
- Clean up temp output files after download to avoid disk bloat.
- Expose the same operation as a CLI (`aiaudio convert in.wav -f mp3`) so GUI, CLI, and library all share one code path.
- `Audio.resample()` and `Audio.set_channels()` are needed for sample rate / channel options — add these to Phase 2.

### Technology Stack

| Package | Purpose |
|---------|---------|
| `gradio` | Primary GUI framework |
| `aiaudio` core | Phase 1 + Phase 2 engine |
| `zipfile`, `tempfile` | Batch ZIP output |

### Deliverable

```bash
python -m aiaudio.gui    # opens converter in the browser
```

---

## Phase 3 — Audio Effects

**Goal:** Commonly used audio editing effects.

### API

```python
audio.fade_in(1000)       # ms
audio.fade_out(1000)
audio.speed(1.5)
audio.reverse()
audio.normalize()
audio.remove_silence()
```

### Technology Stack

| Package | Purpose |
|---------|---------|
| `numpy` | Array operations |
| `scipy.signal` | Signal processing |

---

## Phase 4 — AI Audio Enhancement

**Goal:** AI-based audio cleaning for podcasts, meetings, and voice-overs.

### API

```python
audio.remove_noise()
audio.remove_echo()
audio.clean()             # full noise + echo + background suppression
```

### Technology Stack

| Package | Purpose |
|---------|---------|
| DeepFilterNet | Deep learning noise reduction |
| RNNoise | Lightweight RNN-based noise suppression |
| Demucs | Source separation (music / voice) |

### Use Cases

- Podcast cleanup
- Meeting recording enhancement
- Voice-over post-production

---

## Phase 5 — Speech Intelligence

**Goal:** Convert audio into meaningful text and speaker information.

### API

```python
audio.transcribe()
audio.detect_language()
audio.identify_speakers()
```

### Technology Stack

| Package | Purpose |
|---------|---------|
| Whisper / Faster-Whisper | Speech-to-text |
| Silero | Lightweight VAD + STT |
| pyannote.audio | Speaker diarization |

---

## Phase 6 — Audio Search & Embeddings

**Goal:** Semantic audio understanding — find content by meaning, not filename.

### API

```python
embedding = audio.embed()
audio.search("discussion about sales")
```

### Technology Stack

| Package | Purpose |
|---------|---------|
| OpenAI Embeddings | Text embedding of transcripts |
| BGE Embeddings | Local alternative |
| Sentence Transformers | Open-source embedding models |

### Use Cases

- Podcast search
- Meeting archives
- Audio content discovery

---

## Phase 7 — AI Workflows

**Goal:** Move beyond audio editing into intelligent content extraction.

### API

```python
audio.summarize()
audio.extract_topics()
audio.extract_actions()
audio.generate_minutes()
```

### Technology Stack

| Package | Purpose |
|---------|---------|
| Ollama | Local LLM inference |
| OpenAI API | Cloud LLM option |

---

## Phase 8 — Streaming Support

**Goal:** Process audio in real time from microphone or stream.

### API

```python
Audio.stream()
Audio.live_transcribe()
Audio.live_clean()
```

### Technology Stack

| Package | Purpose |
|---------|---------|
| `sounddevice` | Cross-platform microphone access |
| `pyaudio` | Alternative mic input |
| `websockets` | Real-time browser streaming |

---

## Phase 9 — Plugin Architecture

**Goal:** Let developers extend AIAudio with custom effects, AI models, and exporters.

### API

```python
@plugin
class CustomNoiseReducer:
    ...
```

### Plugin Categories

- Effects
- AI Models
- Export Formats
- Audio Analysis

---

## Phase 10 — Agentic Audio Platform

**Goal:** Transform AIAudio into an AI-native audio operating system — a full pipeline from raw audio to structured report.

### API

```python
audio = Audio.load("meeting.mp3")

audio.clean()
audio.transcribe()
audio.identify_speakers()
audio.extract_actions()
audio.summarize()

audio.export_report("report.md")
```

### Agent Pipeline

```
Audio File
    ↓
Noise Removal
    ↓
Transcription
    ↓
Speaker Detection
    ↓
Topic Extraction
    ↓
Summarization
    ↓
Action Items
    ↓
Final Report
```

---

## Project Structure

```
aiaudio/
│
├── core/
│   ├── audio.py          # Audio class — main user-facing object
│   ├── loader.py         # format detection, FFmpeg decode
│   └── exporter.py       # FFmpeg encode, format routing
│
├── effects/
│   ├── fade.py
│   ├── normalize.py
│   └── silence.py
│
├── ai/
│   ├── enhancer.py       # noise removal, echo reduction
│   ├── whisper.py        # transcription
│   ├── diarization.py    # speaker detection
│   ├── embeddings.py     # audio embeddings
│   └── summarizer.py     # LLM workflows
│
├── gui/
│   ├── __main__.py       # python -m aiaudio.gui entry point
│   └── converter.py      # Gradio app
│
├── plugins/
│   └── registry.py
│
├── utils/
│
└── cli/
    └── main.py           # aiaudio convert / transcribe / ...
```

---

## Long-Term Goal

Become the audio equivalent of:

| Library | Role |
|---------|------|
| Pydub | Audio editing |
| Whisper | Transcription |
| Pyannote | Speaker diarization |
| LangChain | AI workflows |

All behind one unified API:

```python
from aiaudio import Audio

audio = Audio.load("meeting.mp3")
audio.clean()
audio.transcribe()
audio.identify_speakers()
audio.extract_actions()
audio.summarize()
audio.export_report("meeting_report.md")
```
