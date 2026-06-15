"""Phase 4 — audio enhancement (noise reduction).

The default backend is pure numpy/scipy spectral gating: it works out of the box
with no heavy dependencies. A higher-quality deep-learning backend
(``backend="deepfilternet"``) is lazily imported and only requires the optional
``aiaudio[ai]`` extra.

All functions are pure: they take a float32 sample array (mono = 1-D, stereo =
(N, 2)) and return a new array of the same length, never mutating the input.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import istft, stft


def _smooth_rows(mask: np.ndarray, width: int) -> np.ndarray:
    """Moving-average smooth each row (frequency bin) over time to curb musical noise."""
    if width <= 1:
        return mask
    kernel = np.ones(width, dtype=np.float32) / width
    return np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), 1, mask)


def _reduce_noise_channel(
    x: np.ndarray,
    sample_rate: int,
    n_fft: int,
    hop: int,
    noise_percentile: float,
    oversubtraction: float,
    gain_floor: float,
) -> np.ndarray:
    """Spectral-subtraction denoise of a single (mono) channel."""
    if len(x) < n_fft:
        return x.astype(np.float32).copy()

    noverlap = n_fft - hop
    f, t, spec = stft(x, fs=sample_rate, nperseg=n_fft, noverlap=noverlap, boundary="zeros")
    mag = np.abs(spec)
    phase = np.angle(spec)

    # Stationary-noise estimate: a low percentile of each frequency bin over time
    # captures the noise floor (the level a bin sits at during quiet stretches).
    noise = np.percentile(mag, noise_percentile, axis=1, keepdims=True)

    power = mag ** 2
    clean_power = np.maximum(power - (oversubtraction * noise) ** 2, 0.0)
    gain = clean_power / (power + 1e-12)
    gain = np.maximum(gain, gain_floor)  # never fully null a bin -> fewer artifacts
    gain = _smooth_rows(gain, width=3)

    spec_clean = gain * mag * np.exp(1j * phase)
    _, rec = istft(spec_clean, fs=sample_rate, nperseg=n_fft, noverlap=noverlap, boundary=True)

    # Guarantee exact length preservation (STFT framing can over/undershoot).
    rec = rec[: len(x)]
    if len(rec) < len(x):
        rec = np.pad(rec, (0, len(x) - len(rec)))
    return rec.astype(np.float32)


def reduce_noise(
    samples: np.ndarray,
    sample_rate: int,
    backend: str = "spectral",
    *,
    n_fft: int = 2048,
    hop: int = 512,
    noise_percentile: float = 10.0,
    oversubtraction: float = 1.5,
    gain_floor: float = 0.05,
) -> np.ndarray:
    """Reduce background noise.

    ``backend="spectral"`` (default) uses dependency-free spectral subtraction.
    ``backend="deepfilternet"`` uses the DeepFilterNet model (needs ``aiaudio[ai]``).
    """
    if backend == "deepfilternet":
        return _reduce_noise_deepfilternet(samples, sample_rate)
    if backend != "spectral":
        raise ValueError(f"Unknown noise-reduction backend: {backend!r}")

    if samples.ndim == 1:
        return _reduce_noise_channel(
            samples, sample_rate, n_fft, hop, noise_percentile, oversubtraction, gain_floor
        )
    channels = [
        _reduce_noise_channel(
            samples[:, c], sample_rate, n_fft, hop, noise_percentile, oversubtraction, gain_floor
        )
        for c in range(samples.shape[1])
    ]
    return np.stack(channels, axis=1).astype(np.float32)


def _reduce_noise_deepfilternet(samples: np.ndarray, sample_rate: int) -> np.ndarray:  # pragma: no cover - optional dep
    """Lazy DeepFilterNet backend. Requires the ``aiaudio[ai]`` extra."""
    try:
        from df.enhance import enhance, init_df
    except ImportError as exc:
        raise ImportError(
            "The 'deepfilternet' backend requires extra dependencies. Install them with:\n"
            "    pip install aiaudio[ai]"
        ) from exc

    import torch

    model, df_state, _ = init_df()
    target_sr = df_state.sr()

    # DeepFilterNet operates on mono at its own sample rate; resample via Audio.
    from aiaudio import Audio

    audio = Audio(samples, sample_rate).set_channels(1).resample(target_sr)
    tensor = torch.from_numpy(audio._samples).float().unsqueeze(0)
    enhanced = enhance(model, df_state, tensor)
    out = enhanced.squeeze(0).cpu().numpy().astype(np.float32)

    # Restore the caller's original sample rate and length.
    restored = Audio(out, target_sr).resample(sample_rate)._samples
    restored = restored[: len(samples)]
    if len(restored) < len(samples):
        restored = np.pad(restored, (0, len(samples) - len(restored)))
    return restored.astype(np.float32)
