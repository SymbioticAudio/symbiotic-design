// SymbioticAudio branded artwork
// Copyright (c) 2006-2026 Westlee Latta. All rights reserved.
//
// The following files are proprietary artwork and brand identity of
// SymbioticAudio. They are NOT licensed under the MIT licence in LICENSE, nor
// under any open-source licence of an application that uses them (including
// VizDAW and EG13, which are GPL-3.0):
//
//   - source-art/          (master artwork, Photoshop files)
//   - icons/svg/glyph-*    (glyph icons redrawn from the master artwork)
//   - icons/glyphs.json    (descriptions and the designer's names of the glyphs)
//   - icons/coverage.md    (generated report that describes the glyphs; the
//     whole file, including its rows for standard icons)
//   - icons/contact-sheet.html (embeds the glyph artwork; its glyph section
//     remains all rights reserved)
//   - Sources/SymbioticBrand/ (the glyphs as Swift drawing code, generated and
//     hand-written)
//   - Tests/SymbioticBrandTests/ (brand tests and glyph reference PNGs, when
//     added)
//   - logo/                (SymbioticAudio logo, when added)
//   - any PDF, PNG or other rendering generated from the files above
//
// Not covered by this file: the standard icon set in icons/standard/ (and
// icons/standard.json), which is MIT-licensed under LICENSE. The contact sheet
// also shows those standard icons; that section is MIT, the glyph section is not.
//
// No permission is granted to copy, modify, distribute or use this artwork,
// in whole or in part, except in official SymbioticAudio releases or with the
// copyright holder's prior written permission. Forks and redistributions of
// SymbioticAudio's open-source applications must remove this artwork and use
// their own or the applications' fallback icons.
//
// Contact: symbioticaudio@proton.me

import CoreGraphics
import Foundation
import ImageIO
import Testing
import SymbioticTokens
@testable import SymbioticIcons
@testable import SymbioticBrand

/// Every brand glyph drawn by the generated code at 48 px matches the
/// headless-Chrome render of its SVG (tools/references.py).
@Suite struct BrandFidelityTests {
    /// Same tolerances as the standard icons (FidelityTests.tolerance and
    /// FidelityTests.pixelTolerance).
    static let tolerance = 0.02
    static let pixelTolerance = 0.5

    @Test(arguments: BrandGlyph.allCases.map(\.rawValue))
    func glyphMatchesReference(id: String) throws {
        let glyph = try #require(BrandGlyph(rawValue: id))
        let url = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
            .appendingPathComponent("References/\(id).png")
        let source = try #require(CGImageSourceCreateWithURL(url as CFURL, nil), "missing \(url.path)")
        let image = try #require(CGImageSourceCreateImageAtIndex(source, 0, nil))
        let stroke = Theme.classicLight.iconStroke.width(forSize: 48)
        let ours = IconBitmap.alpha(of: glyph.drawing, size: 48, strokeWidth: stroke)
        let reference = IconBitmap.alpha(of: image)
        let diff = IconBitmap.meanDifference(ours, reference)
        let worst = IconBitmap.maxDifference(ours, reference)
        #expect(diff < Self.tolerance, "\(id): mean difference \(diff)")
        #expect(worst < Self.pixelTolerance, "\(id): largest pixel difference \(worst)")
    }
}
