// MIT licence: see LICENSE.
import AppKit
import SwiftUI

/// The weights a type token may use (tools/tokenlib.py WEIGHTS).
public enum FontWeight: String, Sendable, Hashable, CaseIterable {
    case ultraLight, thin, light, regular, medium, semibold, bold, heavy, black

    public var swiftUI: Font.Weight {
        switch self {
        case .ultraLight: return .ultraLight
        case .thin: return .thin
        case .light: return .light
        case .regular: return .regular
        case .medium: return .medium
        case .semibold: return .semibold
        case .bold: return .bold
        case .heavy: return .heavy
        case .black: return .black
        }
    }

    public var appKit: NSFont.Weight {
        switch self {
        case .ultraLight: return .ultraLight
        case .thin: return .thin
        case .light: return .light
        case .regular: return .regular
        case .medium: return .medium
        case .semibold: return .semibold
        case .bold: return .bold
        case .heavy: return .heavy
        case .black: return .black
        }
    }
}

/// A type token: the system font at a size and weight.
public struct TypeStyle: Sendable, Hashable {
    public let size: CGFloat
    public let weight: FontWeight

    public init(size: CGFloat, weight: FontWeight) {
        self.size = size
        self.weight = weight
    }

    public var font: Font { .system(size: size, weight: weight.swiftUI) }
    public var nsFont: NSFont { .systemFont(ofSize: size, weight: weight.appKit) }
}
