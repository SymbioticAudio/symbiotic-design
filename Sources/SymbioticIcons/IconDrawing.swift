// MIT licence: see LICENSE.
import CoreGraphics

/// One path command on the 24-unit icon grid (y down).
public enum PathOp: Sendable, Hashable {
    case move(CGFloat, CGFloat)
    case line(CGFloat, CGFloat)
    case curve(CGFloat, CGFloat, CGFloat, CGFloat, CGFloat, CGFloat)
    case close
}

/// One stroked and/or filled path of an icon.
public struct IconShape: Sendable, Hashable {
    public enum Paint: Sendable, Hashable { case stroke, fill, fillAndStroke }
    public enum Cap: Sendable, Hashable { case butt, round, square }
    public enum Join: Sendable, Hashable { case miter, round, bevel }

    public let paint: Paint
    /// Stroke width relative to the house stroke (1.2 grid units = 1).
    public let weight: CGFloat
    public let cap: Cap
    public let join: Join
    public let ops: [PathOp]

    public init(paint: Paint, weight: CGFloat, cap: Cap, join: Join, ops: [PathOp]) {
        self.paint = paint
        self.weight = weight
        self.cap = cap
        self.join = join
        self.ops = ops
    }
}

/// A complete icon as generated drawing code: shapes on a 24-unit grid.
public struct IconDrawing: Sendable, Hashable {
    public static let gridSize: CGFloat = 24
    /// SVG's default miter limit, which the source artwork assumes.
    public static let miterLimit: CGFloat = 4

    public let shapes: [IconShape]

    public init(shapes: [IconShape]) {
        self.shapes = shapes
    }

    /// The path of one shape scaled from the grid to a `size`-point square, y down.
    public func path(of shape: IconShape, size: CGFloat) -> CGPath {
        let k = size / Self.gridSize
        let path = CGMutablePath()
        for op in shape.ops {
            switch op {
            case let .move(x, y):
                path.move(to: CGPoint(x: x * k, y: y * k))
            case let .line(x, y):
                path.addLine(to: CGPoint(x: x * k, y: y * k))
            case let .curve(x1, y1, x2, y2, x, y):
                path.addCurve(to: CGPoint(x: x * k, y: y * k),
                              control1: CGPoint(x: x1 * k, y: y1 * k),
                              control2: CGPoint(x: x2 * k, y: y2 * k))
            case .close:
                path.closeSubpath()
            }
        }
        return path
    }

    /// The filled regions that make up the icon at `size` points with the given
    /// stroke, in drawing order: each fill as-is, each stroke converted to its
    /// outline. Fill every path with the non-zero winding rule. This is the one
    /// drawing routine: `draw(in:size:strokeWidth:)` and the SwiftUI `Icon` both
    /// fill these paths, so the two renderers cannot diverge.
    func inkPaths(size: CGFloat, strokeWidth: CGFloat) -> [CGPath] {
        var out: [CGPath] = []
        for shape in shapes {
            let path = path(of: shape, size: size)
            if shape.paint != .stroke {
                out.append(path)
            }
            if shape.paint != .fill {
                out.append(path.copy(strokingWithWidth: strokeWidth * shape.weight,
                                     lineCap: shape.cap.cgLineCap,
                                     lineJoin: shape.join.cgLineJoin,
                                     miterLimit: Self.miterLimit))
            }
        }
        return out
    }

    /// Draws into a context whose y axis points down, with its current fill
    /// colour. `strokeWidth` is the theme's icon stroke for `size`; it is not
    /// scaled with the drawing.
    public func draw(in context: CGContext, size: CGFloat, strokeWidth: CGFloat) {
        for path in inkPaths(size: size, strokeWidth: strokeWidth) {
            context.addPath(path)
            context.fillPath(using: .winding)
        }
    }
}

extension IconShape.Cap {
    public var cgLineCap: CGLineCap {
        switch self {
        case .butt: return .butt
        case .round: return .round
        case .square: return .square
        }
    }
}

extension IconShape.Join {
    public var cgLineJoin: CGLineJoin {
        switch self {
        case .miter: return .miter
        case .round: return .round
        case .bevel: return .bevel
        }
    }
}
