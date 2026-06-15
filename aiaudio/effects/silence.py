"""Silence removal — strip silent gaps longer than a threshold."""
from __future__ import annotations

import numpy as np


def remove_silence(
    samples: np.ndarray,
    sample_rate: int,
    threshold_db: float = -40.0,
    min_silence_ms: float = 100.0,
) -> np.ndarray:
    """Remove silent runs longer than ``min_silence_ms``.

    A sample is "silent" when its amplitude is below ``threshold_db`` (relative
    to full scale, e.g. -40 dB). Short pauses below ``min_silence_ms`` are kept
    so natural gaps survive; only longer silences are cut.
    """
    n = len(samples)
    if n == 0:
        return samples.copy()

    # Per-sample amplitude (max across channels for stereo).
    amp = np.abs(samples) if samples.ndim == 1 else np.abs(samples).max(axis=1)
    threshold = 10 ** (threshold_db / 20)
    loud = amp >= threshold

    min_silence = max(1, int(sample_rate * min_silence_ms / 1000))
    keep = loud.copy()

    # Walk contiguous runs (cheap: one iteration per run, not per sample).
    edges = np.flatnonzero(np.diff(loud.astype(np.int8)))
    starts = np.concatenate(([0], edges + 1))
    ends = np.concatenate((edges + 1, [n]))
    for s, e in zip(starts, ends):
        if not loud[s] and (e - s) < min_silence:
            keep[s:e] = True  # short pause — keep it

    return samples[keep].copy()
