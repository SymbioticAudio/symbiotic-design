// MIT licence: see LICENSE.
import Testing
@testable import SymbioticIcons

private struct OneRoleProvider: IconProvider {
    let role: IconRole
    let drawing: IconDrawing
    func drawing(for role: IconRole) -> IconDrawing? { role == self.role ? drawing : nil }
}

@Suite struct RoleTests {
    let plain = IconResolver(provider: nil)

    @Test func rolesAreTypedByTheirDottedID() {
        #expect(IconRole(rawValue: "transport.play") == .transportPlay)
        #expect(IconRole.modeLoop.rawValue == "mode.loop")
        #expect(IconRole.transportPlay.label == "Play")
        #expect(IconRole(rawValue: "transport.plya") == nil)
    }

    @Test(arguments: IconRole.allCases.filter { $0 != .brandLogo }.map(\.rawValue))
    func everyRoleDrawsItsStandardIconWithoutAProvider(id: String) throws {
        let role = try #require(IconRole(rawValue: id))
        let standard = try #require(role.standard)
        #expect(plain.resolve(role) == .drawing(standard.drawing))
        #expect(!role.label.isEmpty)
    }

    @Test func logoWithoutProviderIsTheWordmark() {
        #expect(IconRole.brandLogo.standard == nil)
        #expect(plain.resolve(.brandLogo) == .wordmark("SymbioticAudio"))
    }

    @Test func providerOverridesOnlyTheRolesItMaps() {
        let custom = IconDrawing(shapes: [IconShape(paint: .stroke, weight: 1, cap: .butt, join: .miter,
                                                    ops: [.move(2, 2), .line(22, 22)])])
        let resolver = IconResolver(provider: OneRoleProvider(role: .transportStop, drawing: custom))
        #expect(resolver.resolve(.transportStop) == .drawing(custom))
        #expect(resolver.resolve(.transportPlay) == .drawing(StandardIcon.play.drawing))
        #expect(resolver.resolve(.brandLogo) == .wordmark(Icons.wordmark))
    }

    @Test(arguments: StandardIcon.allCases.map(\.rawValue))
    func everyStandardIconHasInk(name: String) throws {
        let icon = try #require(StandardIcon(rawValue: name))
        #expect(!icon.drawing.shapes.isEmpty)
        let mask = IconBitmap.alpha(of: icon.drawing, size: 24, strokeWidth: 1.2)
        #expect(mask.contains { $0 > 128 })
    }
}
