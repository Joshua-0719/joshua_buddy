import AppKit
import Foundation

let outputDirectory = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let iconsetDirectory = outputDirectory.appendingPathComponent("JoshuaNotes.iconset", isDirectory: true)
let fileManager = FileManager.default
try fileManager.createDirectory(at: iconsetDirectory, withIntermediateDirectories: true)

let iconSizes: [(Int, String)] = [
    (16, "icon_16x16.png"),
    (32, "icon_16x16@2x.png"),
    (32, "icon_32x32.png"),
    (64, "icon_32x32@2x.png"),
    (128, "icon_128x128.png"),
    (256, "icon_128x128@2x.png"),
    (256, "icon_256x256.png"),
    (512, "icon_256x256@2x.png"),
    (512, "icon_512x512.png"),
    (1024, "icon_512x512@2x.png"),
]

for (pixels, filename) in iconSizes {
    let bitmap = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: pixels,
        pixelsHigh: pixels,
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    )!
    let context = NSGraphicsContext(bitmapImageRep: bitmap)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = context
    context.imageInterpolation = .high

    let side = CGFloat(pixels)
    let bounds = NSRect(x: 0, y: 0, width: side, height: side)
    NSColor.clear.setFill()
    bounds.fill()

    let inset = side * 0.055
    let iconRect = bounds.insetBy(dx: inset, dy: inset)
    let background = NSBezierPath(roundedRect: iconRect, xRadius: side * 0.23, yRadius: side * 0.23)
    NSColor(calibratedRed: 0.078, green: 0.49, blue: 0.447, alpha: 1).setFill()
    background.fill()

    let font = NSFont.systemFont(ofSize: side * 0.66, weight: .semibold)
    let attributes: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: NSColor.white,
    ]
    let letter = NSAttributedString(string: "J", attributes: attributes)
    let letterSize = letter.size()
    let letterPoint = NSPoint(
        x: (side - letterSize.width) / 2,
        y: (side - letterSize.height) / 2 + side * 0.025
    )
    letter.draw(at: letterPoint)

    NSGraphicsContext.restoreGraphicsState()
    let pngData = bitmap.representation(using: .png, properties: [:])!
    try pngData.write(to: iconsetDirectory.appendingPathComponent(filename))
}