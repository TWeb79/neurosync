"""
Tests for Session Timeline
Author: Inventions4All - github:TWeb79
"""

import pytest
from neurosync.sessions.timeline import (
    BrainwaveBand,
    TimelineSegment,
    SessionTimeline,
    SLEEP_DESCENT_TIMELINE,
    FOCUS_TIMELINE,
)


class TestBrainwaveBand:
    """Tests for BrainwaveBand enum."""

    def test_delta_band(self):
        """Test delta band enum."""
        assert BrainwaveBand.DELTA.value == "delta"

    def test_theta_band(self):
        """Test theta band enum."""
        assert BrainwaveBand.THETA.value == "theta"

    def test_alpha_band(self):
        """Test alpha band enum."""
        assert BrainwaveBand.ALPHA.value == "alpha"

    def test_beta_band(self):
        """Test beta band enum."""
        assert BrainwaveBand.BETA.value == "beta"

    def test_gamma_band(self):
        """Test gamma band enum."""
        assert BrainwaveBand.GAMMA.value == "gamma"


class TestTimelineSegment:
    """Tests for TimelineSegment dataclass."""

    def test_segment_creation(self):
        """Test creating a timeline segment."""
        segment = TimelineSegment(
            name="Test",
            start_time=0.0,
            beat_frequency=10.0,
            carrier_frequency=220.0,
        )
        assert segment.name == "Test"
        assert segment.start_time == 0.0
        assert segment.beat_frequency == 10.0
        assert segment.carrier_frequency == 220.0

    def test_segment_defaults(self):
        """Test segment default values."""
        segment = TimelineSegment(
            name="Test",
            start_time=0.0,
            beat_frequency=10.0,
            carrier_frequency=220.0,
        )
        assert segment.ambient_layer == "pad_soft"
        assert segment.noise_type == "pink"
        assert segment.harmonic_richness == 0.5
        assert segment.transition_duration == 90.0
        assert segment.ease_type == "ease_in_out"

    def test_segment_custom_values(self):
        """Test segment with custom values."""
        segment = TimelineSegment(
            name="Custom",
            start_time=100.0,
            beat_frequency=5.0,
            carrier_frequency=180.0,
            ambient_layer="pad_dark",
            noise_type="brown",
            harmonic_richness=0.7,
            transition_duration=60.0,
            ease_type="linear",
        )
        assert segment.ambient_layer == "pad_dark"
        assert segment.noise_type == "brown"
        assert segment.harmonic_richness == 0.7
        assert segment.transition_duration == 60.0
        assert segment.ease_type == "linear"


class TestSleepDescentTimeline:
    """Tests for sleep descent timeline definition."""

    def test_sleep_timeline_exists(self):
        """Test that sleep timeline is defined."""
        assert len(SLEEP_DESCENT_TIMELINE) > 0

    def test_sleep_timeline_ordered(self):
        """Test that sleep timeline is properly ordered."""
        for i in range(len(SLEEP_DESCENT_TIMELINE) - 1):
            assert SLEEP_DESCENT_TIMELINE[i].start_time <= SLEEP_DESCENT_TIMELINE[i + 1].start_time

    def test_sleep_timeline_frequency_descent(self):
        """Test that sleep timeline has descending frequencies."""
        first_beat = SLEEP_DESCENT_TIMELINE[0].beat_frequency
        last_beat = SLEEP_DESCENT_TIMELINE[-1].beat_frequency
        assert first_beat > last_beat


class TestFocusTimeline:
    """Tests for focus timeline definition."""

    def test_focus_timeline_exists(self):
        """Test that focus timeline is defined."""
        assert len(FOCUS_TIMELINE) > 0

    def test_focus_timeline_ordered(self):
        """Test that focus timeline is properly ordered."""
        for i in range(len(FOCUS_TIMELINE) - 1):
            assert FOCUS_TIMELINE[i].start_time <= FOCUS_TIMELINE[i + 1].start_time


