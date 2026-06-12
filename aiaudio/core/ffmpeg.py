"""FFmpeg subprocess bridge — decode and encode any audio format."""
from __future__ import annotations

import json
import shutil
import subprocess

import numpy as np


# ---------------------------------------------------------------------------
# Availability
# ---------------------------------------------------------------------------

def is_available() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def _require() -> None:
    if not is_available():
        raise RuntimeError(
            "FFmpeg is not installed or not on PATH.\n"
            "Install it from https://ffmpeg.org/download.html\n"
            "  Windows : winget install ffmpeg\n"
            "  macOS   : brew install ffmpeg\n"
            "  Linux   : sudo apt install ffmpeg"
        )


# ---------------------------------------------------------------------------
# Probe
# ---------------------------------------------------------------------------

def probe(path: str) -> dict:
    """Return sample_rate and channels for the first audio stream."""
    _require()
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-select_streams", "a:0",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    if not data.get("streams"):
        raise ValueError(f"No audio stream found in: {path}")
    stream = data["streams"][0]
    return {
        "sample_rate": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
    }


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_audio(path: str) -> tuple[np.ndarray, int]:
    """Decode any FFmpeg-supported file to a float32 numpy array in [-1, 1]."""
    _require()
    info = probe(path)
    sample_rate = info["sample_rate"]
    channels = info["channels"]

    cmd = [
        "ffmpeg", "-i", path,
        "-f", "s16le",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", str(channels),
        "-",
    ]
    result = subprocess.run(cmd, capture_output=True, check=True)

    samples = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32)
    samples /= 32768.0

    if channels > 1:
        samples = samples.reshape(-1, channels)

    return samples, sample_rate


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_audio(samples: np.ndarray, sample_rate: int, path: str) -> None:
    """Encode a float32 PCM array to any format FFmpeg supports (inferred from extension)."""
    _require()
    samples_int = np.clip(samples * 32767, -32768, 32767).astype(np.int16)
    n_channels = 1 if samples_int.ndim == 1 else samples_int.shape[1]

    cmd = [
        "ffmpeg", "-y",
        "-f", "s16le",
        "-ar", str(sample_rate),
        "-ac", str(n_channels),
        "-i", "pipe:0",
        path,
    ]
    subprocess.run(cmd, input=samples_int.tobytes(), capture_output=True, check=True)
