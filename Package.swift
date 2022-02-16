// swift-tools-version:5.5
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription
import Foundation

var limit = 100
var moduleNames: [String] = [] // module name from AA AB ... YZ ZZ
for c1 in Unicode.Scalar("A").value...Unicode.Scalar("Z").value {
    for c2 in Unicode.Scalar("A").value...Unicode.Scalar("Z").value {
        if limit <= 0 {
            break
        }
        limit -= 1
        let charView = String.UnicodeScalarView([Unicode.Scalar(c1)!, Unicode.Scalar(c2)!])
        let moduleName = String(charView)
        moduleNames.append(moduleName)
    }
}

let targets = moduleNames.map { Target.target(name: $0, dependencies: [], path: "Sources/" + $0) }

let package = Package(
    name: "StubFrameworks",
    products: [
        // Products define the executables and libraries a package produces, and make them visible to other packages.
        .library(
            name: "StubFrameworks",
            targets: moduleNames),
    ],
    dependencies: [
        // Dependencies declare other packages that this package depends on.
        // .package(url: /* package url */, from: "1.0.0"),
    ],
    targets: targets
)
