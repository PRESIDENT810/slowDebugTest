import os
import shutil
import argparse
from string import ascii_uppercase as ABC

parser = argparse.ArgumentParser(description='Create stub frameworks for iOS/macOS platform')
parser.add_argument('--sdk', dest='sdk', default='iphonesimulator',
                    help='specify SDK, like iphonesimulator or macosx. Defaults to iphonesimulator')
parser.add_argument('--configuration', dest='configuration', default='Debug',
                    help='specify configuration, like Debug or Release. Defaults to Debug')
parser.add_argument('--objc', dest = 'objc', action='store_true',default=False,
                    help='generate Objective-C stub framework, default generate Swift framework')
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
objc = args.objc

if objc:
    print("Generate Objective-C sources")
else:
    print("Generate Swift sources")

def generate_objc_sources(module_name, source_index, source_dir):
    # 2.1 Create stub source files
    header_content ="""
#import <Foundation/Foundation.h>

@interface %s%d : NSObject

@property NSString *name;

@end

""" % (module_name, source_index)
    header_name = module_name + str(source_index) + ".h"

    with open(os.path.join(source_dir, header_name), "w") as f:
        f.write(header_content)
    # 1 Create stub header files
    source_content ="""
#import "%s%d.h"

@implementation %s%d

@end

""" % (module_name, source_index, module_name, source_index)
    source_name = module_name + str(source_index) + ".m"
    # 2. Create stub source files
    with open(os.path.join(source_dir, source_name), "w") as f:
        f.write(source_content)
    # 3. Create stub include folder
    include_dir = os.path.join(source_dir, 'include')
    os.makedirs(include_dir, exist_ok=True)
    os.symlink(os.path.join('../', header_name), os.path.join(include_dir, header_name))

def generate_swift_sources(module_name, source_index, source_dir):
    # 1. Create stub swift source files
    source_content ="""
public class %s%d {
    public init() {
    }
}
""" % (module_name, source_index)
    source_name = module_name + str(source_index) + ".swift"
    with open(os.path.join(source_dir, source_name), "w") as f:
        f.write(source_content)
    # 2. Create stub swift main file
    main_source_content ="""
public class %s {
    public init() {
    }
}
""" % (module_name)
    main_source_name = module_name + ".swift"
    with open(os.path.join(source_dir, main_source_name), "w") as f:
        f.write(main_source_content)


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
        shutil.rmtree(source_dir, ignore_errors=True)
        os.makedirs(source_dir, exist_ok=True)

        # 2. Create stub source files, each module contains large number of files
        for source_index in range(module_limit):
            if objc:
                generate_objc_sources(module_name, source_index, source_dir)
            else:
                generate_swift_sources(module_name, source_index, source_dir)

# 3. Generate client source code
source_code_name = "StubFrameworks.swift"
print("Genrating client source code to %s..." % (source_code_name))

source_code = ""
for module_name in module_names:
    source_code += "import %s\n" % (module_name)
source_code += "\n"
source_code += "public func testStubFrameworks() {\n"
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
