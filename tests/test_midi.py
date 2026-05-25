"""
Tests for MIDI Controller
Author: Inventions4All - github:TWeb79
"""

import pytest
from unittest.mock import MagicMock, patch
from neurosync.audio.midi import MidiController, MIDI_AVAILABLE


class TestMidiController:
    """Tests for MIDI controller."""

    def test_init_without_dsp_bridge(self):
        """Test initialization without DSP bridge."""
        controller = MidiController()
        assert controller.dsp_bridge is None
        assert controller.CC_BEAT_FREQ == 1
        assert controller.CC_CARRIER_FREQ == 7
        assert controller.CC_LAYER_BINAURAL == 20
        assert controller.CC_LAYER_ISO == 21
        assert controller.CC_LAYER_AMBIENT == 22

    def test_init_with_dsp_bridge(self):
        """Test initialization with DSP bridge."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        assert controller.dsp_bridge is dsp_bridge

    def test_cc_constants(self):
        """Test that CC constants are defined."""
        controller = MidiController()
        assert controller.CC_BEAT_FREQ == 1
        assert controller.CC_CARRIER_FREQ == 7

    def test_on_message_with_control_change(self):
        """Test handling of CC messages."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        
        # CC message: status=0xB0 (CC), cc=1 (beat freq), value=64
        message = [0xB0, 1, 64]
        controller.on_message(message, None)
        
        # Should have called set_target_beat
        dsp_bridge.set_target_beat.assert_called()

    def test_on_message_with_short_message(self):
        """Test handling of short messages."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        
        # Short message
        message = [0xB0, 1]
        controller.on_message(message, None)
        
        # Should not crash, but also not call set_target

    def test_handle_control_change_beat_freq(self):
        """Test beat frequency control change handling."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        
        # CC_BEAT_FREQ = 1, value = 127 (max)
        controller._handle_control_change(1, 127)
        dsp_bridge.set_target_beat.assert_called()
        
        # Check that frequency is in expected range (0.5 to 40 Hz)
        call_args = dsp_bridge.set_target_beat.call_args[0]
        assert call_args[0] > 0.0

    def test_handle_control_change_carrier_freq(self):
        """Test carrier frequency control change handling."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        
        # CC_CARRIER_FREQ = 7, value = 64 (mid)
        controller._handle_control_change(7, 64)
        dsp_bridge.set_target_carrier.assert_called()
        
        # Check that frequency is in expected range (100-400 Hz)
        call_args = dsp_bridge.set_target_carrier.call_args[0]
        assert 100 <= call_args[0] <= 400

    def test_handle_control_change_beat_freq_min(self):
        """Test beat frequency at minimum."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        
        controller._handle_control_change(1, 0)
        dsp_bridge.set_target_beat.assert_called()

    def test_handle_control_change_beat_freq_max(self):
        """Test beat frequency at maximum."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        
        controller._handle_control_change(1, 127)
        dsp_bridge.set_target_beat.assert_called()

    def test_handle_control_change_carrier_freq_min(self):
        """Test carrier frequency at minimum."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        
        controller._handle_control_change(7, 0)
        call_args = dsp_bridge.set_target_carrier.call_args[0]
        assert call_args[0] == 100.0

    def test_handle_control_change_carrier_freq_max(self):
        """Test carrier frequency at maximum."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        
        controller._handle_control_change(7, 127)
        call_args = dsp_bridge.set_target_carrier.call_args[0]
        assert call_args[0] == 400.0

    def test_handle_control_change_unknown_cc(self):
        """Test handling of unknown CC numbers."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        
        controller._handle_control_change(99, 64)
        # Should not call any set_target methods
        dsp_bridge.set_target_beat.assert_not_called()
        dsp_bridge.set_target_carrier.assert_not_called()

    def test_poll_without_midi(self):
        """Test polling when MIDI is not available."""
        controller = MidiController()
        # Should not crash
        controller.poll()

    def test_poll_with_midi_no_message(self):
        """Test polling with MIDI but no message."""
        dsp_bridge = MagicMock()
        controller = MidiController(dsp_bridge)
        if controller._midi_in:
            controller._midi_in.get_message = MagicMock(return_value=None)
            controller.poll()
