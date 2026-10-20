// MIT licence: see LICENSE.
import SwiftUI
import SymbioticTokens

/// An icon drawn by role in the current foreground style, with the theme's
/// icon stroke for its size.
public struct Icon: View {
    private let role: IconRole
    private let size: CGFloat
    private let resolver: IconResolver?
    @Environment(\.symbioticTheme) private var theme

    public init(_ role: IconRole, size: CGFloat = 16) {
        self.init(role, size: size, resolver: nil)
    }

    /// Uses `resolver` instead of the registered provider (previews and tests).
    public init(_ role: IconRole, size: CGFloat = 16, resolver: IconResolver?) {
        self.role = role
        self.size = size
        self.resolver = resolver
    }

    public var body: some View {
        switch (resolver ?? Icons.resolver).resolve(role) {
        case .drawing(let drawing):
            let stroke = theme.iconStroke.width(forSize: size)
            Canvas { context, canvasSize in
                let side = min(canvasSize.width, canvasSize.height)
                for path in drawing.inkPaths(size: side, strokeWidth: stroke) {
                    context.fill(Path(path), with: .foreground, style: FillStyle(eoFill: false))
                }
            }
            .frame(width: size, height: size)
            .accessibilityElement()
            .accessibilityLabel(role.label)
            .accessibilityAddTraits(.isImage)
        case .wordmark(let text):
            Text(text)
                .font(.system(size: size * 0.75, weight: .semibold))
                .lineLimit(1)
                .fixedSize()
                .frame(height: size)
                .accessibilityLabel(role.label)
        }
    }
}
