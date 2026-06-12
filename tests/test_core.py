import os
import numpy as np
import pytest

from aiaudio import Audio
from aiaudio.core.audio import Audio as _Audio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_audio(duration: float = 1.0, sample_rate: int = 44100, channels: int = 1) -> Audio:
    n = int(duration * sample_rate)
    t = np.linspace(0, duration, n, endpoint=False)
    samples = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)
    if channels == 2:
        samples = np.stack([samples, samples], axis=1)
    return _Audio(samples, sample_rate)


# ---------------------------------------------------------------------------
# Load / export round-trip
# ---------------------------------------------------------------------------

class TestLoadExport:
    def test_round_trip(self, tmp_path):
        a = _make_audio(duration=1.0)
        path = str(tmp_path / "test.wav")
        a.export(path)
        loaded = Audio.load(path)
        assert loaded.sample_rate == 44100
        assert loaded.channels == 1
        assert abs(loaded.duration - 1.0) < 0.02

    def test_export_creates_file(self, tmp_path):
        a = _make_audio()
        out = str(tmp_path / "out.wav")
        a.export(out)
        assert os.path.exists(out)

    def test_load_missing_file_raises(self):
        with pytest.raises(Exception):
            Audio.load("nonexistent.wav")


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

class TestProperties:
    def test_duration(self):
        assert abs(_make_audio(duration=2.5).duration - 2.5) < 0.02

    def test_sample_rate(self):
        assert _make_audio(sample_rate=22050).sample_rate == 22050

    def test_channels_mono(self):
        assert _make_audio(channels=1).channels == 1

    def test_channels_stereo(self):
        assert _make_audio(channels=2).channels == 2

    def test_repr(self):
        r = repr(_make_audio())
        assert "Audio(" in r
        assert "Hz" in r


# ---------------------------------------------------------------------------
# Slice
# ---------------------------------------------------------------------------

class TestSlice:
    def test_duration(self):
        a = _make_audio(duration=10.0)
        assert abs(a.slice(2.0, 5.0).duration - 3.0) < 0.02

    def test_returns_new_object(self):
        a = _make_audio(duration=5.0)
        assert a.slice(0, 2.0) is not a

    def test_immutable(self):
        a = _make_audio(duration=5.0)
        original_len = len(a._samples)
        _ = a.slice(0, 2.0)
        assert len(a._samples) == original_len

    def test_slice_full(self):
        a = _make_audio(duration=3.0)
        assert abs(a.slice(0, 3.0).duration - 3.0) < 0.02


# ---------------------------------------------------------------------------
# Concatenation
# ---------------------------------------------------------------------------

class TestConcat:
    def test_duration_sums(self):
        a = _make_audio(duration=2.0)
        b = _make_audio(duration=3.0)
        assert abs((a + b).duration - 5.0) < 0.02

    def test_returns_new_object(self):
        a = _make_audio()
        b = _make_audio()
        assert (a + b) is not a

    def test_mismatched_sample_rate_raises(self):
        a = _make_audio(sample_rate=44100)
        b = _make_audio(sample_rate=22050)
        with pytest.raises(ValueError):
            _ = a + b

    def test_three_way_concat(self):
        clips = [_make_audio(duration=1.0) for _ in range(3)]
        merged = clips[0] + clips[1] + clips[2]
        assert abs(merged.duration - 3.0) < 0.02


# ---------------------------------------------------------------------------
# Volume
# ---------------------------------------------------------------------------

class TestVolume:
    def test_increase_returns_new(self):
        a = _make_audio()
        assert a.increase_volume(6) is not a

    def test_decrease_returns_new(self):
        a = _make_audio()
        assert a.decrease_volume(6) is not a

    def test_original_unchanged(self):
        a = _make_audio()
        original_max = float(np.abs(a._samples).max())
        _ = a.increase_volume(6)
        assert abs(float(np.abs(a._samples).max()) - original_max) < 1e-6

    def test_louder_has_higher_amplitude(self):
        a = _make_audio()
        louder = a.increase_volume(6)
        assert np.abs(louder._samples).max() >= np.abs(a._samples).max()

    def test_quieter_has_lower_amplitude(self):
        a = _make_audio()
        quieter = a.decrease_volume(6)
        assert np.abs(quieter._samples).max() <= np.abs(a._samples).max()

    def test_clipping_stays_within_bounds(self):
        a = _make_audio()
        very_loud = a.increase_volume(100)
        assert float(np.abs(very_loud._samples).max()) <= 1.0
