import numpy as np
import pytest
from unittest.mock import patch

from aiaudio.core.audio import Audio as _Audio
from aiaudio.cli.main import build_parser, cmd_info, cmd_slice, cmd_volume, cmd_concat


def _make_audio(duration: float = 1.0, sample_rate: int = 44100) -> _Audio:
    n = int(duration * sample_rate)
    t = np.linspace(0, duration, n, endpoint=False)
    samples = (np.sin(2 * np.pi, 440 * t) * 0.5).astype(np.float32)
    return _Audio(samples, sample_rate)


def _save(audio: _Audio, path: str) -> str:
    audio.export(path)
    return path


class TestParser:
    def test_info_command(self):
        parser = build_parser()
        args = parser.parse_args(["info", "song.wav"])
        assert args.command == "info"
        assert args.file == "song.wav"

    def test_slice_command(self):
        parser = build_parser()
        args = parser.parse_args(["slice", "song.wav", "10", "20", "-o", "out.wav"])
        assert args.command == "slice"
        assert args.start == 10.0
        assert args.end == 20.0
        assert args.output == "out.wav"

    def test_volume_positive(self):
        parser = build_parser()
        args = parser.parse_args(["volume", "song.wav", "5", "-o", "out.wav"])
        assert args.db == 5.0

    def test_volume_negative(self):
        parser = build_parser()
        args = parser.parse_args(["volume", "song.wav", "-3", "-o", "out.wav"])
        assert args.db == -3.0

    def test_concat_multiple_files(self):
        parser = build_parser()
        args = parser.parse_args(["concat", "a.wav", "b.wav", "c.wav", "-o", "out.wav"])
        assert args.files == ["a.wav", "b.wav", "c.wav"]


class TestCLICommands:
    def test_info_output(self, tmp_path, capsys):
        a = _make_audio(duration=2.0)
        wav = str(tmp_path / "a.wav")
        a.export(wav)

        parser = build_parser()
        args = parser.parse_args(["info", wav])
        cmd_info(args)

        captured = capsys.readouterr().out
        assert "Duration" in captured
        assert "44100" in captured

    def test_slice_creates_file(self, tmp_path):
        a = _make_audio(duration=5.0)
        inp = str(tmp_path / "in.wav")
        out = str(tmp_path / "out.wav")
        a.export(inp)

        parser = build_parser()
        args = parser.parse_args(["slice", inp, "1", "3", "-o", out])
        cmd_slice(args)

        from aiaudio import Audio
        result = Audio.load(out)
        assert abs(result.duration - 2.0) < 0.02

    def test_volume_creates_file(self, tmp_path):
        a = _make_audio()
        inp = str(tmp_path / "in.wav")
        out = str(tmp_path / "out.wav")
        a.export(inp)

        parser = build_parser()
        args = parser.parse_args(["volume", inp, "3", "-o", out])
        cmd_volume(args)

        import os
        assert os.path.exists(out)

    def test_concat_creates_file(self, tmp_path):
        a = _make_audio(duration=1.0)
        b = _make_audio(duration=1.0)
        p1 = str(tmp_path / "a.wav")
        p2 = str(tmp_path / "b.wav")
        out = str(tmp_path / "out.wav")
        a.export(p1)
        b.export(p2)

        parser = build_parser()
        args = parser.parse_args(["concat", p1, p2, "-o", out])
        cmd_concat(args)

        from aiaudio import Audio
        result = Audio.load(out)
        assert abs(result.duration - 2.0) < 0.02
