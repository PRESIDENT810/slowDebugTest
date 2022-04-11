//
//  ViewController.swift
//  slowDebugTestMac
//
//  Created by 李卓立 on 2022/2/18.
//

import Cocoa
import CoreGraphics

class ViewController: NSViewController {
    var testBuffer: TimeInterval = 0.2
    static var preLoadDataBufferTime: TimeInterval = 0.1
    public private(set) var ctframeSetter: CTFramesetter?
    public private(set) var ctframe: CTFrame?

    override func viewDidLoad() {
        super.viewDidLoad()
      
        sleep(10)
      
        let p = OCPerson()
        print(p.name)
        
        testCTType()

        // Do any additional setup after loading the view.
        testStubFrameworks()
    }
    
    
    func testCTType() {
        let attrText = NSAttributedString(string: "abc")
        let CFRANGE_ZERO = CFRangeMake(0, 0)
        self.ctframeSetter = CTFramesetterCreateWithAttributedString(attrText)
        let path = CGPath(rect: CGRect(x: 0, y: 0, width: 100, height: 100), transform: nil)
        self.ctframe = CTFramesetterCreateFrame(self.ctframeSetter!, CFRANGE_ZERO, path, nil)
        let ctLines = CTFrameGetLines(self.ctframe!)
        var linesCount = CFArrayGetCount(ctLines)
        let originLinesCount = linesCount
    }

    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }


}

