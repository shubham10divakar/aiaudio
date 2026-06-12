"""Phase 2 tests — multi-format support and new Audio methods.

FFmpeg integration tests are skipped automatically when FFmpeg is not installed.
Format-routing and pure-Python method tests run unconditionally.
"""
import math
import os

import numpy as np
import pytest

from aiaudio import Audio
from aiaudio.core.audio import Audio as _Audio
from aiaudio.core.ffmpeg import is_available as ffmpeg_available
from aiaudio.core import loader as _loader, exporter as _exporter

requires_ffmpeg = pytest.mark.skipif(
    not ffmpeg_available(),
    reason="FFmpeg is not installed — skipping format integration tests",
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_audio(duration: float = 1.0, sample_rate: int = 44100, channels: int = 1) -> _Audio:
    n = int(duration * sample_rate)
    t = np.linspace(0, duration, n, endpoint=False)
    samples = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)
    if channels == 2:
        samples = np.stack([samples, samples], axis=1)
    return _Audio(samples, sample_rate)


# ---------------------------------------------------------------------------
# Format routing (no FFmpeg needed)
# ---------------------------------------------------------------------------

class TestFormatRouting:
    def test_wav_still_loads(self, tmp_path):
        a = _make_audio()
        p = str(tmp_path / "test.wav")
        a.export(p)
        loaded = Audio.load(p)
        assert abs(loaded.duration - 1.0) < 0.02

    def test_wav_export_no_ffmpeg_needed(self, tmp_path):
        a = _make_audio()
        p = str(tmp_path / "out.wav")
        a.export(p)
        assert os.path.exists(p)

    def test_non_wav_load_raises_without_ffmpeg(self, tmp_path):
        if ffmpeg_available():
            pytest.skip("FFmpeg present — not testing missing-FFmpeg error path")
        from aiaudio.core.ffmpeg import _require
        with pytest.raises(RuntimeError, match="FFmpeg"):
            _require()

    def test_ffmpeg_availability_check(self):
        result = ffmpeg_available()
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# resample()
# ---------------------------------------------------------------------------

class TestResample:
    def test_same_rate_returns_copy(self):
        a = _make_audio(sample_rate=44100)
        b = a.resample(44100)
        assert b is not a
        assert b.sample_rate == 44100
        assert abs(b.duration - a.duration) < 0.02

    def test_downsample(self):
        a = _make_audio(duration=2.0, sample_rate=44100)
        b = a.resample(22050)
        assert b.sample_rate == 22050
        assert abs(b.duration - 2.0) < 0.05

    def test_upsample(self):
        a = _make_audio(duration=2.0, sample_rate=22050)
        b = a.resample(44100)
        assert b.sample_rate == 44100
        assert abs(b.duration - 2.0) < 0.05

    def test_resample_immutable(self):
        a = _make_audio(sample_rate=44100)
        _ = a.resample(22050)
        assert a.sample_rate == 44100

    def test_resample_stereo(self):
        a = _make_audio(sample_rate=44100, channels=2)
        b = a.resample(22050)
        assert b.sample_rate == 22050
        assert b.channels == 2


# ---------------------------------------------------------------------------
# set_channels()
# ---------------------------------------------------------------------------

class TestSetChannels:
    def test_mono_to_stereo(self):
        a = _make_audio(channels=1)
        b = a.set_channels(2)
        assert b.channels == 2
        assert b._samples.ndim == 2

    def test_stereo_to_mono(self):
        a = _make_audio(channels=2)
        b = a.set_channels(1)
        assert b.channels == 1
        assert b._samples.ndim == 1

    def test_same_channel_returns_copy(self):
        a = _make_audio(channels=1)
        b = a.set_channels(1)
        assert b is not a
        assert b.channels == 1

    def test_invalid_channels_raises(self):
        a = _make_audio()
        with pytest.raises(ValueError):
            a.set_channels(3)

    def test_immutable(self):
        a = _make_audio(channels=1)
        _ = a.set_channels(2)
        assert a.channels == 1

    def test_duration_preserved(self):
        a = _make_audio(duration=2.0, channels=1)
        b = a.set_channels(2)
        assert abs(b.duration - 2.0) < 0.02


