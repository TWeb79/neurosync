import QtQuick 2.15

Canvas {
    id: waveform
    width: parent.width
    height: 140

    Timer {
        interval: 33
        repeat: true
        running: true
        onTriggered: requestPaint()
    }

    onPaint: {
        var ctx = getContext("2d")
        ctx.clearRect(0, 0, width, height)

        ctx.strokeStyle = "rgba(255,255,255,0.04)"
        ctx.beginPath()
        ctx.moveTo(0, 40)
        ctx.lineTo(width, 40)
        ctx.moveTo(0, 100)
        ctx.lineTo(width, 100)
        ctx.stroke()

        ctx.strokeStyle = "#00ffc8"
        ctx.lineWidth = 1.5
        ctx.beginPath()
        for (var i = 0; i < width; i += 10) {
            var y = 40 + Math.sin(i * 0.1) * 15
            if (i === 0) ctx.moveTo(i, y)
            else ctx.lineTo(i, y)
        }
        ctx.stroke()

        ctx.strokeStyle = "#8b5cf6"
        ctx.beginPath()
        for (var j = 0; j < width; j += 10) {
            var y2 = 100 + Math.sin(j * 0.1 + 1) * 15
            if (j === 0) ctx.moveTo(j, y2)
            else ctx.lineTo(j, y2)
        }
        ctx.stroke()
    }
}