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


def cmd_fade(args: argparse.Namespace) -> None:
    audio = Audio.load(args.file)
    if args.in_ms:
        audio = audio.fade_in(args.in_ms)
    if args.out_ms:
        audio = audio.fade_out(args.out_ms)
    audio.export(args.output)
    print(f"Saved: {args.output}")


def cmd_normalize(args: argparse.Namespace) -> None:
    audio = Audio.load(args.file).normalize(args.headroom)
    audio.export(args.output)
    print(f"Saved: {args.output}")


def cmd_reverse(args: argparse.Namespace) -> None:
    audio = Audio.load(args.file).reverse()
    audio.export(args.output)
    print(f"Saved: {args.output}")


def cmd_speed(args: argparse.Namespace) -> None:
    audio = Audio.load(args.file).speed(args.factor)
    audio.export(args.output)
    print(f"Saved: {args.output}")


def cmd_silence(args: argparse.Namespace) -> None:
    audio = Audio.load(args.file).remove_silence(args.threshold, args.min_silence)
    audio.export(args.output)
    print(f"Saved: {args.output}")


def cmd_gui(args: argparse.Namespace) -> None:
    try:
        from aiaudio.gui.converter import launch
    except ImportError:
        print(
            "Error: Gradio is not installed. Install the GUI extra:\n"
            "  pip install aiaudio[gui]",
            file=sys.stderr,
        )
        sys.exit(1)
    launch(server_port=args.port, share=args.share)


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

    # fade
    p = sub.add_parser("fade", help="Apply fade in and/or fade out")
    p.add_argument("file", help="Input audio file")
    p.add_argument("--in", dest="in_ms", type=float, default=0, metavar="MS",
                   help="Fade-in duration in milliseconds")
    p.add_argument("--out", dest="out_ms", type=float, default=0, metavar="MS",
                   help="Fade-out duration in milliseconds")
    p.add_argument("-o", "--output", required=True, help="Output file path")

    # normalize
    p = sub.add_parser("normalize", help="Peak-normalize the audio")
    p.add_argument("file", help="Input audio file")
    p.add_argument("--headroom", type=float, default=0.0, metavar="DB",
                   help="Headroom below full scale in dB (default: 0)")
    p.add_argument("-o", "--output", required=True, help="Output file path")

    # reverse
    p = sub.add_parser("reverse", help="Reverse the audio in time")
    p.add_argument("file", help="Input audio file")
    p.add_argument("-o", "--output", required=True, help="Output file path")

    # speed
    p = sub.add_parser("speed", help="Change tempo (pitch preserved); 1.5 = 1.5x faster")
    p.add_argument("file", help="Input audio file")
    p.add_argument("factor", type=float, help="Speed factor (>1 faster, <1 slower)")
    p.add_argument("-o", "--output", required=True, help="Output file path")

    # silence
    p = sub.add_parser("silence", help="Remove silent gaps")
    p.add_argument("file", help="Input audio file")
    p.add_argument("--threshold", type=float, default=-40.0, metavar="DB",
                   help="Silence threshold in dBFS (default: -40)")
    p.add_argument("--min-silence", dest="min_silence", type=float, default=100.0, metavar="MS",
                   help="Minimum silence to remove, in ms (default: 100)")
    p.add_argument("-o", "--output", required=True, help="Output file path")

    # gui (requires gradio)
    p = sub.add_parser("gui", help="Launch the browser-based format converter (requires gradio)")
    p.add_argument("--port", type=int, default=None, metavar="PORT",
                   help="Port to serve on (default: Gradio's choice)")
    p.add_argument("--share", action="store_true",
                   help="Create a public shareable link")

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
        "fade": cmd_fade,
        "normalize": cmd_normalize,
        "reverse": cmd_reverse,
        "speed": cmd_speed,
        "silence": cmd_silence,
        "gui": cmd_gui,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