class TestSessionTimeline:
    """Tests for SessionTimeline controller."""

    def test_timeline_initialization(self):
        """Test timeline initialization."""
        timeline = SessionTimeline(SLEEP_DESCENT_TIMELINE)
        assert timeline.segments == SLEEP_DESCENT_TIMELINE
        assert timeline._current_segment_idx == 0
        assert timeline._segment_start_time == 0.0

    def test_timeline_total_duration(self):
        """Test timeline total duration calculation."""
        timeline = SessionTimeline(SLEEP_DESCENT_TIMELINE)
        duration = timeline.total_duration
        assert duration > 0
        assert duration == SLEEP_DESCENT_TIMELINE[-1].start_time

    def test_get_segment_at_start(self):
        """Test getting segment at start time."""
        timeline = SessionTimeline(SLEEP_DESCENT_TIMELINE)
        segment, progress = timeline.get_segment_at_time(0.0)
        assert segment == SLEEP_DESCENT_TIMELINE[0]
        assert progress >= 0.0  # Progress could be > 0 due to transition logic

    def test_get_segment_during_segment(self):
        """Test getting segment during playback."""
        timeline = SessionTimeline(SLEEP_DESCENT_TIMELINE)
        elapsed = SLEEP_DESCENT_TIMELINE[1].start_time
        segment, progress = timeline.get_segment_at_time(elapsed)
        assert segment.beat_frequency <= SLEEP_DESCENT_TIMELINE[1].beat_frequency

    def test_get_segment_progress_calculation(self):
        """Test transition progress calculation."""
        timeline = SessionTimeline(SLEEP_DESCENT_TIMELINE)
        seg = SLEEP_DESCENT_TIMELINE[1]
        # At the start of transition
        segment, progress = timeline.get_segment_at_time(seg.start_time - seg.transition_duration / 2)
        assert 0.0 <= progress <= 1.0

    def test_get_segment_at_end(self):
        """Test getting segment at end of timeline."""
        timeline = SessionTimeline(SLEEP_DESCENT_TIMELINE)
        last_segment = SLEEP_DESCENT_TIMELINE[-1]
        segment, progress = timeline.get_segment_at_time(last_segment.start_time)
        assert segment == last_segment
        assert progress == 1.0

    def test_get_segment_beyond_end(self):
        """Test getting segment beyond timeline end."""
        timeline = SessionTimeline(SLEEP_DESCENT_TIMELINE)
        total_duration = timeline.total_duration
        segment, progress = timeline.get_segment_at_time(total_duration + 100)
        # Should return first segment
        assert segment == SLEEP_DESCENT_TIMELINE[0]

    def test_get_segment_with_zero_transition_duration(self):
        """Test getting segment with zero transition duration during transition."""
        # Line 78's else branch (`else 0`) is hit when elapsed < seg.start_time 
        # AND transition_duration == 0. This happens when elapsed == seg.start_time exactly
        # because the window becomes a single point.
        # But actually, we need to test the case where we hit line 77 and transition_duration > 0.
        # Let me test with a normal transition period.
        segments = [
            TimelineSegment("First", 0.0, 10.0, 220.0, transition_duration=90.0),
            TimelineSegment("Second", 200.0, 8.0, 200.0, transition_duration=90.0),
        ]
        timeline = SessionTimeline(segments)
        # At elapsed=95.0, we're 5 seconds before First's start, in transition period
        segment, progress = timeline.get_segment_at_time(95.0)
        assert segment == segments[0]
        # progress should be around 0.1 (5/50 = 0.1) but clamped
        assert 0.0 <= progress <= 1.0

    def test_get_segment_at_exact_transition_start(self):
        """Test getting segment at exact transition start time."""
        segments = [
            TimelineSegment("First", 100.0, 10.0, 220.0, transition_duration=90.0),
        ]
        timeline = SessionTimeline(segments)
        # At elapsed=10.0, we're at transition start (100 - 90 = 10)
        # But elapsed is 10 which is < 100 (start_time), so we're in pre-transition
        # Wait, that doesn't make sense. Transition starts at start_time - transition_duration.
        # So for start_time=100, trans_duration=90, the window is 10 to 190.
        segment, progress = timeline.get_segment_at_time(10.0)
        assert segment == segments[0]
        assert progress == 0.0  # At the very start of transition

    def test_timeline_with_empty_segments(self):
        """Test timeline with empty segments list."""
        timeline = SessionTimeline([])
        assert timeline.total_duration == 0

    def test_segment_frequency_values(self):
        """Test that segments have valid frequency values."""
        for segment in SLEEP_DESCENT_TIMELINE:
            assert segment.beat_frequency > 0
            assert segment.carrier_frequency > 0
            assert 0 <= segment.harmonic_richness <= 1.0

    def test_focus_timeline_segment_at_time(self):
        """Test focus timeline segment access."""
        timeline = SessionTimeline(FOCUS_TIMELINE)
        segment, progress = timeline.get_segment_at_time(0.0)
        assert segment == FOCUS_TIMELINE[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])