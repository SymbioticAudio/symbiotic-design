// MIT licence: see LICENSE.
import AppKit
import SwiftUI
import Testing
@testable import SymbioticTokens

@Suite struct ThemeTests {
    @Test func themesInTokensOrder() {
        #expect(Theme.all.map(\.id) == ["classic-light", "studio-dark", "flat", "console", "symbiotic"])
        #expect(Theme.all.map(\.appearance) == [.light, .dark, .light, .dark, .light])
        #expect(Theme.all.map(\.isPlaceholder) == [false, false, true, true, false])
        #expect(Theme.all.last == .symbiotic)
    }

    @Test func typedGroupsReadAsInTheSpec() {
        let theme = Theme.classicLight
        #expect(theme.spacing.m == 12)
        #expect(theme.meter.clip.fallbackComponents.red == 1)
        #expect(theme.control.eqLow == Theme.classicLight.control.eqLow)
        #expect(theme.type.body.size == 13)
        #expect(theme.type.title.weight == .semibold)
    }

    @Test(arguments: Theme.all.map(\.id))
    func everyTokenResolves(id: String) throws {
        let theme = try #require(Theme.named(id))
        let colours: [ThemeColor] = [
            theme.surface.window, theme.surface.panel, theme.surface.raised, theme.surface.inset,
            theme.surface.separator, theme.surface.selection, theme.surface.focusRing,
            theme.text.primary, theme.text.secondary, theme.text.disabled, theme.text.inverse,
            theme.accent.accent, theme.accent.onAccent,
            theme.state.record, theme.state.play, theme.state.solo, theme.state.mute,
            theme.state.warning, theme.state.error, theme.state.offline,
            theme.meter.background, theme.meter.low, theme.meter.mid, theme.meter.high, theme.meter.clip,
            theme.graph.line, theme.graph.fill, theme.graph.grid, theme.graph.handle, theme.graph.handleSelected,
            theme.control.gain, theme.control.eqLow, theme.control.eqLowMid, theme.control.eqHighMid,
            theme.control.eqHigh, theme.control.send, theme.control.pan, theme.control.dynamics, theme.control.filter,
            theme.strip.channel, theme.strip.instrument, theme.strip.auxReturn, theme.strip.bus, theme.strip.master,
            theme.brand.gold, theme.brand.cyan, theme.brand.cyanInk, theme.brand.ink, theme.brand.paper,
            theme.brand.rule,
        ]
        for colour in colours {
            #expect(colour.nsColor.usingColorSpace(.sRGB) != nil)
            _ = colour.color
            if case .system = colour.source {
                #expect(colour.appearance == theme.appearance)
            }
        }
        let metrics: [CGFloat] = [
            theme.spacing.xxs, theme.spacing.xs, theme.spacing.s, theme.spacing.m, theme.spacing.l, theme.spacing.xl,
            theme.radius.none, theme.radius.s, theme.radius.m, theme.radius.l,
            theme.iconStroke.s16, theme.iconStroke.s24, theme.iconStroke.s32,
        ]
        #expect(metrics.allSatisfy { $0 >= 0 })
        for style in [theme.type.caption, theme.type.body, theme.type.label, theme.type.title, theme.type.display] {
            #expect(style.nsFont.pointSize == style.size)
        }
    }

