// MIT licence: see LICENSE.
import AppKit
import SwiftUI
import Testing
import SymbioticTokens
@testable import SymbioticIcons

/// Draws `drawing` for every role (renders a chosen standard icon through `Icon`).
private struct EveryRoleProvider: IconProvider {
    let drawing: IconDrawing
    func drawing(for role: IconRole) -> IconDrawing? { drawing }
}

/// classic-light with a heavier icon stroke, built with the public memberwise
/// initialiser the way an app with its own palette (EG13) builds its theme.
private func heavyStrokeTheme() -> Theme {
    let base = Theme.classicLight
    return Theme(id: "test-heavy-stroke", appearance: base.appearance,
                 surface: base.surface, text: base.text, accent: base.accent, state: base.state,
                 meter: base.meter, graph: base.graph, control: base.control, strip: base.strip,
                 brand: base.brand, spacing: base.spacing, radius: base.radius,
                 iconStroke: Theme.IconStrokeMetrics(s16: 3, s24: 3.6, s32: 4.8),
                 type: base.type)
}

/// Inked pixels (alpha above `minAlpha`) of an image, in sRGB.
private func inkedColours(_ image: CGImage, minAlpha: CGFloat = 0.9) -> [NSColor] {
    let rep = NSBitmapImageRep(cgImage: image)
    var out: [NSColor] = []
    for y in 0..<image.height {
        for x in 0..<image.width {
            if let c = rep.colorAt(x: x, y: y)?.usingColorSpace(.sRGB), c.alphaComponent > minAlpha {
                out.append(c)
            }
        }
    }
    return out
}

/// The alpha mask of `drawing` rendered through the SwiftUI `Icon` view at scale 1.
@MainActor
private func viewMask(_ drawing: IconDrawing, size: CGFloat, theme: Theme) throws -> (width: Int, mask: [UInt8]) {
    let view = Icon(.transportStop, size: size, resolver: IconResolver(provider: EveryRoleProvider(drawing: drawing)))
        .foregroundStyle(Color.black)
        .symbioticTheme(theme)
    let renderer = ImageRenderer(content: view)
    renderer.scale = 1
    let image = try #require(renderer.cgImage)
    return (image.width, IconBitmap.alpha(of: image))
}

@Suite struct RenderTests {
    let plain = IconResolver(provider: nil)

    @Test(arguments: [16.0, 24.0, 32.0, 13.0])
    func nsImageIsATemplateOfTheRequestedSize(size: Double) {
        let image = NSImage.icon(.transportPlay, size: size, theme: .classicLight, resolver: plain)
        #expect(image.isTemplate)
        #expect(image.size == NSSize(width: size, height: size))
        #expect(image.accessibilityDescription == "Play")
        #expect(image.cgImage(forProposedRect: nil, context: nil, hints: nil) != nil)
    }

    @Test func wordmarkImageIsTheRequestedHeightAndWiderThanTall() {
        let image = NSImage.icon(.brandLogo, size: 24, theme: .classicLight, resolver: plain)
        #expect(image.isTemplate)
        #expect(image.size.height == 24)
        #expect(image.size.width > 48)
    }

    @Test func strokeComesFromTheThemeNotFromScaling() {
        let drawing = StandardIcon.stop.drawing
        let thin = IconBitmap.alpha(of: drawing, size: 48, strokeWidth: 1)
        let thick = IconBitmap.alpha(of: drawing, size: 48, strokeWidth: 3)
        let ink = { (mask: [UInt8]) in mask.reduce(0) { $0 + Int($1) } }
        #expect(ink(thick) > ink(thin) * 2)
    }

