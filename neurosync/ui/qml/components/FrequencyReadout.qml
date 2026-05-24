import QtQuick 2.15

Row {
    id: freqRow
    spacing: 40

    property real carrierFrequency: 220.0
    property real beatFrequency: 10.0

    property real leftFreq: carrierFrequency
    property real rightFreq: carrierFrequency + beatFrequency

    Column {
        Text {
            text: leftFreq.toFixed(1) + " Hz"
            font.family: "Orbitron"
            font.pixelSize: 32
            color: "#00ffc8"
        }
        Text {
            text: "LEFT EAR"
            font.family: "JetBrains Mono"
            font.pixelSize: 10
            color: "#64748b"
        }
    }

    Column {
        Text {
            text: beatFrequency.toFixed(1) + " Hz"
            font.family: "Orbitron"
            font.pixelSize: 32
            color: "#e2e8f0"
        }
        Text {
            text: "BEAT"
            font.family: "JetBrains Mono"
            font.pixelSize: 10
            color: "#64748b"
        }
    }

    Column {
        Text {
            text: rightFreq.toFixed(1) + " Hz"
            font.family: "Orbitron"
            font.pixelSize: 32
            color: "#8b5cf6"
        }
        Text {
            text: "RIGHT EAR"
            font.family: "JetBrains Mono"
            font.pixelSize: 10
            color: "#64748b"
        }
    }
}