// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "SampleSwift",
    targets: [
        .target(name: "SampleSwift", path: "Sources"),
        .testTarget(name: "SampleSwiftTests", dependencies: ["SampleSwift"], path: "Tests"),
    ]
)
