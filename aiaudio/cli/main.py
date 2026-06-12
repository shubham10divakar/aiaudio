import argparse
import sys

from aiaudio import Audio
from aiaudio.core.ffmpeg import is_available as _ffmpeg_available


def cmd_info(args: argparse.Namespace) -> None:
    audio = Audio.load(args.file)
    print(f"File:        {args.file}")
    print(f"Duration:    {audio.duration:.2f}s")
    print(f"Sample rate: {audio.sample_rate} Hz")
    print(f"Channels:    {audio.channels}")


def cmd_slice(args: argparse.Namespace) -> None:
    audio = Audio.load(args.file)
    result = audio.slice(args.start, args.end)
    result.export(args.output)
    print(f"Saved: {args.output}")


def cmd_volume(args: argparse.Namespace) -> None:
    audio = Audio.load(args.file)
    if args.db >= 0:
        result = audio.increase_volume(args.db)
    else:
        result = audio.decrease_volume(-args.db)
    result.export(args.output)
    print(f"Saved: {args.output}")


def cmd_convert(args: argparse.Namespace) -> None:
    if not _ffmpeg_available():
        print(
            "Error: FFmpeg is not installed. Install it to convert between formats.\n"
            "  Windows: winget install ffmpeg\n"
            "  macOS:   brew install ffmpeg\n"
            "  Linux:   sudo apt install ffmpeg",
            file=sys.stderr,
        )
        sys.exit(1)
    audio = Audio.load(args.file)
    if args.sample_rate:
        audio = audio.resample(args.sample_rate)
    if args.channels:
        audio = audio.set_channels(args.channels)
    audio.export(args.output)
    print(f"Saved: {args.output}")


def cmd_concat(args: argparse.Namespace) -> None:
    audios = [Audio.load(f) for f in args.files]
    result = audios[0]
    for a in audios[1:]:
        result = result + a
    result.export(args.output)
    print(f"Saved: {args.output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aiaudio",
        description="AIAudio — Audio Processing Meets Audio Intelligence.",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # info
    p = sub.add_parser("info", help="Show audio file info")
    p.add_argument("file", help="Path to audio file")

    # slice
    p = sub.add_parser("slice", help="Extract a segment of audio")
    p.add_argument("file", help="Input audio file")
    p.add_argument("start", type=float, help="Start time in seconds")
    p.add_argument("end", type=float, help="End time in seconds")
    p.add_argument("-o", "--output", required=True, help="Output file path")

    # volume
    p = sub.add_parser("volume", help="Adjust volume (+dB louder, -dB quieter)")
    p.add_argument("file", help="Input audio file")
    p.add_argument("db", type=float, help="dB adjustment (e.g. 5 or -3)")
    p.add_argument("-o", "--output", required=True, help="Output file path")

    # concat
    p = sub.add_parser("concat", help="Concatenate audio files in order")
    p.add_argument("files", nargs="+", help="Input audio files")
    p.add_argument("-o", "--output", required=True, help="Output file path")

    # convert (requires FFmpeg)
    p = sub.add_parser("convert", help="Convert audio to a different format (requires FFmpeg)")
    p.add_argument("file", help="Input audio file")
    p.add_argument("-o", "--output", required=True, help="Output file path (extension sets format)")
    p.add_argument("--sample-rate", type=int, default=None, metavar="HZ",
                   help="Resample to this rate (e.g. 44100)")
    p.add_argument("--channels", type=int, choices=[1, 2], default=None,
                   help="Set channel count: 1 (mono) or 2 (stereo)")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "info": cmd_info,
        "slice": cmd_slice,
        "volume": cmd_volume,
        "concat": cmd_concat,
        "convert": cmd_convert,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
