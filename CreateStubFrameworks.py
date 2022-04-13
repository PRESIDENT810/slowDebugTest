import os
import argparse
from string import ascii_uppercase as ABC

parser = argparse.ArgumentParser(description='Create stub frameworks for iOS/macOS platform')
parser.add_argument('--sdk', dest='sdk', default='iphonesimulator',
                    help='specify SDK, like iphonesimulator or macosx. Defaults to iphonesimulator')
parser.add_argument('--configuration', dest='configuration', default='Debug',
                    help='specify configuration, like Debug or Release. Defaults to Debug')
args = parser.parse_args()


sdk = args.sdk
configuration = args.configuration
if sdk == 'iphonesimulator':
    archs = 'x86_64'
elif sdk == 'macosx':
    archs = 'x86_64'
elif sdk == 'iphoneos':
    archs = 'arm64'
else:
    raise Exception("Unsupported sdk %s, update the script" % (sdk))

module_names = []
limit = 100
module_limit = 200
for c1 in ABC:
    for c2 in ABC:
        if limit <= 0:
            break
        limit -= 1
        module_name = c1 + c2 + "Stub"
        module_names.append(module_name)
        source_dir = os.path.join("Sources", module_name)

        # 1. Create stub source folder
        print("Genrating %s module and source files..." % (module_name))
        os.makedirs(source_dir, exist_ok=True)

        # 2. Create stub source files, each module contains large number of files
        for i in range(module_limit):
            source_content ="""
import Foundation
import UIKit
import CoreText
import CoreML
import CoreNFC
import CoreData
import CoreAudio
import CoreImage
import CoreMotion
import CoreServices
import CoreFoundation
import CoreAudioKit
import CoreSpotlight
import CoreMedia
import CoreBluetooth
import CoreLocation
import ObjectiveC
import Darwin
import OpenAL
import OpenGLES
import QuartzCore
import AVFAudio
import CoreMIDI
import CoreVideo
import CoreHaptics
import CoreGraphics
import CoreTelephony
import CoreAudioTypes
import JavaScriptCore
import MobileCoreServices
import SwiftUI
import WebKit
import WidgetKit
import Network
import PhotosUI
import Metal
import MusicKit
import MessageUI
import MediaPlayer
import MapKit
import MetalKit
import MediaToolbox
import Messages
import ShazamKit
import LinkPresentation
import LocalAuthentication
import SQLite3
import libxml2
import NetworkExtension
import networkext
import SceneKit
import ARKit
import AVKit
import GLKit
import GameKit
import HomeKit
import CloudKit
import CryptoKit
import SensorKit
import HealthKit

public class %s%d {
    public var _outOfRangeText: NSAttributedString?
    public var defaultFont: UIFont
    public var var1: UIView
    public var var2: UILabel
    public var var3: UIButton
    public var var4: UIColor

    public init() {
        let SYSTEM_FONT = UIFont.systemFont(ofSize: UIFont.systemFontSize)
        self._outOfRangeText = NSAttributedString()
        self.defaultFont = SYSTEM_FONT
        self.var1 = UIView()
        self.var2 = UILabel()
        self.var3 = UIButton()
        self.var4 = UIColor()
    }
}
""" % (module_name, i)
            source_name = module_name + str(i) + ".swift"
            with open(os.path.join(source_dir, source_name), "w") as f:
                f.write(source_content)

        main_source_content ="""
public class %s {
    public init() {
    }
}
""" % (module_name)
        main_source_name = module_name + ".swift"
        with open(os.path.join(source_dir, main_source_name), "w") as f:
            f.write(main_source_content)

# 3. Generate client source code
source_code_name = "StubFrameworks.swift"
print("Genrating client source code to %s..." % (source_code_name))

source_code = ""
for module_name in module_names:
    source_code += "import %s\n" % (module_name)
source_code += "\n"
source_code += "public func testStubFrameworks() {\n"
source_code += "    let temp = AAStub0()\n"
for module_name in module_names:
    source_code += "    let _ = %s()\n" % (module_name)
    for i in range(module_limit):
        source_code += "    let _ = %s%d()\n" % (module_name, i)
source_code += "}"
with open(source_code_name, "w") as source_f:
    source_f.write(source_code)

# 4. SwiftPM generate Xcodeproj
xcodeproj_path = "StubFrameworks.xcodeproj"
print("Genrating xcode project to %s..." % (xcodeproj_path))

os.system("swift package generate-xcodeproj")

# 5. Create xcconfig, setting to static framework and long search path
xcconfig_path = "StubFrameworks.xcconfig"
with open(xcconfig_path, "w") as f:
    framework_search_paths = list(map(lambda x : "/path/not/found/%s" % (x), module_names))
    f.write("MACH_O_TYPE = staticlib\n")
    f.write("VALID_ARCHS = %s\n" % (archs)) # I'm not testing M1 Mac :)
    f.write("FRAMEWORK_SEARCH_PATHS = ")
    for module_name in module_names:
        for i in range(10):
            f.write("/path/not/found/%s/%d " % (module_name, i))

# 6. Xcodebuild build framework
cmd = "xcodebuild build -project %s -xcconfig %s -configuration %s -sdk %s " % (xcodeproj_path, xcconfig_path, configuration, sdk)
for module_name in module_names:
    cmd += " -target %s" % (module_name)
print("Building frameworks...")
print(cmd)
os.system(cmd)
