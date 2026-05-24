import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
from "views/MainView.qml"

ApplicationWindow {
    id: window
    width: 1200
    height: 800
    visible: true
    title: qsTr("NeuroSync v0.2.0")

    MainView {
        anchors.fill: parent
    }
}