"""
Audio MIDI Controller
Author: Inventions4All - github:TWeb79
"""

from typing import Any, Optional

try:
    import rtmidi
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False


class MidiController:
    """Maps MIDI CC to DSP parameters."""

    CC_BEAT_FREQ = 1
    CC_CARRIER_FREQ = 7
    CC_LAYER_BINAURAL = 20
    CC_LAYER_ISO = 21
    CC_LAYER_AMBIENT = 22

    def __init__(self, dsp_bridge: Optional[Any] = None) -> None:
        """Initialize MIDI controller.
        
        Args:
            dsp_bridge: Optional DSP bridge for controlling parameters.
        """
        self.dsp_bridge = dsp_bridge
        self._midi_in: Optional[Any] = None
        if MIDI_AVAILABLE:
            self._midi_in = rtmidi.MidiIn()
            ports = self._midi_in.get_ports()
            if ports:
                self._midi_in.open_port(0)

    def on_message(self, message, data):
        """Handle incoming MIDI message."""
        if len(message) >= 3:
            status, cc, value = message[0], message[1], message[2]
            if status == 0xB0 and self.dsp_bridge:
                self._handle_control_change(cc, value)

    def _handle_control_change(self, cc: int, value: int):
        """Process MIDI CC message."""
        normalized = value / 127.0
        if cc == self.CC_BEAT_FREQ:
            hz = 0.5 * (40 / 0.5) ** normalized
            if self.dsp_bridge:
                self.dsp_bridge.set_target_beat(hz)
        elif cc == self.CC_CARRIER_FREQ:
            hz = 100 + normalized * 300
            if self.dsp_bridge:
                self.dsp_bridge.set_target_carrier(hz)

    def poll(self):
        """Poll for MIDI messages if available."""
        if not MIDI_AVAILABLE or not self._midi_in:
            return
        message = self._midi_in.get_message()
        if message:
            self.on_message(message[0], None)