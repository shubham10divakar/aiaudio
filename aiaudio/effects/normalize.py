"""Peak normalization."""
from __future__ import annotations

import numpy as np


def normalize(samples: np.ndarray, headroom_db: float = 0.0) -> np.ndarray:
    """Scale so the loudest sample peaks at ``-headroom_db`` dBFS.

    ``headroom_db=0`` peaks at full scale (1.0); ``headroom_db=3`` leaves 3 dB
    of headroom. Silent input (all zeros) is returned unchanged.
    """
    peak = float(np.max(np.abs(samples))) if samples.size else 0.0
    if peak == 0.0:
        return samples.copy()
    target = 10 ** (-abs(headroom_db) / 20)  # 0 dB -> 1.0
    factor = target / peak
    return np.clip(samples * factor, -1.0, 1.0).astype(np.float32)
