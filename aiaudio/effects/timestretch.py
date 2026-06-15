"""Tempo change without pitch change (overlap-add time stretching).

``speed(factor)`` makes audio play ``factor`` times faster (factor > 1) or
slower (factor < 1). Unlike resampling, the pitch is preserved: we re-time the
signal by overlap-adding windowed analysis frames at a different synthesis hop.

This is plain OLA (no phase locking) — fast, dependency-free, and good for
speech/voice. Output length is approximately ``len(input) / factor``.
"""
from __future__ import annotations

import numpy as np


def _stretch_channel(x: np.ndarray, frame: int, hop_syn: int, hop_ana: float) -> np.ndarray:
    window = np.hanning(frame).astype(np.float32)
    n_in = len(x)
    if n_in < frame:
        return x.astype(np.float32).copy()

    n_frames = int((n_in - frame) / hop_ana) + 1
    out_len = (n_frames - 1) * hop_syn + frame
    out = np.zeros(out_len, dtype=np.float32)
    norm = np.zeros(out_len, dtype=np.float32)

    for i in range(n_frames):
        a = int(round(i * hop_ana))
        seg = x[a:a + frame]
        if len(seg) < frame:
            break
        s = i * hop_syn
        out[s:s + frame] += seg * window
        norm[s:s + frame] += window

    norm[norm < 1e-6] = 1.0
    return (out / norm).astype(np.float32)


def speed(samples: np.ndarray, sample_rate: int, factor: float) -> np.ndarray:
    """Change tempo by ``factor`` while preserving pitch.

    ``factor=1.5`` → 1.5× faster (shorter); ``factor=0.5`` → half speed (longer).
    """
    if factor <= 0:
        raise ValueError(f"speed factor must be positive, got {factor}")
    if factor == 1.0:
        return samples.copy()

    # ~40 ms frames with 75% overlap (synthesis hop = frame / 4).
    frame = max(8, int(sample_rate * 0.04))
    hop_syn = max(1, frame // 4)
    hop_ana = hop_syn * factor  # analysis advances faster/slower than synthesis

    if samples.ndim == 1:
        return _stretch_channel(samples, frame, hop_syn, hop_ana)

    channels = [
        _stretch_channel(samples[:, c], frame, hop_syn, hop_ana)
        for c in range(samples.shape[1])
    ]
    length = min(len(c) for c in channels)
    return np.stack([c[:length] for c in channels], axis=1).astype(np.float32)