    @Test func brandColoursNeedNoTheme() {
        #expect(Brand.gold == ThemeColor(hex: 0xEFC031FF))
        let brands = Theme.all.map(\.brand)
        #expect(brands.allSatisfy {
            $0 == Theme.BrandColors(gold: Brand.gold, cyan: Brand.cyan, cyanInk: Brand.cyanInk,
                                    ink: Brand.ink, paper: Brand.paper, rule: Brand.rule)
        })
    }

    @Test func hexColourIsExact() {
        let c = ThemeColor(hex: 0x336699CC).nsColor.usingColorSpace(.sRGB)!
        #expect(abs(c.redComponent - 0x33 / 255.0) < 0.0001)
        #expect(abs(c.alphaComponent - 0xCC / 255.0) < 0.0001)
    }

    @Test func lightThemeStaysLightInDarkMode() {
        var light = NSColor.black
        var dark = NSColor.white
        NSAppearance(named: .darkAqua)!.performAsCurrentDrawingAppearance {
            light = Theme.classicLight.surface.window.nsColor.usingColorSpace(.sRGB)!
        }
        NSAppearance(named: .aqua)!.performAsCurrentDrawingAppearance {
            dark = Theme.studioDark.surface.window.nsColor.usingColorSpace(.sRGB)!
        }
        #expect(light.brightnessComponent > 0.6)
        #expect(dark.brightnessComponent < 0.4)
    }

    /// Pre-flight M1: Increase Contrast picks the high-contrast variant; light/dark stays the theme's.
    @Test func increaseContrastIsKeptWhileTheAppearanceStaysPinned() {
        func resolved(_ colour: () -> NSColor, in name: NSAppearance.Name) -> NSColor {
            var out = NSColor.clear
            NSAppearance(named: name)!.performAsCurrentDrawingAppearance {
                out = colour().usingColorSpace(.sRGB)!
            }
            return out
        }
        let themed = resolved({ Theme.classicLight.text.secondary.nsColor }, in: .accessibilityHighContrastDarkAqua)
        let expected = resolved({ NSColor.secondaryLabelColor }, in: .accessibilityHighContrastAqua)
        #expect(themed == expected)
        let normal = resolved({ Theme.classicLight.text.secondary.nsColor }, in: .darkAqua)
        #expect(normal == resolved({ NSColor.secondaryLabelColor }, in: .aqua))
    }

    /// The choice behind M1, tested on names: on macOS 26, outside a running app,
    /// `NSAppearance(named:)` turns the high-contrast names into their plain ones, so
    /// the test above cannot tell the variants apart.
    @Test(arguments: [
        (ThemeAppearance.light, NSAppearance.Name.accessibilityHighContrastDarkAqua,
         NSAppearance.Name.accessibilityHighContrastAqua),
        (.light, .accessibilityHighContrastAqua, .accessibilityHighContrastAqua),
        (.light, .darkAqua, .aqua),
        (.light, .aqua, .aqua),
        (.dark, .accessibilityHighContrastAqua, .accessibilityHighContrastDarkAqua),
        (.dark, .accessibilityHighContrastDarkAqua, .accessibilityHighContrastDarkAqua),
        (.dark, .aqua, .darkAqua),
    ])
    func resolutionKeepsTheThemesModeAndTheDrawingsContrast(
        theme: ThemeAppearance, match: NSAppearance.Name, expected: NSAppearance.Name
    ) {
        #expect(theme.resolutionName(matching: match) == expected)
    }

    @Test func resolutionWithoutAMatchUsesThePlainThemeAppearance() {
        #expect(ThemeAppearance.light.resolutionName(matching: nil) == .aqua)
        #expect(ThemeAppearance.dark.resolutionName(matching: nil) == .darkAqua)
    }

    /// Review M1: if the high-contrast appearance cannot be made, the theme's own
    /// light/dark is used, never the appearance being drawn in.
    @Test func missingHighContrastAppearanceFallsBackToTheThemesAppearance() {
        let drawing = NSAppearance(named: .darkAqua)!
        let noHighContrast: (NSAppearance.Name) -> NSAppearance? = { name in
            name == .accessibilityHighContrastAqua || name == .accessibilityHighContrastDarkAqua
                ? nil : NSAppearance(named: name)
        }
        let light = ThemeAppearance.light.resolutionAppearance(
            matching: .accessibilityHighContrastDarkAqua, drawing: drawing, named: noHighContrast)
        #expect(light.name == .aqua)
        let dark = ThemeAppearance.dark.resolutionAppearance(
            matching: .accessibilityHighContrastAqua, drawing: NSAppearance(named: .aqua)!, named: noHighContrast)
        #expect(dark.name == .darkAqua)
        // Only when no appearance can be made at all is the drawing appearance used.
        let none = ThemeAppearance.light.resolutionAppearance(matching: .aqua, drawing: drawing, named: { _ in nil })
        #expect(none === drawing)
    }

    /// Review M3: the Theme's appearance decides how its system colours resolve, even when
    /// they were copied from a theme of the other appearance.
    @Test func customDarkThemeResolvesCopiedSystemColoursDark() {
        let base = Theme.classicLight
        let dark = Theme(
            id: "copied-dark", appearance: .dark, surface: base.surface, text: base.text, accent: base.accent,
            state: base.state, meter: base.meter, graph: base.graph, control: base.control, strip: base.strip,
            brand: base.brand, spacing: base.spacing, radius: base.radius, iconStroke: base.iconStroke, type: base.type)
        func resolved(_ colour: NSColor, in name: NSAppearance.Name) -> NSColor {
            var out = NSColor.clear
            NSAppearance(named: name)!.performAsCurrentDrawingAppearance { out = colour.usingColorSpace(.sRGB)! }
            return out
        }
        let expected = resolved(.labelColor, in: .darkAqua)
        #expect(expected != resolved(.labelColor, in: .aqua))
        // Drawn in a light window, the dark theme's text is still dark-mode text.
        #expect(resolved(dark.text.primary.nsColor, in: .aqua) == expected)
        #expect(dark.text.primary.appearance == .dark)
        // The preset is untouched, and rebuilding a preset through the init changes nothing.
        #expect(resolved(base.text.primary.nsColor, in: .darkAqua) == resolved(.labelColor, in: .aqua))
        for theme in Theme.all {
            let rebuilt = Theme(
                id: theme.id, appearance: theme.appearance, isPlaceholder: theme.isPlaceholder,
                surface: theme.surface, text: theme.text, accent: theme.accent, state: theme.state,
                meter: theme.meter, graph: theme.graph, control: theme.control, strip: theme.strip,
                brand: theme.brand, spacing: theme.spacing, radius: theme.radius, iconStroke: theme.iconStroke,
                type: theme.type)
            #expect(rebuilt == theme)
        }
        // A hex colour has no appearance to pin.
        #expect(ThemeColor(hex: 0x336699FF).pinned(to: .dark) == ThemeColor(hex: 0x336699FF))
    }

    @Test func environmentDefaultFollowsColorScheme() {
        var env = EnvironmentValues()
        env.colorScheme = .light
        #expect(env.symbioticTheme.id == "classic-light")
        env.colorScheme = .dark
        #expect(env.symbioticTheme.id == "studio-dark")
        env.symbioticTheme = .console
        env.colorScheme = .light
        #expect(env.symbioticTheme.id == "console")
    }

    @Test func lookupByID() {
        #expect(Theme.named("flat") == .flat)
        #expect(Theme.named("symbiotic") == .symbiotic)
        #expect(Theme.named("cubase-dark") == nil)
    }

    @Test func iconStrokeIsExactAtTokenSizesAndScalesOutside() {
        let s = Theme.classicLight.iconStroke
        #expect(s.width(forSize: 16) == s.s16)
        #expect(s.width(forSize: 24) == s.s24)
        #expect(s.width(forSize: 32) == s.s32)
        #expect(abs(s.width(forSize: 20) - (s.s16 + s.s24) / 2) < 0.0001)
        #expect(abs(s.width(forSize: 48) - s.s32 * 1.5) < 0.0001)
        #expect(abs(s.width(forSize: 8) - s.s16 / 2) < 0.0001)
    }

    /// An app with its own identity (EG13) builds a Theme from the primitives.
    static func customTheme() -> Theme {
        let base = Theme.classicLight
        return Theme(
            id: "eg13", appearance: .dark,
            surface: base.surface, text: base.text,
            accent: Theme.AccentColors(accent: ThemeColor(hex: 0xEFC031FF), onAccent: ThemeColor(hex: 0x222222FF)),
            state: base.state, meter: base.meter, graph: base.graph, control: base.control,
            strip: base.strip, brand: base.brand, spacing: Theme.SpacingMetrics(xxs: 1, xs: 2, s: 4, m: 6, l: 8, xl: 12),
            radius: base.radius, iconStroke: Theme.IconStrokeMetrics(s16: 1, s24: 1.5, s32: 2),
            type: Theme.TypeStyles(caption: TypeStyle(size: 9, weight: .regular), body: base.type.body,
                                   label: base.type.label, title: base.type.title, display: base.type.display))
    }

    @Test func customThemeIsBuiltFromScratchAndReadThroughTheEnvironment() {
        let custom = Self.customTheme()
        #expect(custom.isPlaceholder == false)
        #expect(Theme.named("eg13") == nil)
        var env = EnvironmentValues()
        env.symbioticTheme = custom
        #expect(env.symbioticTheme == custom)
        #expect(env.symbioticTheme.accent.accent == ThemeColor(hex: 0xEFC031FF))
        #expect(env.symbioticTheme.accent.accent != Theme.classicLight.accent.accent)
        // Same values, but the dark theme re-pins classic-light's system colours (review M3).
        #expect(env.symbioticTheme.surface == Theme.classicLight.surface.pinned(to: .dark))
        #expect(env.symbioticTheme.surface != Theme.classicLight.surface)
        #expect(env.symbioticTheme.meter == Theme.classicLight.meter)
        #expect(env.symbioticTheme.spacing.m == 6)
        #expect(env.symbioticTheme.iconStroke.width(forSize: 24) == 1.5)
        #expect(env.symbioticTheme.type.caption.size == 9)
    }

    /// Pre-flight I2: one modifier applies a theme and its colour scheme.
    @MainActor @Test(arguments: [false, true])
    func themeModifierSetsThemeAndColorScheme(custom: Bool) {
        let theme = custom ? Self.customTheme() : Theme.classicLight
        let probe = EnvironmentProbe()
        // The outer colour scheme is the opposite of the theme's, as in a host app in the other mode.
        let outer: ColorScheme = theme.appearance == .dark ? .light : .dark
        let view = ProbeView(probe: probe).symbioticTheme(theme).environment(\.colorScheme, outer)
        _ = ImageRenderer(content: view).nsImage
        #expect(probe.theme == theme)
        #expect(probe.colorScheme == theme.appearance.colorScheme)
    }
}

@MainActor final class EnvironmentProbe {
    var theme: Theme?
    var colorScheme: ColorScheme?
}

private struct ProbeView: View {
    let probe: EnvironmentProbe
    @Environment(\.symbioticTheme) private var theme
    @Environment(\.colorScheme) private var colorScheme

    var body: some View {
        probe.theme = theme
        probe.colorScheme = colorScheme
        return Color.clear.frame(width: 4, height: 4)
    }
}
