// MIT licence: see LICENSE.
import CoreGraphics
import SwiftUI

extension Theme {
    /// The theme with this ID, e.g. a choice saved in preferences.
    public static func named(_ id: String) -> Theme? {
        all.first { $0.id == id }
    }

    /// The default theme for a colour scheme: classic-light or studio-dark.
    public static func standard(for scheme: ColorScheme) -> Theme {
        scheme == .dark ? .studioDark : .classicLight
    }
}

extension Theme.IconStrokeMetrics {
    /// Icon stroke width in points for an icon drawn at `size` points.
    ///
    /// Exact at 16, 24 and 32; linear between them; proportional to the
    /// nearest token below 16 and above 32.
    public func width(forSize size: CGFloat) -> CGFloat {
        if size <= 16 { return s16 * size / 16 }
        if size <= 24 { return s16 + (s24 - s16) * (size - 16) / 8 }
        if size <= 32 { return s24 + (s32 - s24) * (size - 24) / 8 }
        return s32 * size / 32
    }
}

private struct SymbioticThemeKey: EnvironmentKey {
    static let defaultValue: Theme? = nil
}

extension EnvironmentValues {
    /// The current theme. Unless set, classic-light in light mode and studio-dark in dark mode.
    public var symbioticTheme: Theme {
        get { self[SymbioticThemeKey.self] ?? Theme.standard(for: colorScheme) }
        set { self[SymbioticThemeKey.self] = newValue }
    }
}

extension View {
    /// Applies a theme and its colour scheme, so icons, template images and native
    /// controls drawn below follow the theme's light/dark appearance, not the window's.
    public func symbioticTheme(_ theme: Theme) -> some View {
        environment(\.symbioticTheme, theme).environment(\.colorScheme, theme.appearance.colorScheme)
    }
}
