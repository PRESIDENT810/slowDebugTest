//
//  ViewController.swift
//  slowDebugTest
//
//  Created by ByteDance on 2022/2/10.
//

import UIKit
import SnapKit

class ViewController: UIViewController {
    lazy var box = UIView()

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        
        sleep(10) // wait so I have time to let debugger attach to process lldb-rpc-server
        
        // Stub Frameworks break point
        testStubFrameworks()
        
        self.view.addSubview(box)
        box.backgroundColor = .green
        box.snp.makeConstraints { (make) -> Void in
           make.width.height.equalTo(50)
           make.center.equalTo(self.view)
        }
    }
}

