// MIT licence: see LICENSE.
import os

/// Supplies drawings for roles, e.g. SymbioticBrand.provider. Return nil to
/// let a role fall back to its standard icon.
public protocol IconProvider: Sendable {
    func drawing(for role: IconRole) -> IconDrawing?
}

/// What a role draws as.
public enum ResolvedIcon: Sendable, Hashable {
    case drawing(IconDrawing)
    /// Text instead of a drawing: brand.logo with no brand provider.
    case wordmark(String)
}

/// Resolves roles: the provider's drawing if it maps the role, otherwise the
/// standard icon; brand.logo without a provider becomes the wordmark.
public struct IconResolver: Sendable {
    public let provider: (any IconProvider)?

    public init(provider: (any IconProvider)?) {
        self.provider = provider
    }

    public func resolve(_ role: IconRole) -> ResolvedIcon {
        if let drawing = provider?.drawing(for: role) {
            return .drawing(drawing)
        }
        if let standard = role.standard {
            return .drawing(standard.drawing)
        }
        return .wordmark(Icons.wordmark)
    }
}

/// The app-wide icon registry.
public enum Icons {
    /// What brand.logo shows when no brand provider is registered.
    public static let wordmark = "SymbioticAudio"

    /// Registers the provider used by `Icon` and `NSImage.icon` (one per app):
    /// `#if canImport(SymbioticBrand) Icons.register(SymbioticBrand.provider) #endif`
    public static func register(_ provider: any IconProvider) {
        registry.withLock { $0 = provider }
    }

    /// Removes the registered provider; every role draws its standard icon again.
    /// Internal: tests only (`@testable import SymbioticIcons`).
    static func unregister() {
        registry.withLock { $0 = nil }
    }

    /// A resolver for the currently registered provider.
    public static var resolver: IconResolver {
        IconResolver(provider: registry.withLock { $0 })
    }

    /// A struct lock, not a class, so two copies of this module in one process
    /// (VizDAW hosting EG13) register no duplicate Objective-C class.
    private static let registry = OSAllocatedUnfairLock<(any IconProvider)?>(initialState: nil)
}
