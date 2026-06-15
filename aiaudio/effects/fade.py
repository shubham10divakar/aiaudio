"""Linear fade in / out envelopes.

All functions are pure: they take a float32 sample array (mono = 1-D, stereo =
(N, 2)) and return a new array, never mutating the input.
"""
from __future__ import annotations

import numpy as np


def _apply_envelope(samples: np.ndarray, env: np.ndarray) -> np.ndarray:
    """Multiply samples by a per-sample gain envelope, broadcasting for stereo."""
    if samples.ndim == 2:
        env = env[:, None]
    return (samples * env).astype(np.float32)


def _fade_length(sample_rate: int, duration_ms: float, total: int) -> int:
    """Number of samples covered by a fade, clamped to the clip length."""
    n = int(sample_rate * duration_ms / 1000)
    return max(0, min(n, total))


def fade_in(samples: np.ndarray, sample_rate: int, duration_ms: float) -> np.ndarray:
    """Ramp gain linearly from 0 → 1 over the first ``duration_ms`` milliseconds."""
    total = len(samples)
    n = _fade_length(sample_rate, duration_ms, total)
    if n == 0:
        return samples.copy()
    env = np.ones(total, dtype=np.float32)
    env[:n] = np.linspace(0.0, 1.0, n, dtype=np.float32)
    return _apply_envelope(samples, env)


def fade_out(samples: np.ndarray, sample_rate: int, duration_ms: float) -> np.ndarray:
    """Ramp gain linearly from 1 → 0 over the last ``duration_ms`` milliseconds."""
    total = len(samples)
    n = _fade_length(sample_rate, duration_ms, total)
    if n == 0:
        return samples.copy()
    env = np.ones(total, dtype=np.float32)
    env[total - n:] = np.linspace(1.0, 0.0, n, dtype=np.float32)
    return _apply_envelope(samples, env)