# ---------------------------------------------------------------------------
# FFmpeg integration (skip if not installed)
# ---------------------------------------------------------------------------

class TestFFmpegFormats:
    @requires_ffmpeg
    def test_load_mp3(self, tmp_path):
        a = _make_audio(duration=2.0)
        wav = str(tmp_path / "source.wav")
        mp3 = str(tmp_path / "out.mp3")
        a.export(wav)
        # Convert WAV → MP3 via FFmpeg
        import subprocess
        subprocess.run(["ffmpeg", "-i", wav, mp3, "-y"], capture_output=True, check=True)
        loaded = Audio.load(mp3)
        assert abs(loaded.duration - 2.0) < 0.2  # MP3 encoding adds a small pad

    @requires_ffmpeg
    def test_export_mp3(self, tmp_path):
        a = _make_audio(duration=1.0)
        mp3 = str(tmp_path / "out.mp3")
        a.export(mp3)
        assert os.path.exists(mp3)
        assert os.path.getsize(mp3) > 0

    @requires_ffmpeg
    def test_export_flac(self, tmp_path):
        a = _make_audio(duration=1.0)
        flac = str(tmp_path / "out.flac")
        a.export(flac)
        assert os.path.exists(flac)
        loaded = Audio.load(flac)
        assert abs(loaded.duration - 1.0) < 0.02

    @requires_ffmpeg
    def test_export_ogg(self, tmp_path):
        a = _make_audio(duration=1.0)
        ogg = str(tmp_path / "out.ogg")
        a.export(ogg)
        assert os.path.exists(ogg)

    @requires_ffmpeg
    def test_round_trip_flac(self, tmp_path):
        a = _make_audio(duration=1.0, sample_rate=44100)
        flac = str(tmp_path / "rt.flac")
        a.export(flac)
        b = Audio.load(flac)
        assert b.sample_rate == 44100
        assert b.channels == 1
        assert abs(b.duration - 1.0) < 0.02

    @requires_ffmpeg
    def test_convert_with_resample(self, tmp_path):
        a = _make_audio(duration=1.0, sample_rate=44100)
        flac = str(tmp_path / "out.flac")
        a.resample(22050).export(flac)
        b = Audio.load(flac)
        assert b.sample_rate == 22050

    @requires_ffmpeg
    def test_probe(self, tmp_path):
        from aiaudio.core.ffmpeg import probe
        a = _make_audio(duration=1.0, sample_rate=44100, channels=2)
        wav = str(tmp_path / "test.wav")
        a.export(wav)
        info = probe(wav)
        assert info["sample_rate"] == 44100
        assert info["channels"] == 2


# ---------------------------------------------------------------------------
# CLI convert command
# ---------------------------------------------------------------------------

class TestCLIConvert:
    def test_convert_parser(self):
        from aiaudio.cli.main import build_parser
        parser = build_parser()
        args = parser.parse_args(["convert", "in.mp3", "-o", "out.flac"])
        assert args.command == "convert"
        assert args.file == "in.mp3"
        assert args.output == "out.flac"
        assert args.sample_rate is None
        assert args.channels is None

    def test_convert_parser_with_options(self):
        from aiaudio.cli.main import build_parser
        parser = build_parser()
        args = parser.parse_args(["convert", "in.wav", "-o", "out.mp3",
                                  "--sample-rate", "22050", "--channels", "1"])
        assert args.sample_rate == 22050
        assert args.channels == 1

    @requires_ffmpeg
    def test_convert_wav_to_flac(self, tmp_path):
        from aiaudio.cli.main import build_parser, cmd_convert
        a = _make_audio()
        inp = str(tmp_path / "in.wav")
        out = str(tmp_path / "out.flac")
        a.export(inp)
        args = build_parser().parse_args(["convert", inp, "-o", out])
        cmd_convert(args)
        assert os.path.exists(out)
