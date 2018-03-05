//
//  DXBeatingHeartView.swift
//  KandArbete
//
//  Created by Albin Bååw on 2018-02-26.
//  Copyright © 2018 Albin Bååw. All rights reserved.
//

import UIKit

class DXBeatingHeartView: UIView {

    /*
    // Only override draw() if you perform custom drawing.
    // An empty implementation adversely affects performance during animation.
    override func draw(_ rect: CGRect) {
        // Drawing code
    }
    */
	
	internal var image:UIImageView!
	internal var label:UILabel!
	
	override init(frame: CGRect) {
		super.init(frame: frame)
		
		image = UIImageView(frame: CGRect(x: 0, y: 0, width: self.frame.width, height: self.frame.height))
		image.image = #imageLiteral(resourceName: "heart-btn")
		
		self.addSubview(image)
		
		label = UILabel(frame: CGRect(x: 0, y: self.frame.height/2 - 12, width: self.frame.width, height: 20))
		label.textColor = .white
		label.textAlignment = .center
		
		self.addSubview(label)
		
		animate()
	}
	
	required init?(coder aDecoder: NSCoder) {
		fatalError("init(coder:) has not been implemented")
	}
	
	func setText(text:String){
		self.label.text = text
	}
	
	internal func animate(){
		UIView.animate(withDuration: 1.5, animations: {
			self.image.transform = self.image.transform.scaledBy(x: 1.25, y: 1.25)
		}) { (bool) in
			UIView.animate(withDuration: 1.5, animations: {
				self.image.transform = self.image.transform.scaledBy(x: 0.8, y: 0.8)
			}) { (bool) in
				self.animate()
			}
		}
	}

}
