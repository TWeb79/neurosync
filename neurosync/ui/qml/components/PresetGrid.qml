import QtQuick 2.15
import QtQuick.Controls 2.15

GridView {
    id: grid
    cellWidth: 180
    cellHeight: 180
    model: ListModel {
        ListElement { name: "Deep Sleep"; beat: 2.0; band: "Delta"; duration: 3600 }
        ListElement { name: "Coding Flow"; beat: 14.0; band: "Beta"; duration: 2700 }
        ListElement { name: "Zen Meditation"; beat: 7.0; band: "Theta"; duration: 1800 }
        ListElement { name: "Creative Flow"; beat: 8.0; band: "Theta"; duration: 1800 }
    }

    delegate: Rectangle {
        width: 160
        height: 160
        radius: 16
        color: "#0c0c14"
        border.color: "#00ffc8"
        border.width: 1

        Column {
            anchors.margins: 12
            anchors.fill: parent
            spacing: 4

            Text {
                text: model.name
                font.family: "Rajdhani"
                font.pixelSize: 16
                font.bold: true
                color: "white"
            }
            Text {
                text: model.band + " · " + model.beat + " Hz"
                font.family: "JetBrains Mono"
                font.pixelSize: 11
                color: "#64748b"
            }
        }

        MouseArea {
            anchors.fill: parent
            onClicked: bridge.loadPreset(model.name.toLowerCase().replace(" ", "_"))
        }
    }
}