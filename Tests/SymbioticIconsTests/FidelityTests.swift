// MIT licence: see LICENSE.
import CoreGraphics
import Foundation
import ImageIO
import Testing
import SymbioticTokens
@testable import SymbioticIcons

/// Every standard icon drawn by the generated code at 48 px matches the
/// headless-Chrome render of its SVG (tools/references.py).
@Suite struct FidelityTests {
    static let size = 48
    /// Mean per-pixel alpha difference allowed (0...1). Measured at Task 8:
    /// worst standard icon 0.0080 (hidden), worst glyph 0.0079 (glyph-10),
    /// all antialiasing (Chrome's Skia against CoreGraphics filling stroked
    /// outlines).
    static let tolerance = 0.02
    /// Largest single-pixel alpha difference allowed (0...1). The mean alone
    /// cannot tell lock from unlock (0.006 apart, below the antialiasing
    /// noise), but no pixel of a matching icon differs by more than 0.33
    /// (measured worst: 84/255, glyph-23), while every pair of different
    /// icons has at least four pixels that differ by more than 0.5.
    static let pixelTolerance = 0.5

    static func reference(_ name: String) throws -> [UInt8] {
        let url = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
            .appendingPathComponent("References/\(name).png")
        let source = try #require(CGImageSourceCreateWithURL(url as CFURL, nil), "missing \(url.path)")
        let image = try #require(CGImageSourceCreateImageAtIndex(source, 0, nil))
        #expect(image.width == size && image.height == size)
        return IconBitmap.alpha(of: image)
    }

    static func ours(_ icon: StandardIcon) -> [UInt8] {
        let stroke = Theme.classicLight.iconStroke.width(forSize: CGFloat(size))
        return IconBitmap.alpha(of: icon.drawing, size: size, strokeWidth: stroke)
    }

    @Test(arguments: StandardIcon.allCases.map(\.rawValue))
    func matchesReference(name: String) throws {
        let icon = try #require(StandardIcon(rawValue: name))
        let ours = Self.ours(icon)
        let reference = try Self.reference(name)
        let diff = IconBitmap.meanDifference(ours, reference)
        let worst = IconBitmap.maxDifference(ours, reference)
        #expect(diff < Self.tolerance, "\(name): mean difference \(diff)")
        #expect(worst < Self.pixelTolerance, "\(name): largest pixel difference \(worst)")
    }

    @Test func aDifferentIconDoesNotMatch() throws {
        let ours = Self.ours(.play)
        #expect(IconBitmap.meanDifference(ours, try Self.reference("stop")) > Self.tolerance)
    }

    /// The closest pair of different icons: only the pixel check separates them.
    @Test func lockDoesNotMatchUnlock() throws {
        let ours = Self.ours(.lock)
        #expect(IconBitmap.maxDifference(ours, try Self.reference("unlock")) > Self.pixelTolerance)
    }
}
