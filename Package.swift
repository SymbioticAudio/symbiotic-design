// swift-tools-version: 6.0
// MIT licence: see LICENSE.
import PackageDescription

/// The one place the deployment floor is set (spec section 4).
let minimumMacOS: SupportedPlatform = .macOS(.v14)

let package = Package(
    name: "symbiotic-design",
    platforms: [minimumMacOS],
    products: [
        .library(name: "SymbioticTokens", targets: ["SymbioticTokens"]),
        .library(name: "SymbioticIcons", targets: ["SymbioticIcons"]),
    ],
    targets: [
        .target(name: "SymbioticTokens"),
        .target(name: "SymbioticIcons", dependencies: ["SymbioticTokens"]),
        .testTarget(name: "SymbioticTokensTests", dependencies: ["SymbioticTokens"]),
        .testTarget(name: "SymbioticIconsTests", dependencies: ["SymbioticIcons", "SymbioticTokens"]),
    ]
)
