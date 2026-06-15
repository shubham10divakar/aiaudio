"""Phase 3 tests — audio effects (fade, normalize, reverse, speed, silence).

Pure numpy/scipy effects — no FFmpeg needed, so everything runs unconditionally.
"""
import numpy as np
import pytest

from aiaudio import Audio
from aiaudio.core.audio import Audio as _Audio


def _make_audio(duration: float = 1.0, sample_rate: int = 44100, channels: int = 1,
                amplitude: float = 0.5) -> _Audio:
    n = int(duration * sample_rate)
    t = np.linspace(0, duration, n, endpoint=False)
    samples = (np.sin(2 * np.pi * 440 * t) * amplitude).astype(np.float32)
    if channels == 2:
        samples = np.stack([samples, samples], axis=1)
    return _Audio(samples, sample_rate)


# ---------------------------------------------------------------------------
# Fade
# ---------------------------------------------------------------------------

class TestFade:
    def test_fade_in_starts_silent(self):
        a = _make_audio()
        b = a.fade_in(100)
        assert abs(float(b._samples[0])) < 1e-6

    def test_fade_in_preserves_length_and_immutable(self):
        a = _make_audio()
        b = a.fade_in(100)
        assert len(b._samples) == len(a._samples)
        assert float(np.max(np.abs(a._samples))) > 0.4  # original untouched

    def test_fade_out_ends_silent(self):
        a = _make_audio()
        b = a.fade_out(100)
        assert abs(float(b._samples[-1])) < 1e-6

    def test_fade_in_attenuates_start(self):
        a = _make_audio()
        b = a.fade_in(500)
        sr = a.sample_rate
        # Energy in the first 100 ms should drop after fade-in.
        seg = slice(0, sr // 10)
        assert np.sum(b._samples[seg] ** 2) < np.sum(a._samples[seg] ** 2)

    def test_fade_stereo(self):
        a = _make_audio(channels=2)
        b = a.fade_in(100)
        assert b.channels == 2
        assert np.allclose(b._samples[0], 0.0, atol=1e-6)

    def test_fade_longer_than_clip_clamps(self):
        a = _make_audio(duration=0.1)
        b = a.fade_in(10_000)  # far longer than the clip
        assert len(b._samples) == len(a._samples)
        assert abs(float(b._samples[0])) < 1e-6


# ---------------------------------------------------------------------------
# Normalize
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_normalize_reaches_full_scale(self):
        a = _make_audio(amplitude=0.2)
        b = a.normalize()
        assert abs(float(np.max(np.abs(b._samples))) - 1.0) < 1e-3

    def test_normalize_headroom(self):
        a = _make_audio(amplitude=0.2)
        b = a.normalize(headroom_db=6.0)
        peak = float(np.max(np.abs(b._samples)))
        assert abs(peak - 10 ** (-6 / 20)) < 1e-3  # ~0.501

    def test_normalize_silence_unchanged(self):
        a = _Audio(np.zeros(1000, dtype=np.float32), 44100)
        b = a.normalize()
        assert float(np.max(np.abs(b._samples))) == 0.0

    def test_normalize_immutable(self):
        a = _make_audio(amplitude=0.2)
        _ = a.normalize()
        assert abs(float(np.max(np.abs(a._samples))) - 0.2) < 1e-3


# ---------------------------------------------------------------------------
# Reverse
# ---------------------------------------------------------------------------

class TestReverse:
    def test_reverse_flips(self):
        a = _Audio(np.array([0.1, 0.2, 0.3], dtype=np.float32), 44100)
        b = a.reverse()
        assert np.allclose(b._samples, [0.3, 0.2, 0.1])

    def test_reverse_twice_is_identity(self):
        a = _make_audio()
        b = a.reverse().reverse()
        assert np.allclose(a._samples, b._samples)

    def test_reverse_preserves_duration(self):
        a = _make_audio(duration=2.0)
        b = a.reverse()
        assert abs(b.duration - a.duration) < 1e-6

    def test_reverse_stereo(self):
        a = _make_audio(channels=2)
        b = a.reverse()
        assert b.channels == 2


# ---------------------------------------------------------------------------
# Speed (tempo change, pitch preserved)
# ---------------------------------------------------------------------------

class TestSpeed:
    def test_speed_up_shortens(self):
        a = _make_audio(duration=2.0)
        b = a.speed(2.0)
        assert abs(b.duration - 1.0) < 0.1

    def test_slow_down_lengthens(self):
        a = _make_audio(duration=2.0)
        b = a.speed(0.5)
        assert abs(b.duration - 4.0) < 0.2

    def test_speed_preserves_sample_rate(self):
        a = _make_audio(duration=2.0, sample_rate=44100)
        b = a.speed(1.5)
        assert b.sample_rate == 44100  # pitch preserved -> same rate

    def test_speed_one_is_noop_copy(self):
        a = _make_audio()
        b = a.speed(1.0)
        assert b is not a
        assert np.allclose(a._samples, b._samples)

    def test_speed_invalid_factor(self):
        a = _make_audio()
        with pytest.raises(ValueError):
            a.speed(0)

    def test_speed_stereo(self):
        a = _make_audio(duration=2.0, channels=2)
        b = a.speed(2.0)
        assert b.channels == 2
        assert abs(b.duration - 1.0) < 0.1


# ---------------------------------------------------------------------------
# Remove silence
# ---------------------------------------------------------------------------

class TestRemoveSilence:
    def _clip_with_silence(self, sr=44100):
        # 0.5s silence + 0.5s tone + 0.5s silence
        silence = np.zeros(sr // 2, dtype=np.float32)
        t = np.linspace(0, 0.5, sr // 2, endpoint=False)
        tone = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)
        return _Audio(np.concatenate([silence, tone, silence]), sr)

    def test_trims_leading_and_trailing_silence(self):
        a = self._clip_with_silence()
        b = a.remove_silence()
        # Only the ~0.5s tone should remain.
        assert b.duration < a.duration
        assert abs(b.duration - 0.5) < 0.1

    def test_keeps_short_pauses(self):
        sr = 44100
        t = np.linspace(0, 0.3, int(sr * 0.3), endpoint=False)
        tone = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)
        short_gap = np.zeros(int(sr * 0.05), dtype=np.float32)  # 50 ms < 100 ms default
        a = _Audio(np.concatenate([tone, short_gap, tone]), sr)
        b = a.remove_silence(min_silence_ms=100)
        # Short gap retained -> length roughly unchanged.
        assert abs(b.duration - a.duration) < 0.02

    def test_empty_stays_empty(self):
        a = _Audio(np.zeros(0, dtype=np.float32), 44100)
        b = a.remove_silence()
        assert len(b._samples) == 0

    def test_immutable(self):
        a = self._clip_with_silence()
        original_len = len(a._samples)
        _ = a.remove_silence()
        assert len(a._samples) == original_len


# ---------------------------------------------------------------------------
# Chaining
# ---------------------------------------------------------------------------

class TestChaining:
    def test_chain_effects(self):
        a = _make_audio(duration=2.0, amplitude=0.2)
        out = a.normalize().fade_in(100).fade_out(100).reverse()
        assert out.sample_rate == a.sample_rate
        assert abs(out.duration - a.duration) < 1e-6
        assert abs(float(out._samples[0])) < 1e-6   # fade_out end became start
        assert abs(float(out._samples[-1])) < 1e-6  # fade_in start became end


# ---------------------------------------------------------------------------
# CLI parsers
# ---------------------------------------------------------------------------

class TestCLIEffects:
    def test_fade_parser(self):
        from aiaudio.cli.main import build_parser
        args = build_parser().parse_args(["fade", "in.wav", "--in", "500", "--out", "300", "-o", "out.wav"])
        assert args.command == "fade"
        assert args.in_ms == 500
        assert args.out_ms == 300

    def test_speed_parser(self):
        from aiaudio.cli.main import build_parser
        args = build_parser().parse_args(["speed", "in.wav", "1.5", "-o", "out.wav"])
        assert args.factor == 1.5

    def test_normalize_parser(self):
        from aiaudio.cli.main import build_parser
        args = build_parser().parse_args(["normalize", "in.wav", "--headroom", "3", "-o", "out.wav"])
        assert args.headroom == 3.0

    def test_silence_parser(self):
        from aiaudio.cli.main import build_parser
        args = build_parser().parse_args(
            ["silence", "in.wav", "--threshold", "-30", "--min-silence", "200", "-o", "out.wav"]
        )
        assert args.threshold == -30.0
        assert args.min_silence == 200.0

    def test_reverse_parser(self):
        from aiaudio.cli.main import build_parser
        args = build_parser().parse_args(["reverse", "in.wav", "-o", "out.wav"])
        assert args.command == "reverse"

    def test_effect_roundtrip_wav(self, tmp_path):
        from aiaudio.cli.main import build_parser, cmd_normalize
        a = _make_audio(amplitude=0.2)
        inp = str(tmp_path / "in.wav")
        out = str(tmp_path / "out.wav")
        a.export(inp)
        cmd_normalize(build_parser().parse_args(["normalize", inp, "-o", out]))
        loaded = Audio.load(out)
        assert float(np.max(np.abs(loaded._samples))) > 0.9
