import wave
from pathlib import Path

import numpy as np


def export_wav(samples: np.ndarray, sample_rate: int, path: str) -> None:
    samples_int = np.clip(samples * 32767, -32768, 32767).astype(np.int16)
    n_channels = 1 if samples_int.ndim == 1 else samples_int.shape[1]

    with wave.open(path, "wb") as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples_int.tobytes())


def export(samples: np.ndarray, sample_rate: int, path: str) -> None:
    """Export to any format, routing to WAV writer or FFmpeg as appropriate."""
    if Path(path).suffix.lower() == ".wav":
        export_wav(samples, sample_rate, path)
    else:
        from .ffmpeg import export_audio
        export_audio(samples, sample_rate, path)
