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
    ],
    targets: [
        .target(name: "SymbioticTokens"),
        .testTarget(name: "SymbioticTokensTests", dependencies: ["SymbioticTokens"]),
    ]
)
