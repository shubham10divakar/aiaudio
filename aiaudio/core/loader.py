import wave
from pathlib import Path

import numpy as np


_WAV_EXT = {".wav"}
_FFMPEG_EXT = {".mp3", ".flac", ".ogg", ".aac", ".m4a", ".opus", ".wma"}


def load_wav(path: str) -> tuple[np.ndarray, int]:
    with wave.open(path, "rb") as wf:
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
    dtype = dtype_map.get(sample_width, np.int16)

    samples = np.frombuffer(raw, dtype=dtype).astype(np.float32)
    max_val = float(2 ** (8 * sample_width - 1))
    samples /= max_val

    if n_channels > 1:
        samples = samples.reshape(-1, n_channels)

    return samples, sample_rate


def load(path: str) -> tuple[np.ndarray, int]:
    """Load any supported audio file, routing to WAV or FFmpeg as appropriate."""
    ext = Path(path).suffix.lower()
    if ext in _WAV_EXT:
        return load_wav(path)
    if ext in _FFMPEG_EXT or ext not in _WAV_EXT:
        from .ffmpeg import load_audio
        return load_audio(path)
    raise ValueError(f"Unsupported audio format: {ext!r}")
