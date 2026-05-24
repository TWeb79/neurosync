import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: window
    width: 1200
    height: 800
    visible: true
    title: qsTr("NeuroSync v0.1.0 (2026-05-24)")

    property int beatFrequency: 10
    property int carrierFrequency: 220
    property string sessionState: "ready"

    Rectangle {
        anchors.fill: parent
        color: "#0a0a0a"

        Column {
            anchors.fill: parent
            padding: 20
            spacing: 20

            Text {
                text: "NeuroSync"
                color: "#00ffff"
                font.pixelSize: 48
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Adaptive Brainwave Audio Studio"
                color: "#ffffff"
                font.pixelSize: 18
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 300
                height: 300
                color: "#0a0a2a"
                border.color: "#00ffff"
                border.width: 2
                radius: 150

                Rectangle {
                    anchors.centerIn: parent
                    width: 20
                    height: 20
                    color: "#00ffff"
                    radius: 10

                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        NumberAnimation { to: 0.3; duration: 1000 }
                        NumberAnimation { to: 1.0; duration: 1000 }
                    }
                }

                RotationAnimation on rotation {
                    from: 0
                    to: 360
                    duration: 4000
                    loops: Animation.Infinite
                }
            }

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 20

                Button {
                    text: "Deep Sleep (2Hz)"
                    onClicked: {
                        beatFrequency = 2; carrierFrequency = 180
                        sessionState = "Deep Sleep active"
                    }
                }
                Button {
                    text: "Focus (14Hz)"
                    onClicked: {
                        beatFrequency = 14; carrierFrequency = 220
                        sessionState = "Focus active"
                    }
                }
                Button {
                    text: "Meditate (7Hz)"
                    onClicked: {
                        beatFrequency = 7; carrierFrequency = 200
                        sessionState = "Meditation active"
                    }
                }
            }

            Text {
                text: "Beat: " + beatFrequency + " Hz | Carrier: " + carrierFrequency + " Hz"
                color: "#00ff00"
                font.pixelSize: 16
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: sessionState
                color: "#ffff00"
                font.pixelSize: 14
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }
}