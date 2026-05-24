import QtQuick 2.15

Canvas {
    id: frequencyRings
    width: 200
    height: 200

    property real ringValues: [0.2, 0.4, 0.6, 0.8, 1.0]  // Default values
    property int numRings: 5

    Timer {
        interval: 33
        repeat: true
        running: true
        onTriggered: requestPaint()
    }

    onPaint: {
        var ctx = getContext("2d")
        ctx.clearRect(0, 0, width, height)

        var centerX = width / 2
        var centerY = height / 2
        var maxRadius = Math.min(width, height) / 2 * 0.8

        // Draw rings from inner to outer
        for (var i = 0; i < numRings; i++) {
            var ringIndex = i
            var value = ringValues[ringIndex] || 0.5
            
            // Base radius increases for each ring
            var baseRadius = 20 + (i * 30)
            var radiusVariation = value * 15  // +/- 15px variation
            var radius = baseRadius + radiusVariation
            
            // Color gradient from cyan to violet
            var ratio = i / (numRings - 1)
            var r = Math.round(0 + (139 - 0) * ratio)  // 0 to 139
            var g = Math.round(255 - (255 - 92) * ratio)  // 255 to 92
            var b = Math.round(200 + (246 - 200) * ratio)  // 200 to 246
            var color = "rgba(" + r + "," + g + "," + b + ",0.6)"
            
            ctx.beginPath()
            ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
            ctx.strokeStyle = color
            ctx.lineWidth = 2 - (i * 0.3)  // Decrease width for outer rings
            ctx.stroke()
        }
    }
}