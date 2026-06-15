"""Phase 4 tests — AI audio enhancement (noise reduction).

The default spectral backend is pure numpy/scipy, so it runs unconditionally.
The deep-learning backend is only checked for its optional-dependency error path.
"""
import numpy as np
import pytest

from aiaudio.core.audio import Audio as _Audio
from aiaudio.ai import enhancer


def _noisy_tone_bursts(sample_rate=16000, seed=0):
    """Tone bursts with silent gaps, plus white noise.

    Returns (clean, noisy, gap_slice, active_slice) so tests can compare the
    noise floor in the silent gaps against the energy in the active region.
    """
    rng = np.random.default_rng(seed)
    burst_n = sample_rate // 2          # 0.5 s tone
    gap_n = sample_rate // 2            # 0.5 s silence
    t = np.linspace(0, 0.5, burst_n, endpoint=False)
    tone = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)
    gap = np.zeros(gap_n, dtype=np.float32)

    clean = np.concatenate([gap, tone, gap, tone, gap]).astype(np.float32)
    noise = rng.normal(0, 0.05, len(clean)).astype(np.float32)
    noisy = (clean + noise).astype(np.float32)

    first_gap = slice(0, gap_n)
    first_active = slice(gap_n, gap_n + burst_n)
    return clean, noisy, first_gap, first_active


def _energy(x):
    return float(np.mean(x ** 2))


class TestSpectralNoiseReduction:
    def test_reduces_noise_floor_in_gaps(self):
        clean, noisy, gap, active = _noisy_tone_bursts()
        out = enhancer.reduce_noise(noisy, 16000)
        # Residual energy in the silent gap should drop after denoising.
        assert _energy(out[gap]) < _energy(noisy[gap])

    def test_retains_signal_in_active_region(self):
        clean, noisy, gap, active = _noisy_tone_bursts()
        out = enhancer.reduce_noise(noisy, 16000)
        # The tone should largely survive (don't gate out the real signal).
        assert _energy(out[active]) > 0.4 * _energy(noisy[active])

    def test_improves_correlation_with_clean(self):
        clean, noisy, gap, active = _noisy_tone_bursts()
        out = enhancer.reduce_noise(noisy, 16000)

        def corr(a, b):
            a = a - a.mean()
            b = b - b.mean()
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))

        assert corr(out, clean) >= corr(noisy, clean) - 1e-6

    def test_length_preserved(self):
        _, noisy, _, _ = _noisy_tone_bursts()
        out = enhancer.reduce_noise(noisy, 16000)
        assert len(out) == len(noisy)

    def test_stereo(self):
        _, noisy, _, _ = _noisy_tone_bursts()
        stereo = np.stack([noisy, noisy], axis=1)
        out = enhancer.reduce_noise(stereo, 16000)
        assert out.ndim == 2 and out.shape[1] == 2
        assert len(out) == len(noisy)

    def test_short_signal_passthrough(self):
        x = np.array([0.1, -0.2, 0.3], dtype=np.float32)
        out = enhancer.reduce_noise(x, 16000)
        assert np.allclose(out, x)

    def test_unknown_backend_raises(self):
        x = np.zeros(4096, dtype=np.float32)
        with pytest.raises(ValueError, match="backend"):
            enhancer.reduce_noise(x, 16000, backend="bogus")

    def test_output_is_float32(self):
        _, noisy, _, _ = _noisy_tone_bursts()
        out = enhancer.reduce_noise(noisy, 16000)
        assert out.dtype == np.float32


class TestAudioRemoveNoise:
    def test_method_returns_new_audio(self):
        _, noisy, _, _ = _noisy_tone_bursts()
        a = _Audio(noisy, 16000)
        b = a.remove_noise()
        assert b is not a
        assert b.sample_rate == 16000
        assert abs(b.duration - a.duration) < 1e-6

    def test_immutable(self):
        _, noisy, _, _ = _noisy_tone_bursts()
        a = _Audio(noisy.copy(), 16000)
        original = a._samples.copy()
        _ = a.remove_noise()
        assert np.allclose(a._samples, original)


class TestDeepFilterNetBackend:
    def test_missing_dependency_message(self):
        """Without the optional model installed, the error must point to aiaudio[ai]."""
        import importlib.util

        if importlib.util.find_spec("df") is not None:
            pytest.skip("DeepFilterNet is installed — not testing the missing-dep path")

        x = np.zeros(4096, dtype=np.float32)
        with pytest.raises(ImportError, match=r"aiaudio\[ai\]"):
            enhancer.reduce_noise(x, 16000, backend="deepfilternet")
