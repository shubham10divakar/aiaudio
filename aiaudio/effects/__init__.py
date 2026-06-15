"""Phase 3 — audio effects.

Pure-function effects operating on float32 sample arrays. The user-facing API is
on :class:`aiaudio.Audio` (``audio.fade_in(...)`` etc.); these modules hold the
underlying DSP so ``audio.py`` stays lean.
"""
from . import fade, normalize, silence, timestretch

__all__ = ["fade", "normalize", "silence", "timestretch"]
