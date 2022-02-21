//
//  ViewController.swift
//  slowDebugTestMac
//
//  Created by 李卓立 on 2022/2/18.
//

import Cocoa

class ViewController: NSViewController {
  
    static var preLoadDataBufferTime: TimeInterval = 0.1

    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        testStubFrameworks()
    }

    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }


}