    @Test func templateImageUsesTheThemeStroke() {
        let image = NSImage.icon(.transportStop, size: 32, theme: .classicLight, resolver: plain)
        let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil)!
        let fromImage = IconBitmap.alpha(of: cg)
        let expected = IconBitmap.alpha(of: StandardIcon.stop.drawing, size: cg.width,
                                        strokeWidth: Theme.classicLight.iconStroke.width(forSize: 32) * CGFloat(cg.width) / 32)
        #expect(IconBitmap.meanDifference(fromImage, expected) < 0.02)
    }

    @Test func templateImageUsesACustomThemesStroke() {
        let custom = heavyStrokeTheme()
        let image = NSImage.icon(.transportStop, size: 32, theme: custom, resolver: plain)
        let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil)!
        let scale = CGFloat(cg.width) / 32
        let fromImage = IconBitmap.alpha(of: cg)
        let heavy = IconBitmap.alpha(of: StandardIcon.stop.drawing, size: cg.width,
                                     strokeWidth: custom.iconStroke.width(forSize: 32) * scale)
        let house = IconBitmap.alpha(of: StandardIcon.stop.drawing, size: cg.width,
                                     strokeWidth: Theme.classicLight.iconStroke.width(forSize: 32) * scale)
        #expect(IconBitmap.meanDifference(fromImage, heavy) < 0.02)
        #expect(IconBitmap.meanDifference(fromImage, house) > 0.05)
    }

    @MainActor @Test func iconViewDrawsInTheForegroundStyle() throws {
        let renderer = ImageRenderer(content: Icon(.transportStop, size: 24, resolver: plain).foregroundStyle(Color.red))
        renderer.scale = 2
        let image = try #require(renderer.cgImage)
        #expect(image.width == 48)
        let inked = inkedColours(image)
        let red = inked.filter { $0.redComponent > 0.9 && $0.greenComponent < 0.5 && $0.blueComponent < 0.5 }
        #expect(inked.count > 50)
        #expect(red.count == inked.count)
    }

    /// Pre-flight I2: an explicit light theme wins over a dark environment.
    @MainActor @Test func iconFollowsAnExplicitLightThemeInDarkMode() throws {
        let themed = Icon(.transportStop, size: 24, resolver: plain)
            .symbioticTheme(.classicLight)
            .environment(\.colorScheme, .dark)
        let renderer = ImageRenderer(content: themed)
        renderer.scale = 2
        // The default foreground (.primary, labelColor) is about 85% opaque.
        let inked = inkedColours(try #require(renderer.cgImage), minAlpha: 0.5)
        #expect(inked.count > 50)
        #expect(inked.allSatisfy { $0.brightnessComponent < 0.5 })

        // Control: without the theme the same view in dark mode draws light ink.
        let unthemed = ImageRenderer(content: Icon(.transportStop, size: 24, resolver: plain)
            .environment(\.colorScheme, .dark))
        unthemed.scale = 2
        let light = inkedColours(try #require(unthemed.cgImage), minAlpha: 0.5)
        #expect(light.count > 50)
        #expect(light.allSatisfy { $0.brightnessComponent > 0.5 })
    }

    /// Pre-flight M9: the SwiftUI path and the CoreGraphics path draw the same pixels.
    @MainActor @Test(arguments: ["stop", "record", "pointer", "fade-in"])
    func iconViewMatchesTheCoreGraphicsRenderer(name: String) throws {
        let drawing = try #require(StandardIcon(rawValue: name)).drawing
        let stroke = Theme.classicLight.iconStroke.width(forSize: 48)
        #expect(abs(stroke - 2.4) < 1e-9)
        let view = try viewMask(drawing, size: 48, theme: .classicLight)
        #expect(view.width == 48)
        let cg = IconBitmap.alpha(of: drawing, size: 48, strokeWidth: 2.4)
        #expect(IconBitmap.meanDifference(view.mask, cg) < 0.02)
    }

    /// A Theme value built by the app (custom palette) sets the icon stroke.
    @MainActor @Test func iconViewUsesACustomThemesStroke() throws {
        let custom = heavyStrokeTheme()
        let drawing = StandardIcon.stop.drawing
        let view = try viewMask(drawing, size: 48, theme: custom)
        let heavy = IconBitmap.alpha(of: drawing, size: 48, strokeWidth: custom.iconStroke.width(forSize: 48))
        let house = IconBitmap.alpha(of: drawing, size: 48, strokeWidth: 2.4)
        #expect(abs(custom.iconStroke.width(forSize: 48) - 7.2) < 1e-9)
        #expect(IconBitmap.meanDifference(view.mask, heavy) < 0.02)
        #expect(IconBitmap.meanDifference(view.mask, house) > 0.05)
    }

    @MainActor @Test func wordmarkViewRendersText() throws {
        let renderer = ImageRenderer(content: Icon(.brandLogo, size: 20, resolver: plain))
        let image = try #require(renderer.cgImage)
        #expect(image.width > image.height * 2)
    }
}
