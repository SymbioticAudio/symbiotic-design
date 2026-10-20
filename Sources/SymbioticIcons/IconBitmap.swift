// MIT licence: see LICENSE.
import CoreGraphics

/// Coverage masks for comparing icon renderings. Internal: tests only
/// (`@testable import SymbioticIcons`).
enum IconBitmap {
    /// Renders `drawing` at `size` x `size` pixels in black on transparent and
    /// returns the alpha channel, row by row from the top.
    static func alpha(of drawing: IconDrawing, size: Int, strokeWidth: CGFloat) -> [UInt8] {
        render(width: size, height: size) { context in
            context.translateBy(x: 0, y: CGFloat(size))
            context.scaleBy(x: 1, y: -1)
            context.setFillColor(CGColor(gray: 0, alpha: 1))
            drawing.draw(in: context, size: CGFloat(size), strokeWidth: strokeWidth)
        }
    }

    /// The alpha channel of an image, row by row from the top.
    static func alpha(of image: CGImage) -> [UInt8] {
        render(width: image.width, height: image.height) { context in
            context.draw(image, in: CGRect(x: 0, y: 0, width: image.width, height: image.height))
        }
    }

    /// Mean absolute difference of two equal-length masks, 0 (same) to 1.
    static func meanDifference(_ a: [UInt8], _ b: [UInt8]) -> Double {
        precondition(a.count == b.count, "masks differ in size")
        guard !a.isEmpty else { return 0 }
        var total = 0
        for i in a.indices {
            total += abs(Int(a[i]) - Int(b[i]))
        }
        return Double(total) / Double(a.count) / 255
    }

    /// How many pixels of two equal-length masks differ by more than
    /// `threshold` (0...1). Catches a small missing or extra stroke that the
    /// mean cannot (lock and unlock differ by a mean of only about 0.006 at
    /// 48 px), while tolerating a stray antialiased pixel or two.
    static func pixelsDiffering(_ a: [UInt8], _ b: [UInt8], by threshold: Double) -> Int {
        precondition(a.count == b.count, "masks differ in size")
        let limit = threshold * 255
        var count = 0
        for i in a.indices where Double(abs(Int(a[i]) - Int(b[i]))) > limit {
            count += 1
        }
        return count
    }

    private static func render(width: Int, height: Int, _ body: (CGContext) -> Void) -> [UInt8] {
        var pixels = [UInt8](repeating: 0, count: width * height * 4)
        pixels.withUnsafeMutableBytes { buffer in
            guard let context = CGContext(
                data: buffer.baseAddress, width: width, height: height, bitsPerComponent: 8,
                bytesPerRow: width * 4, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { return }
            body(context)
        }
        return stride(from: 3, to: pixels.count, by: 4).map { pixels[$0] }
    }
}
