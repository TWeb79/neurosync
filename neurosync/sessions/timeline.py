"""
Session Timeline - Automated frequency transitions
Author: Inventions4All - github:TWeb79
"""

from dataclasses import dataclass
from enum import Enum


class BrainwaveBand(Enum):
    DELTA = "delta"
    THETA = "theta"
    ALPHA = "alpha"
    BETA = "beta"
    GAMMA = "gamma"


@dataclass
class TimelineSegment:
    """A single segment in a session timeline."""

    name: str
    start_time: float
    beat_frequency: float
    carrier_frequency: float
    ambient_layer: str = "pad_soft"
    noise_type: str = "pink"
    harmonic_richness: float = 0.5
    transition_duration: float = 90.0
    ease_type: str = "ease_in_out"


SLEEP_DESCENT_TIMELINE: list[TimelineSegment] = [
    TimelineSegment("Wake (Beta)", 0.0, 16.0, 240.0, "pad_soft", "brown", 0.3, 90.0, "ease_out"),
    TimelineSegment("Transition", 150.0, 10.0, 220.0, "pad_soft", "brown", 0.35, 90.0, "ease_in_out"),
    TimelineSegment("Alpha", 240.0, 8.0, 200.0, "pad_soft", "brown", 0.4, 90.0, "ease_in_out"),
    TimelineSegment("Low Alpha", 480.0, 7.0, 190.0, "pad_soft", "brown", 0.4, 90.0, "ease_out"),
    TimelineSegment("Theta Entry", 720.0, 5.0, 180.0, "pad_soft", "pink", 0.6, 90.0, "ease_in_out"),
    TimelineSegment("Deep Theta", 1080.0, 4.0, 165.0, "pad_soft", "pink", 0.7, 90.0, "ease_in_out"),
    TimelineSegment("Delta Entry", 1680.0, 2.5, 150.0, "pad_dark", "pink", 0.8, 90.0, "exponential"),
    TimelineSegment("Deep Delta", 2280.0, 1.5, 140.0, "pad_dark", "pink", 0.9, 90.0, "linear"),
]


FOCUS_TIMELINE: list[TimelineSegment] = [
    TimelineSegment("Work", 0.0, 14.0, 220.0, "pad_soft", "brown", 0.4, 0.0, "linear"),
    TimelineSegment("Micro-reset", 240.0, 12.0, 220.0, "pad_soft", "off", 0.2, 30.0, "ease_in_out"),
    TimelineSegment("Resume", 270.0, 14.0, 220.0, "pad_soft", "brown", 0.4, 30.0, "ease_in_out"),
]


class SessionTimeline:
    """Manages timeline playback and segment transitions."""

    def __init__(self, segments: list[TimelineSegment]):
        self.segments = segments
        self._current_segment_idx = 0
        self._segment_start_time = 0.0
        self._total_duration = segments[-1].start_time if segments else 0

    def get_segment_at_time(self, elapsed: float) -> tuple[TimelineSegment, float]:
        """Get the current segment and transition progress.

        Args:
            elapsed: Elapsed time in seconds

        Returns:
            Tuple of (segment, transition_progress 0-1)
        """
        for i, seg in enumerate(self.segments):
            if i + 1 < len(self.segments):
                next_time = self.segments[i + 1].start_time - seg.transition_duration
            else:
                next_time = self._total_duration
            if seg.start_time <= elapsed < next_time + seg.transition_duration:
                trans_start = seg.start_time - seg.transition_duration
                if elapsed < seg.start_time:
                    progress = (elapsed - trans_start) / seg.transition_duration if seg.transition_duration > 0 else 0
                else:
                    progress = 1.0
                return seg, min(1.0, max(0.0, progress))
        return self.segments[0], 0.0

    @property
    def total_duration(self) -> float:
        return self._total_duration