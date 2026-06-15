"""Phase 2.5 — Audio Format Converter GUI.

The conversion logic here is pure Python and has no GUI dependency, so it can be
tested without Gradio installed and reused by the CLI/library. ``build_app`` and
``launch`` add the thin Gradio layer on top (Gradio is imported lazily so that
``import aiaudio.gui.converter`` works even when Gradio is absent).

Every conversion delegates to ``aiaudio.Audio`` — the GUI never touches samples
directly, keeping one code path across library, CLI, and GUI.
"""
from __future__ import annotations

import os
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from aiaudio import Audio

# Formats offered in the GUI dropdown. WAV needs no FFmpeg; the rest do.
SUPPORTED_FORMATS = ["wav", "mp3", "flac", "ogg", "aac", "m4a"]
SAMPLE_RATE_CHOICES = ["Keep original", "16000", "22050", "44100", "48000"]
CHANNEL_CHOICES = ["Keep", "Mono", "Stereo"]


@dataclass
class ConversionResult:
    """Outcome of converting a single file. ``error`` is None on success."""

    source: str
    output: Optional[str]
    error: Optional[str]

    @property
    def ok(self) -> bool:
        return self.error is None


# ---------------------------------------------------------------------------
# Dropdown label parsing
# ---------------------------------------------------------------------------

def parse_sample_rate(label: Optional[str]) -> Optional[int]:
    """Map a sample-rate dropdown label to an int, or None to keep original."""
    if not label or label == "Keep original":
        return None
    return int(label)


def parse_channels(label: Optional[str]) -> Optional[int]:
    """Map a channels dropdown label to 1/2, or None to keep original."""
    if not label or label == "Keep":
        return None
    return 1 if label == "Mono" else 2


def _input_path(file_obj) -> str:
    """Normalise a Gradio file value (str path or object with ``.name``)."""
    return file_obj if isinstance(file_obj, str) else file_obj.name


# ---------------------------------------------------------------------------
# Pure conversion core (no Gradio)
# ---------------------------------------------------------------------------

def convert_one(
    source: str,
    target_format: str,
    sample_rate: Optional[int] = None,
    channels: Optional[int] = None,
    out_dir: Optional[str] = None,
) -> str:
    """Convert a single file and return the output path.

    Raises on failure (bad file, missing FFmpeg, etc.) — callers that batch
    should catch per file so one bad input doesn't abort the rest.
    """
    target_format = target_format.lower().lstrip(".")
    if target_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported target format: {target_format!r}")

    audio = Audio.load(source)
    if sample_rate is not None:
        audio = audio.resample(sample_rate)
    if channels is not None:
        audio = audio.set_channels(channels)

    out_dir = out_dir or tempfile.mkdtemp(prefix="aiaudio_")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{Path(source).stem}.{target_format}")
    audio.export(out_path)
    return out_path


def convert_batch(
    sources,
    target_format: str,
    sample_rate: Optional[int] = None,
    channels: Optional[int] = None,
    out_dir: Optional[str] = None,
) -> list[ConversionResult]:
    """Convert many files, isolating failures per file.

    Returns one :class:`ConversionResult` per input, in order.
    """
    # All files in one batch share an output dir so we can zip them together.
    out_dir = out_dir or tempfile.mkdtemp(prefix="aiaudio_")
    results: list[ConversionResult] = []
    for src in sources:
        path = _input_path(src)
        try:
            output = convert_one(path, target_format, sample_rate, channels, out_dir)
            results.append(ConversionResult(source=path, output=output, error=None))
        except Exception as exc:  # noqa: BLE001 — surface any failure per file
            results.append(ConversionResult(source=path, output=None, error=str(exc)))
    return results


def make_zip(paths, zip_path: Optional[str] = None) -> str:
    """Bundle output files into a single ZIP and return its path."""
    if zip_path is None:
        zip_path = os.path.join(tempfile.mkdtemp(prefix="aiaudio_"), "converted.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))
    return zip_path


# ---------------------------------------------------------------------------
# Gradio layer (lazy import)
# ---------------------------------------------------------------------------

def _run_conversion(files, target_format, sample_rate_label, channels_label):
    """Gradio click handler: convert uploads and build a status table + download."""
    if not files:
        return [], None

    sample_rate = parse_sample_rate(sample_rate_label)
    channels = parse_channels(channels_label)
    results = convert_batch(files, target_format, sample_rate, channels)

    status_rows = [
        [
            os.path.basename(r.source),
            target_format,
            "✓ done" if r.ok else f"✗ {r.error}",
        ]
        for r in results
    ]

    outputs = [r.output for r in results if r.ok]
    if not outputs:
        return status_rows, None
    if len(outputs) == 1:
        return status_rows, outputs[0]
    return status_rows, make_zip(outputs)


def build_app():
    """Build and return the Gradio Blocks app (without launching it)."""
    try:
        import gradio as gr
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise ImportError(
            "Gradio is required for the GUI. Install it with:\n"
            "    pip install aiaudio[gui]"
        ) from exc

    with gr.Blocks(title="AIAudio — Format Converter") as app:
        gr.Markdown(
            "# AIAudio — Format Converter\n"
            "Drag in one or more audio files, pick a target format, and convert. "
            "Batches download as a single ZIP."
        )
        files = gr.File(
            file_count="multiple",
            label="Drop audio files here (or click to browse)",
        )
        with gr.Row():
            target = gr.Dropdown(SUPPORTED_FORMATS, value="mp3", label="Convert to")
            sample_rate = gr.Dropdown(
                SAMPLE_RATE_CHOICES, value="Keep original", label="Sample rate"
            )
            channels = gr.Dropdown(CHANNEL_CHOICES, value="Keep", label="Channels")
        convert_btn = gr.Button("Convert all", variant="primary")
        status = gr.Dataframe(
            headers=["File", "Target", "Status"],
            label="Queue",
            interactive=False,
            wrap=True,
        )
        result = gr.File(label="Download result")

        convert_btn.click(
            _run_conversion,
            inputs=[files, target, sample_rate, channels],
            outputs=[status, result],
        )

    return app


def launch(**kwargs):
    """Build and launch the converter in the browser."""
    return build_app().launch(**kwargs)
