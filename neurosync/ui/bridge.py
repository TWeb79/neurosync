"""
UI Bridge - PySide6 QObject for QML-Python communication
Author: Inventions4All - github:TWeb79
"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from neurosync.sessions.controller import PRESETS
from neurosync.dsp.core import BinauralGenerator


class UIBridge(QObject):
    """Exposes DSP state to QML via Qt Property/Signal system."""

    carrierFreqChanged = Signal(float)
    beatFreqChanged = Signal(float)
    amplitudeChanged = Signal(float)
    bandChanged = Signal(str)
    presetChanged = Signal(str)
    sessionProgress = Signal(float)

    def __init__(self):
        super().__init__()
        self._carrier_freq = 220.0
        self._beat_freq = 10.0
        self._amplitude = 0.0
        self._band = "Alpha"
        self._current_preset = ""
        self._generator = BinauralGenerator()

    @Property(float, notify=carrierFreqChanged)
    def carrierFreq(self) -> float:
        return self._carrier_freq

    @Property(float, notify=beatFreqChanged)
    def beatFreq(self) -> float:
        return self._beat_freq

    @Property(float, notify=amplitudeChanged)
    def amplitude(self) -> float:
        return self._amplitude

    @Property(str, notify=bandChanged)
    def band(self) -> str:
        return self._band

    @Property(str, notify=presetChanged)
    def currentPreset(self) -> str:
        return self._current_preset

    @Slot(str)
    def loadPreset(self, name: str) -> None:
        if name in PRESETS:
            preset = PRESETS[name]
            self._carrier_freq = preset.carrier_frequency
            self._beat_freq = preset.beat_frequency
            self._current_preset = name
            self.carrierFreqChanged.emit(self._carrier_freq)
            self.beatFreqChanged.emit(self._beat_freq)
            self.presetChanged.emit(name)

    @Slot(float)
    def setBeatFrequency(self, hz: float) -> None:
        self._beat_freq = hz
        self.beatFreqChanged.emit(hz)

    @Slot(float)
    def setCarrierFrequency(self, hz: float) -> None:
        self._carrier_freq = hz
        self.carrierFreqChanged.emit(hz)

    @Slot()
    def startPlayback(self) -> None:
        self._amplitude = 1.0
        self.amplitudeChanged.emit(1.0)

    @Slot()
    def stopPlayback(self) -> None:
        self._amplitude = 0.0
        self.amplitudeChanged.emit(0.0)

    def _update_band(self, beat: float) -> None:
        """Update brainwave band based on beat frequency."""
        if beat < 4.0:
            self._band = "Delta"
        elif beat < 8.0:
            self._band = "Theta"
        elif beat < 13.0:
            self._band = "Alpha"
        elif beat < 30.0:
            self._band = "Beta"
        else:
            self._band = "Gamma"
        self.bandChanged.emit(self._band)

    def update_from_generator(self, freqs: dict) -> None:
        carrier = freqs.get("carrier", self._carrier_freq)
        beat = freqs.get("beat", self._beat_freq)
        if carrier != self._carrier_freq:
            self._carrier_freq = carrier
            self.carrierFreqChanged.emit(carrier)
        if beat != self._beat_freq:
            self._beat_freq = beat
            self.beatFreqChanged.emit(beat)
            self._update_band(beat)