"""
telemetry.py — shared live stats for the HUD.

Why this module exists:
    camera.py knows the frame rate, detector.py knows the object
    count, and app.py needs both. Rather than having those files
    import each other (circular-import risk), they all write into
    this one small module, and /telemetry reads from it.

Wiring (one line each):
    camera.py    → call telemetry.record_frame() once per captured frame
    detector.py  → call telemetry.set_objects(n) after NMS each frame
"""

import time
import threading
from collections import deque

_lock = threading.Lock()

# Timestamps of the most recent frames — enough to compute a smooth FPS
_frame_times = deque(maxlen=30)

_object_count = 0


def record_frame():
    """Call once per captured frame (from camera.py)."""
    with _lock:
        _frame_times.append(time.monotonic())


def set_objects(n: int):
    """Call after each detection pass (from ai/detector.py)."""
    global _object_count
    with _lock:
        _object_count = int(n)


def get_fps() -> float:
    """FPS averaged over the last ~30 frames. 0.0 if the feed is idle."""
    with _lock:
        if len(_frame_times) < 2:
            return 0.0
        newest = _frame_times[-1]
        oldest = _frame_times[0]

    # If no frame arrived recently, the stream is stalled — report 0
    if time.monotonic() - newest > 2.0:
        return 0.0

    span = newest - oldest
    if span <= 0:
        return 0.0
    return (len(_frame_times) - 1) / span


def get_objects() -> int:
    with _lock:
        return _object_count
