import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"

Item {
    id: mainView
    property alias bridge: uiBridge

    UIBridge {
        id: uiBridge
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        BrainVisualizer {
            id: brainViz
            beatFreq: bridge.beatFreq
            Layout.alignment: Qt.AlignHCenter
        }

        FrequencyReadout {
            id: freqReadout
            beatFrequency: bridge.beatFreq
            carrierFrequency: bridge.carrierFreq
            Layout.alignment: Qt.AlignHCenter
        }

        WaveformDisplay {
            Layout.fillWidth: true
            height: 140
        }

        FrequencyRings {
            id: freqRings
            Layout.fillWidth: true
            height: 200
        }

        PresetGrid {
            Layout.fillWidth: true
            Layout.preferredHeight: 200
        }

        ParameterPanel {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
        }
    }
}