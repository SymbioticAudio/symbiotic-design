// MIT licence: see LICENSE.
import AppKit
import Testing
import SymbioticTokens
@testable import SymbioticIcons

/// A provider that maps every role but has nothing to draw (e.g. absent glyph data).
private struct EmptyDrawingProvider: IconProvider {
    func drawing(for role: IconRole) -> IconDrawing? { IconDrawing(shapes: []) }
}

/// Draws `image` into a `side` x `side` pixel bitmap at 1x and returns its alpha mask.
private func drawnMask(_ image: NSImage, side: Int, flipped: Bool = false) -> [UInt8] {
    let context = CGContext(data: nil, width: side, height: side, bitsPerComponent: 8, bytesPerRow: 0,
                            space: CGColorSpace(name: CGColorSpace.sRGB)!,
                            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(cgContext: context, flipped: flipped)
    if flipped {
        // Make the context's y axis point down, as a flipped view's does.
        context.translateBy(x: 0, y: CGFloat(side))
        context.scaleBy(x: 1, y: -1)
    }
    image.draw(in: NSRect(x: 0, y: 0, width: side, height: side))
    NSGraphicsContext.restoreGraphicsState()
    return IconBitmap.alpha(of: context.makeImage()!)
}

@Suite struct CacheAndImageTests {
    // Ink paths are built once per (drawing, size, stroke).

    @Test func inkPathsAreCachedPerDrawingSizeAndStroke() {
        let drawing = StandardIcon.fadeIn.drawing
        let first = drawing.inkPaths(size: 48, strokeWidth: 2.4)
        let again = drawing.inkPaths(size: 48, strokeWidth: 2.4)
        #expect(!first.isEmpty)
        #expect(first.count == again.count)
        #expect(zip(first, again).allSatisfy { $0 === $1 })
        let other = drawing.inkPaths(size: 48, strokeWidth: 3)
        #expect(!(other.first! === first.first!))
    }

    @Test func inkCacheIsBounded() {
        let cache = InkCache(limit: 8)
        let drawing = StandardIcon.stop.drawing
        for i in 0..<20 {
            _ = cache.paths(for: drawing, size: 24, strokeWidth: 1 + CGFloat(i) / 10)
            #expect(cache.count <= 8)
        }
        #expect(cache.count >= 1)
    }

    @Test func inkCacheIsSafeUnderConcurrentUse() async {
        let cache = InkCache(limit: 64)
        let drawings = StandardIcon.allCases.prefix(16).map(\.drawing)
        let counts = await withTaskGroup(of: Int.self) { group in
            for i in 0..<200 {
                group.addTask { cache.paths(for: drawings[i % 16], size: 24, strokeWidth: 1.2).count }
            }
            var all: [Int] = []
            for await n in group { all.append(n) }
            return all
        }
        #expect(counts.count == 200)
        #expect(counts.allSatisfy { $0 > 0 })
        #expect(cache.count == 16)
    }

    // An empty drawing from a provider counts as "not provided".

    @Test func emptyProviderDrawingFallsBack() {
        let resolver = IconResolver(provider: EmptyDrawingProvider())
        #expect(resolver.resolve(.transportStop) == .drawing(StandardIcon.stop.drawing))
        #expect(resolver.resolve(.brandLogo) == .wordmark(Icons.wordmark))
    }

    // The image honours the rect it is drawn into; the stroke stays the requested size's.

    @Test func imageDrawnIntoALargerRectKeepsItsStroke() {
        let image = NSImage.icon(.transportStop, size: 16, theme: .classicLight, resolver: IconResolver(provider: nil))
        let drawn = drawnMask(image, side: 64)
        let stroke16 = Theme.classicLight.iconStroke.width(forSize: 16)
        let kept = IconBitmap.alpha(of: StandardIcon.stop.drawing, size: 64, strokeWidth: stroke16)
        let fattened = IconBitmap.alpha(of: StandardIcon.stop.drawing, size: 64, strokeWidth: stroke16 * 4)
        #expect(IconBitmap.meanDifference(drawn, kept) < 0.02)
        #expect(IconBitmap.meanDifference(drawn, fattened) > 0.05)
    }

    @Test func resizedImageKeepsItsStroke() {
        let image = NSImage.icon(.transportStop, size: 16, theme: .classicLight, resolver: IconResolver(provider: nil))
        image.size = NSSize(width: 32, height: 32)
        var rect = NSRect(x: 0, y: 0, width: 32, height: 32)
        let cg = image.cgImage(forProposedRect: &rect, context: nil, hints: nil)!
        let scale = CGFloat(cg.width) / 32
        let stroke16 = Theme.classicLight.iconStroke.width(forSize: 16)
        let kept = IconBitmap.alpha(of: StandardIcon.stop.drawing, size: cg.width, strokeWidth: stroke16 * scale)
        let fattened = IconBitmap.alpha(of: StandardIcon.stop.drawing, size: cg.width, strokeWidth: stroke16 * 2 * scale)
        let fromImage = IconBitmap.alpha(of: cg)
        #expect(IconBitmap.meanDifference(fromImage, kept) < 0.02)
        #expect(IconBitmap.meanDifference(fromImage, fattened) > 0.05)
    }

    // Copies of an image and of its representation own their drawing: freeing
    // the originals and then the copies must not over-release it.

    @Test func copiedImageAndRepresentationSurviveTheOriginals() {
        let resolver = IconResolver(provider: nil)
        let expected = IconBitmap.alpha(of: StandardIcon.stop.drawing, size: 32,
                                        strokeWidth: Theme.classicLight.iconStroke.width(forSize: 32))
        for _ in 0..<3 {
            var imageCopy: NSImage?
            var repCopy: NSImageRep?
            autoreleasepool {
                let image = NSImage.icon(.transportStop, size: 32, theme: .classicLight, resolver: resolver)
                imageCopy = image.copy() as? NSImage
                repCopy = image.representations.first?.copy() as? NSImageRep
            }
            #expect(imageCopy != nil)
            #expect(repCopy is IconImageRep)
            #expect(repCopy?.size == NSSize(width: 32, height: 32))
            autoreleasepool {
                #expect(IconBitmap.meanDifference(drawnMask(imageCopy!, side: 32), expected) < 0.02)
                let fromRep = NSImage(size: NSSize(width: 32, height: 32))
                fromRep.addRepresentation(repCopy!)
                #expect(IconBitmap.meanDifference(drawnMask(fromRep, side: 32), expected) < 0.02)
                #expect(IconBitmap.meanDifference(drawnMask(imageCopy!, side: 32, flipped: true), expected) < 0.02)
            }
            autoreleasepool {
                imageCopy = nil
                repCopy = nil
            }
        }
    }
}
