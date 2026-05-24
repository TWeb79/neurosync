import QtQuick 2.15
import QtQuick.Controls 2.15

Canvas {
    id: brainCanvas
    width: 400
    height: 340

    property real beatFreq: 10.0
    property real beatProgress: 0.0

    Timer {
        interval: 33
        repeat: true
        running: true
        onTriggered: requestPaint()
    }

    onBeatFreqChanged: {
        if (beatFreq > 0) {
            beatAnim.duration = 1000 / beatFreq
        }
    }

    NumberAnimation on beatProgress {
        id: beatAnim
        from: 0
        to: 1
        duration: 100
        loops: Animation.Infinite
    }

    onPaint: {
        var ctx = getContext("2d")
        ctx.clearRect(0, 0, width, height)

        ctx.fillStyle = "#0a0a12"
        ctx.strokeStyle = "rgba(0,255,200,0.12)"
        ctx.lineWidth = 1

        var r = 180
        ctx.ellipse(200, 150, r, 150, 0, 0, 2 * Math.PI)
        ctx.fill()

        var leftPulse = Math.sin(beatProgress * Math.PI) * 0.14 + 0.04
        var rightPulse = Math.sin((beatProgress + 0.5) * Math.PI) * 0.14 + 0.04

        ctx.fillStyle = "rgba(0,255,200," + leftPulse + ")"
        ctx.beginPath()
        ctx.ellipse(200, 150, r - 2, 146, 0, Math.PI, 0, true)
        ctx.fill()

        ctx.fillStyle = "rgba(139,92,246," + rightPulse + ")"
        ctx.beginPath()
        ctx.ellipse(200, 150, r - 2, 146, 0, 0, Math.PI, true)
        ctx.fill()

        ctx.strokeStyle = "rgba(255,255,255,0.15)"
        ctx.beginPath()
        ctx.moveTo(80, 150)
        ctx.quadraticCurveTo(200, 160, 320, 150)
        ctx.stroke()

        ctx.font = "14px 'Orbitron'"
        ctx.fillStyle = "#00ffc8"
        ctx.textAlign = "center"
        ctx.fillText("L " + Math.round(220) + " Hz", 120, 280)
        ctx.fillStyle = "#8b5cf6"
        ctx.fillText("R " + Math.round(230) + " Hz", 280, 280)
        ctx.fillStyle = "#e2e8f0"
        ctx.fillText("BEAT: " + beatFreq.toFixed(1) + " Hz", 200, 310)
    }
}