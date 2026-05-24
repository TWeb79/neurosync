import QtQuick 2.15
import QtQuick.Controls 2.15

Row {
    id: panel
    spacing: 20

    Slider {
        id: beatSlider
        from: 0.5
        to: 40
        value: bridge.beatFreq
        onValueChanged: bridge.setBeatFrequency(value)
        ToolTip {
            text: value.toFixed(1) + " Hz"
            visible: beatSlider.hovered || beatSlider.pressed
        }
    }

    Slider {
        id: carrierSlider
        from: 100
        to: 400
        value: bridge.carrierFreq
        onValueChanged: bridge.setCarrierFrequency(value)
    }

    Button {
        text: "Play"
        onClicked: bridge.startPlayback()
    }
}