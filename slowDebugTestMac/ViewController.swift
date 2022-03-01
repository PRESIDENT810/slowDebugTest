//
//  ViewController.swift
//  slowDebugTestMac
//
//  Created by 李卓立 on 2022/2/18.
//

import Cocoa

class ViewController: NSViewController {
    var testBuffer: TimeInterval = 0.2
    static var preLoadDataBufferTime: TimeInterval = 0.1

    override func viewDidLoad() {
        super.viewDidLoad()
      
        let p = OCPerson()
        print(p.name)

        // Do any additional setup after loading the view.
        testStubFrameworks()
    }

    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }


}

