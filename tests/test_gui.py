"""Phase 2.5 tests — GUI conversion core.

These exercise the pure conversion logic (no Gradio needed). WAV-only paths run
unconditionally; format conversions that need FFmpeg are skipped when it's absent.
"""
import os
import zipfile

import numpy as np
import pytest

from aiaudio.core.audio import Audio as _Audio
from aiaudio.core.ffmpeg import is_available as ffmpeg_available
from aiaudio.gui import converter

requires_ffmpeg = pytest.mark.skipif(
    not ffmpeg_available(),
    reason="FFmpeg is not installed — skipping format integration tests",
)


def _make_audio(duration: float = 1.0, sample_rate: int = 44100, channels: int = 1) -> _Audio:
    n = int(duration * sample_rate)
    t = np.linspace(0, duration, n, endpoint=False)
    samples = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)
    if channels == 2:
        samples = np.stack([samples, samples], axis=1)
    return _Audio(samples, sample_rate)


def _wav(tmp_path, name="in.wav", **kw):
    p = str(tmp_path / name)
    _make_audio(**kw).export(p)
    return p


# ---------------------------------------------------------------------------
# Dropdown label parsing
# ---------------------------------------------------------------------------

class TestParsing:
    def test_sample_rate_keep(self):
        assert converter.parse_sample_rate("Keep original") is None
        assert converter.parse_sample_rate(None) is None

    def test_sample_rate_value(self):
        assert converter.parse_sample_rate("22050") == 22050

    def test_channels_keep(self):
        assert converter.parse_channels("Keep") is None
        assert converter.parse_channels(None) is None

    def test_channels_mono_stereo(self):
        assert converter.parse_channels("Mono") == 1
        assert converter.parse_channels("Stereo") == 2


# ---------------------------------------------------------------------------
# convert_one / convert_batch (WAV — no FFmpeg)
# ---------------------------------------------------------------------------

class TestConvertCore:
    def test_convert_one_wav(self, tmp_path):
        src = _wav(tmp_path)
        out = converter.convert_one(src, "wav", out_dir=str(tmp_path / "out"))
        assert os.path.exists(out)
        assert out.endswith("in.wav")

    def test_convert_one_with_resample(self, tmp_path):
        src = _wav(tmp_path, sample_rate=44100)
        out = converter.convert_one(src, "wav", sample_rate=22050, out_dir=str(tmp_path / "out"))
        assert converter.Audio.load(out).sample_rate == 22050

    def test_convert_one_with_channels(self, tmp_path):
        src = _wav(tmp_path, channels=2)
        out = converter.convert_one(src, "wav", channels=1, out_dir=str(tmp_path / "out"))
        assert converter.Audio.load(out).channels == 1

    def test_convert_one_rejects_unknown_format(self, tmp_path):
        src = _wav(tmp_path)
        with pytest.raises(ValueError, match="Unsupported"):
            converter.convert_one(src, "xyz", out_dir=str(tmp_path / "out"))

    def test_batch_all_succeed(self, tmp_path):
        srcs = [_wav(tmp_path, name=f"a{i}.wav") for i in range(3)]
        results = converter.convert_batch(srcs, "wav", out_dir=str(tmp_path / "out"))
        assert len(results) == 3
        assert all(r.ok for r in results)

    def test_batch_isolates_failures(self, tmp_path):
        good = _wav(tmp_path, name="good.wav")
        bad = str(tmp_path / "missing.wav")  # never created → load fails
        results = converter.convert_batch([good, bad], "wav", out_dir=str(tmp_path / "out"))
        assert results[0].ok
        assert not results[1].ok
        assert results[1].error  # message captured, batch not aborted


# ---------------------------------------------------------------------------
# make_zip
# ---------------------------------------------------------------------------

class TestZip:
    def test_make_zip(self, tmp_path):
        srcs = [_wav(tmp_path, name=f"z{i}.wav") for i in range(2)]
        outs = [r.output for r in converter.convert_batch(srcs, "wav", out_dir=str(tmp_path / "out"))]
        zip_path = converter.make_zip(outs, zip_path=str(tmp_path / "bundle.zip"))
        assert os.path.exists(zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            assert len(zf.namelist()) == 2


# ---------------------------------------------------------------------------
# Gradio handler (single vs batch output)
# ---------------------------------------------------------------------------

class TestRunConversion:
    def test_empty_returns_nothing(self):
        rows, out = converter._run_conversion([], "wav", "Keep original", "Keep")
        assert rows == []
        assert out is None

    def test_single_file_returns_file(self, tmp_path):
        src = _wav(tmp_path)
        rows, out = converter._run_conversion([src], "wav", "Keep original", "Keep")
        assert len(rows) == 1
        assert rows[0][2] == "✓ done"
        assert out is not None and not out.endswith(".zip")

    def test_multiple_files_return_zip(self, tmp_path):
        srcs = [_wav(tmp_path, name=f"m{i}.wav") for i in range(2)]
        rows, out = converter._run_conversion(srcs, "wav", "Keep original", "Keep")
        assert len(rows) == 2
        assert out.endswith(".zip")


# ---------------------------------------------------------------------------
# CLI gui subcommand
# ---------------------------------------------------------------------------

class TestCLIGui:
    def test_gui_parser(self):
        from aiaudio.cli.main import build_parser
        args = build_parser().parse_args(["gui", "--port", "8080", "--share"])
        assert args.command == "gui"
        assert args.port == 8080
        assert args.share is True

    def test_gui_parser_defaults(self):
        from aiaudio.cli.main import build_parser
        args = build_parser().parse_args(["gui"])
        assert args.port is None
        assert args.share is False
