// SymbioticAudio branded artwork: see ASSETS-LICENSE. All rights reserved.
import Testing
@testable import SymbioticIcons
@testable import SymbioticBrand

@Suite struct BrandTests {
    let branded = IconResolver(provider: SymbioticBrand.provider)

    @Test func mappedRolesDrawTheirGlyphs() {
        #expect(branded.resolve(.modeLoop) == .drawing(BrandGlyph.glyph40.drawing))
        #expect(branded.resolve(.editorEnvelope) == .drawing(BrandGlyph.glyph05.drawing))
        #expect(branded.resolve(.brandLogo) == .drawing(BrandGlyph.glyph39.drawing))
        #expect(branded.resolve(.transportPlay) == .drawing(StandardIcon.play.drawing))
    }

    @Test func exactlyTheTwelveConfirmedGlyphsAreMapped() {
        let mapped = Set(IconRole.allCases.compactMap { BrandGlyph.forRole($0) })
        #expect(mapped.count == 12)
        #expect(!mapped.contains(.glyph27))
        #expect(BrandGlyph.allCases.count == 41)
    }

    /// The only test that touches the app-wide registry, so parallel tests never see it change.
    @Test func registeringTheProviderSwitchesTheAppWideResolver() {
        Icons.unregister()
        #expect(Icons.resolver.resolve(.modeLoop) == .drawing(StandardIcon.loop.drawing))
        #expect(Icons.resolver.resolve(.brandLogo) == .wordmark("SymbioticAudio"))
        Icons.register(SymbioticBrand.provider)
        #expect(Icons.resolver.resolve(.modeLoop) == .drawing(BrandGlyph.glyph40.drawing))
        Icons.unregister()
        #expect(Icons.resolver.resolve(.modeLoop) == .drawing(StandardIcon.loop.drawing))
    }
}
