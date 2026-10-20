// MIT licence: see LICENSE.
import AppKit
import SymbioticTokens

extension NSImage {
    /// A template image of the role at `size` points (tinted by AppKit like any
    /// template image). The stroke is the theme's icon stroke for that size.
    /// brand.logo without a brand provider becomes the wordmark: `size` high
    /// and as wide as the text. Pass the app's current theme (there is no
    /// default, so a non-default theme's stroke is never silently ignored).
    /// Drawn into a larger rect, or after `image.size` is changed, the icon fills
    /// that rect but keeps the stroke for `size`; for another size's stroke, ask
    /// for a new image.
    public static func icon(_ role: IconRole, size: CGFloat, theme: Theme,
                            resolver: IconResolver = Icons.resolver) -> NSImage {
        let image: NSImage
        switch resolver.resolve(role) {
        case .drawing(let drawing):
            let stroke = theme.iconStroke.width(forSize: size)
            image = NSImage(size: NSSize(width: size, height: size))
            image.addRepresentation(IconImageRep(drawing: drawing, size: size, strokeWidth: stroke))
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

/// Draws an icon into whatever rect AppKit asks for. A drawing-handler image is
/// always handed its original bounds with a magnifying transform, which would
/// fatten the stroke; `draw(in:)` here receives the real destination rect.
final class IconImageRep: NSImageRep, @unchecked Sendable {
    private let drawing: IconDrawing
    private let strokeWidth: CGFloat

    init(drawing: IconDrawing, size: CGFloat, strokeWidth: CGFloat) {
        self.drawing = drawing
        self.strokeWidth = strokeWidth
        super.init()
        self.size = NSSize(width: size, height: size)
        self.hasAlpha = true
    }

    required init?(coder: NSCoder) {
        nil
    }

    /// NSImageRep's own copy duplicates the object's bytes without retaining
    /// the stored Swift references, so freeing the original and the copy would
    /// release `drawing` twice. Build a fresh rep instead (NSImage.copy() copies
    /// its representations through this too).
    override func copy(with zone: NSZone? = nil) -> Any {
        let copy = IconImageRep(drawing: drawing, size: size.width, strokeWidth: strokeWidth)
        copy.size = size
        return copy
    }

    override func draw() -> Bool {
        draw(in: NSRect(origin: .zero, size: size))
    }

    override func draw(in rect: NSRect) -> Bool {
        guard let graphics = NSGraphicsContext.current else { return false }
        let context = graphics.cgContext
        let side = min(rect.width, rect.height)
        context.saveGState()
        defer { context.restoreGState() }
        // Centre the square icon in the rect; the drawing's y axis points down.
        let x = rect.minX + (rect.width - side) / 2
        let y = rect.minY + (rect.height - side) / 2
        if graphics.isFlipped {
            context.translateBy(x: x, y: y)
        } else {
            context.translateBy(x: x, y: y + side)
            context.scaleBy(x: 1, y: -1)
        }
        context.setFillColor(CGColor(gray: 0, alpha: 1))
        drawing.draw(in: context, size: side, strokeWidth: strokeWidth)
        return true
    }
}
