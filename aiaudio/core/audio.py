from __future__ import annotations

import math

import numpy as np

from . import loader as _loader
from . import exporter as _exporter


class Audio:
    """Immutable audio object. Every operation returns a new Audio instance."""

    def __init__(self, samples: np.ndarray, sample_rate: int) -> None:
        self._samples = samples
        self._sample_rate = sample_rate

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, path: str) -> Audio:
        """Load any supported audio file (WAV natively; MP3/FLAC/OGG/AAC/M4A via FFmpeg)."""
        samples, sample_rate = _loader.load(path)
        return cls(samples, sample_rate)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def duration(self) -> float:
        return len(self._samples) / self._sample_rate

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def channels(self) -> int:
        return 1 if self._samples.ndim == 1 else self._samples.shape[1]

    # ------------------------------------------------------------------
    # Editing — all return new Audio objects
    # ------------------------------------------------------------------

    def slice(self, start: float, end: float) -> Audio:
        """Return a new Audio covering [start, end] seconds."""
        start_idx = int(start * self._sample_rate)
        end_idx = int(end * self._sample_rate)
        return Audio(self._samples[start_idx:end_idx].copy(), self._sample_rate)

    def __add__(self, other: Audio) -> Audio:
        """Concatenate two Audio objects with matching sample rates."""
        if self._sample_rate != other._sample_rate:
            raise ValueError(
                f"Sample rates must match: {self._sample_rate} vs {other._sample_rate}"
            )
        return Audio(np.concatenate([self._samples, other._samples]), self._sample_rate)

    def increase_volume(self, db: float) -> Audio:
        """Amplify by db decibels. Clips at the [-1, 1] boundary."""
        factor = 10 ** (db / 20)
        return Audio(np.clip(self._samples * factor, -1.0, 1.0), self._sample_rate)

    def decrease_volume(self, db: float) -> Audio:
        """Attenuate by db decibels."""
        return self.increase_volume(-abs(db))

    def resample(self, target_rate: int) -> Audio:
        """Return a new Audio resampled to target_rate Hz."""
        if target_rate == self._sample_rate:
            return Audio(self._samples.copy(), self._sample_rate)
        from scipy.signal import resample_poly
        gcd = math.gcd(self._sample_rate, target_rate)
        up = target_rate // gcd
        down = self._sample_rate // gcd
        resampled = resample_poly(self._samples, up, down, axis=0)
        return Audio(resampled.astype(np.float32), target_rate)

    def set_channels(self, channels: int) -> Audio:
        """Convert between mono and stereo. channels must be 1 or 2."""
        if channels not in (1, 2):
            raise ValueError(f"channels must be 1 or 2, got {channels}")
        if channels == self.channels:
            return Audio(self._samples.copy(), self._sample_rate)
        if channels == 1:
            mono = self._samples.mean(axis=1).astype(np.float32)
            return Audio(mono, self._sample_rate)
        # channels == 2: duplicate mono channel
        stereo = np.stack([self._samples, self._samples], axis=1).astype(np.float32)
        return Audio(stereo, self._sample_rate)

    # ------------------------------------------------------------------
    # Effects (Phase 3) — all return new Audio objects
    # ------------------------------------------------------------------

    def fade_in(self, duration_ms: float) -> Audio:
        """Linear fade in over the first ``duration_ms`` milliseconds."""
        from ..effects import fade
        return Audio(fade.fade_in(self._samples, self._sample_rate, duration_ms), self._sample_rate)

    def fade_out(self, duration_ms: float) -> Audio:
        """Linear fade out over the last ``duration_ms`` milliseconds."""
        from ..effects import fade
        return Audio(fade.fade_out(self._samples, self._sample_rate, duration_ms), self._sample_rate)

    def normalize(self, headroom_db: float = 0.0) -> Audio:
        """Peak-normalize so the loudest sample sits at ``-headroom_db`` dBFS."""
        from ..effects import normalize as _normalize
        return Audio(_normalize.normalize(self._samples, headroom_db), self._sample_rate)

    def reverse(self) -> Audio:
        """Reverse the audio in time."""
        return Audio(self._samples[::-1].copy(), self._sample_rate)

    def speed(self, factor: float) -> Audio:
        """Change tempo by ``factor`` while preserving pitch (1.5 = 1.5× faster)."""
        from ..effects import timestretch
        return Audio(timestretch.speed(self._samples, self._sample_rate, factor), self._sample_rate)

    def remove_silence(self, threshold_db: float = -40.0, min_silence_ms: float = 100.0) -> Audio:
        """Strip silent gaps longer than ``min_silence_ms`` (silence < ``threshold_db``)."""
        from ..effects import silence
        return Audio(
            silence.remove_silence(self._samples, self._sample_rate, threshold_db, min_silence_ms),
            self._sample_rate,
        )

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export(self, path: str) -> None:
        """Export to any supported format (WAV natively; MP3/FLAC/OGG/AAC/M4A via FFmpeg)."""
        _exporter.export(self._samples, self._sample_rate, path)

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Audio(duration={self.duration:.2f}s, "
            f"sample_rate={self.sample_rate}Hz, "
            f"channels={self.channels})"
        )
