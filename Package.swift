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
        .library(name: "SymbioticBrand", targets: ["SymbioticBrand"]),
    ],
    targets: [
        .target(name: "SymbioticTokens"),
        .target(name: "SymbioticIcons", dependencies: ["SymbioticTokens"]),
        .target(name: "SymbioticBrand", dependencies: ["SymbioticIcons"]),
        .testTarget(name: "SymbioticTokensTests", dependencies: ["SymbioticTokens"]),
        .testTarget(name: "SymbioticIconsTests", dependencies: ["SymbioticIcons", "SymbioticTokens"], exclude: ["References"]),
        .testTarget(name: "SymbioticBrandTests", dependencies: ["SymbioticBrand", "SymbioticIcons", "SymbioticTokens"], exclude: ["References"]),
    ]
)
