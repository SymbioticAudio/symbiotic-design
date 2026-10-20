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
    /// A pixel is "wrong" when its alpha differs by more than this (0...1).
    /// The mean alone cannot tell zoom-in from zoom-out (0.013 apart, below
    /// the tolerance). Measured at Task 8: no pixel of a matching icon
    /// differs by more than 0.33 (84/255, glyph-23). Re-measured after the
    /// unlock redraw (final review I1): every one of the 21,756 ordered pairs
    /// of different icons and glyphs has at least 16 pixels that differ by
    /// more than 0.5 (fewest: zoom-in/zoom-out, 16; lock/unlock is now 214,
    /// unlock/lock 220, up from 4).
    static let pixelThreshold = 0.5
    /// An icon fails when this many pixels or more are wrong. Count-based so
    /// one stray antialiased pixel on another renderer cannot flake CI;
    /// well below the closest pair's 16.
    static let wrongPixelLimit = 3

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
        let wrong = IconBitmap.pixelsDiffering(ours, reference, by: Self.pixelThreshold)
        #expect(diff < Self.tolerance, "\(name): mean difference \(diff)")
        #expect(wrong < Self.wrongPixelLimit, "\(name): \(wrong) pixels differ by more than \(Self.pixelThreshold)")
    }

    @Test func aDifferentIconDoesNotMatch() throws {
        let ours = Self.ours(.play)
        #expect(IconBitmap.meanDifference(ours, try Self.reference("stop")) > Self.tolerance)
    }

    /// A state pair that must read as two states: lock and unlock differ by
    /// far more than the limit (214 pixels when measured), and by the mean too.
    @Test func lockDoesNotMatchUnlock() throws {
        let ours = Self.ours(.lock)
        let reference = try Self.reference("unlock")
        let wrong = IconBitmap.pixelsDiffering(ours, reference, by: Self.pixelThreshold)
        #expect(wrong >= 10 * Self.wrongPixelLimit)
        #expect(IconBitmap.meanDifference(ours, reference) > Self.tolerance)
    }

    /// The closest pair of different icons: only the pixel check separates them.
    @Test func zoomInDoesNotMatchZoomOut() throws {
        let ours = Self.ours(.zoomIn)
        let wrong = IconBitmap.pixelsDiffering(ours, try Self.reference("zoom-out"), by: Self.pixelThreshold)
        #expect(wrong >= Self.wrongPixelLimit)
    }
}
