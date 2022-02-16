# sloweDebugTest

This project aims to reproduce a scenario that when using static frameworks (frameworks that are just archives), it is notably slow to debug in Xcode.

## Overview

This project itself is a very simple iOS swift project, and it uses a static framework "SnapKit".
When building SnapKit, I added about 1000 framework search paths, and they are mostly paths on a remote build machine.
This is because in my project, there are about 1000 Pods used, and they are also static frameworks built on a remote machine.
These framework search paths appear to be like this:
`/Users/remote/Jenkins/workspace/lark/ios/binary/Pods/Build/Products/Release-iphonesimulator/LarkPerf-Frameworks` (which is apparently not a valid path on my local machine).

For these pods, their framework search paths add up to about 1000, so to simulate this, I manually added these paths when I was building SnapKit in this project. One can easily check this using `llvm-bcanalyzer ../slowDebugTest/SnapKit.framework/Modules/SnapKit.swiftmodule/x86_64-apple-ios-simulator.swiftmodule --dump`.


## How to run this demo and generate stub frameworks

```bash
python3 CreateStubFrameworks.py
```

This will create static frameworks `AA.framework AB.framework ... ZZ.framework`

each of framework contains one swift source file `AA.swift` like this:

```swift
public class AA {
	public init() {

	}
}
```

and also 200 swift source files `AA0.swift AA2.swift ... AA199.swift` like this:

```swift
public struct AA1 {
	public init() {

	}
}
```

And a generated `StubFrameworks.swift` source code, which looks like:

```swift
import AA
import AB
//...
import ZZ

public func testStubFrameworks() {
	let _ = AA()
	let _ = AB()
	//...
	let _ = ZZ()
}
```

then, import these stub frameworks and types from iOS Application's `ViewController.swift`, build the iOS App target to attach the debugger to see the slow debugger experience.


## What this project aims to reproduce

As I mentioned, I have a huge iOS project (Lark), which is very slow to debug in Xcode. As I set a breakpoint and start debugging, it takes about 100s to show variables in Xcode after this breakpoint is hit. By `log timers dump` command in LLDB, I can ascertain the problem occurs in `SwiftASTContext::LoadModule`:

```
(lldb) log timers dump
84.697079116 sec (total: 86.018s; child: 1.321s; count: 246) for void lldb_private::SwiftASTContext::LoadModule(swift::ModuleDecl *, lldb_private::Process &, lldb_private::Status &)
45.275086790 sec (total: 45.602s; child: 0.327s; count: 740) for size_t ObjectFileMachO::ParseSymtab()
30.420983273 sec (total: 72.596s; child: 42.175s; count: 706) for static lldb::TypeSystemSP lldb_private::SwiftASTContext::CreateInstance(lldb::LanguageType, lldb_private::Module &, lldb_private::Target *, bool)
17.402660895 sec (total: 17.403s; child: 0.000s; count: 24093) for lldb_private::FileSpec LocateExecutableSymbolFileDsym(const lldb_private::ModuleSpec &)
16.910604685 sec (total: 16.911s; child: 0.000s; count: 737) for void lldb_private::Symtab::InitNameIndexes()
12.938461787 sec (total: 12.938s; child: 0.000s; count: 126) for swift::ModuleDecl *lldb_private::SwiftASTContext::GetModule(const lldb_private::SourceModule &, lldb_private::Status &)
```

This function uses a lambda function `addLinkLibrary` to load all imported modules, and in this lambda function, 
it first determines whether this module is a framework or a library. For framework, it tries to load it using `@rpath`, framework search paths, and `/System/Library/Frameworks/`. I added a llvm::Timer() to measure time used in this phase, and here is my result:
- Time used for loading framework using `@rpath`: about 0.06s on average
- Time used for loading framework using framework search paths: about 0.6s on average
- Time used for loading framework using `/System/Library/Frameworks/`: about 0.06s on average
- Time used for loading library using library search paths: about 0.00s on averayge (My precision is set to two digits after decimal point...)

The reason why it takes so long to load using framework search paths is because I have about 1000 framework search paths, and in the end, `PlatformPOSIX::DoLoadImage` will be invoked to try to load the framework using these paths. `PlatformPOSIX::DoLoadImage` appears to use JIT to compile some pre-defined codes that wrap `dlopen function` **in the process that is being debugged**.

In Lark, there are 118 modules go into this `LoadModule` function, and each time LLDB tries to load modules using this function, it takes
0.06+0.6+0.06=0.7s, so for these 118 modules, the total amount of time cost by `LoadModule` is about 80s, which matches the result of `log timers dump` commabd shown above.

## How this project reproduce this problem

According to my observation, `PlatformPOSIX::DoLoadImage` always ends up with a dlopen error (because you can't just dlopen an "archive"!). You can see this problem in this test project too.

Therefore, to reproduce this problem in this test project, I compiled a static framework (SnapKit, which is available on GitHub), and used it in ViewController.swift.

Before I start debugging, I set a breakpoint at ViewController:24. I also built a Xcode toolchain myself so I can debug into LLDB and see what happens.

As my breakpoint is hit, LLDB goes into `LoadModule` function and this is the result I have for adding llvm::Timer() in `LoadModule`:
- Time used for loading framework using `@rpath`: about 0.09s on average
- Time used for loading framework using framework search paths: about 0.2s on average
- Time used for loading framework using `/System/Library/Frameworks/`: about 0.01s on average

Not sure why loading framework using framework search paths takes less time than in Lark though, maybe it's because the overall size of this test project is far smaller than Lark? I wonder. However I think this is enough to reproduce the problem I encountered in Lark, since dlopen error also occurs when LLDB trying to load SnapKit in this test project.

## Possible solutions I can come up with

For expedients, I think I can just add some code that determines whether a framework search path exists (if this path is some path on remote machine that is not available on my local machine, then we don't need to go for it), and if it exists, determine whether it is an arvhice by reading the file header; if it is, then we don't search this path, either, because it's bound to fail to dlopen an archive.
In addition, I don't think this will affect other parts of LLDB, because it fails to load static frameworks anyway, adding this logic simply makes it faster to fail by skiping unnecessary dlopen steps.

However I think the best solution is to add logic so `LoadModule` can load a static framework as a library, not sure how to implement it though.

## Questions

Why failure to load static frameworks seem to have no impact to debugging? Even though I get dlopen errors, in Xcode I have my variables shown normally, and I can also use LLDB commands like `p` or `po`. Not sure why is that.
I even tried to make `LoadModule` return immediately without doing anythings, and it is still OK to debug. Interesting.