// MIT licence: see LICENSE.
import AppKit
import SymbioticTokens

extension NSImage {
    /// A template image of the role at `size` points (tinted by AppKit like any
    /// template image). The stroke is the theme's icon stroke for that size.
    /// brand.logo without a brand provider becomes the wordmark: `size` high
    /// and as wide as the text. Pass the app's current theme (there is no
    /// default, so a non-default theme's stroke is never silently ignored).
    public static func icon(_ role: IconRole, size: CGFloat, theme: Theme,
                            resolver: IconResolver = Icons.resolver) -> NSImage {
        let image: NSImage
        switch resolver.resolve(role) {
        case .drawing(let drawing):
            let stroke = theme.iconStroke.width(forSize: size)
            image = NSImage(size: NSSize(width: size, height: size), flipped: true) { _ in
                guard let context = NSGraphicsContext.current?.cgContext else { return false }
                context.setFillColor(CGColor(gray: 0, alpha: 1))
                drawing.draw(in: context, size: size, strokeWidth: stroke)
                return true
            }
        case .wordmark(let text):
            let font = NSFont.systemFont(ofSize: size * 0.75, weight: .semibold)
            let attributed = NSAttributedString(string: text, attributes: [.font: font, .foregroundColor: NSColor.black])
            let width = ceil(attributed.size().width)
            image = NSImage(size: NSSize(width: width, height: size), flipped: false) { rect in
                let textHeight = attributed.size().height
                attributed.draw(at: NSPoint(x: 0, y: (rect.height - textHeight) / 2))
                return true
            }
        }
        image.isTemplate = true
        image.accessibilityDescription = role.label
        return image
    }
}
