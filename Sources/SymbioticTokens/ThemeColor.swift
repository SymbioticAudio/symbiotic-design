// MIT licence: see LICENSE.
import AppKit
import SwiftUI

/// Light or dark: the appearance a theme is designed for.
public enum ThemeAppearance: String, Sendable, Hashable, CaseIterable {
    case light
    case dark

    public var colorScheme: ColorScheme { self == .dark ? .dark : .light }

    public var nsAppearanceName: NSAppearance.Name { self == .dark ? .darkAqua : .aqua }

    /// The appearance name, in its Increase Contrast variant when `highContrast` is true.
    public func nsAppearanceName(highContrast: Bool) -> NSAppearance.Name {
        guard highContrast else { return nsAppearanceName }
        return self == .dark ? .accessibilityHighContrastDarkAqua : .accessibilityHighContrastAqua
    }

    /// The appearance names a system colour may be resolved in, best first (pre-flight M1).
    static let resolutionCandidates: [NSAppearance.Name] = [
        .accessibilityHighContrastAqua, .accessibilityHighContrastDarkAqua, .aqua, .darkAqua,
    ]

    /// The appearance a system colour is resolved in, given the best match of the drawing
    /// appearance among `resolutionCandidates`: light/dark always from the theme, the
    /// Increase Contrast variant when the match is a high-contrast name.
    func resolutionName(matching match: NSAppearance.Name?) -> NSAppearance.Name {
        let highContrast = match == .accessibilityHighContrastAqua || match == .accessibilityHighContrastDarkAqua
        return nsAppearanceName(highContrast: highContrast)
    }
}

/// A colour token value: an sRGB colour, or a macOS semantic colour with an sRGB fallback.
public struct ThemeColor: Sendable, Hashable {
    public enum Source: Sendable, Hashable {
        /// 0xRRGGBBAA in sRGB.
        case rgba(UInt32)
        /// A macOS semantic colour, resolved in the theme's appearance; the fallback serves other platforms.
        case system(SystemColorName, fallback: UInt32)
    }

    public let source: Source
    /// The appearance a system colour is resolved in, so a light theme stays light in Dark Mode.
    public let appearance: ThemeAppearance

    public init(hex: UInt32) {
        source = .rgba(hex)
        appearance = .light
    }

    public init(system: SystemColorName, fallback: UInt32, appearance: ThemeAppearance) {
        source = .system(system, fallback: fallback)
        self.appearance = appearance
    }

    /// The sRGB value written in tokens.json (the fallback for a system colour), as 0...1 components.
    public var fallbackComponents: (red: Double, green: Double, blue: Double, alpha: Double) {
        let v: UInt32
        switch source {
        case .rgba(let x): v = x
        case .system(_, let fallback): v = fallback
        }
        return (Double((v >> 24) & 0xFF) / 255, Double((v >> 16) & 0xFF) / 255,
                Double((v >> 8) & 0xFF) / 255, Double(v & 0xFF) / 255)
    }

    public var nsColor: NSColor {
        switch source {
        case .rgba:
            let c = fallbackComponents
            return NSColor(srgbRed: c.red, green: c.green, blue: c.blue, alpha: c.alpha)
        case .system(let name, _):
            let themeAppearance = appearance
            return NSColor(name: nil) { drawing in
                // Light/dark comes from the theme; Increase Contrast comes from where it is drawn.
                let match = drawing.bestMatch(from: ThemeAppearance.resolutionCandidates)
                let pinned = themeAppearance.resolutionName(matching: match)
                var resolved = NSColor.black
                let target = NSAppearance(named: pinned) ?? drawing
                target.performAsCurrentDrawingAppearance {
                    resolved = name.nsColor.usingColorSpace(.sRGB) ?? name.nsColor
                }
                return resolved
            }
        }
    }

    public var color: Color { Color(nsColor: nsColor) }
}
