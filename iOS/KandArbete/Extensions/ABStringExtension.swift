//
//  ABStringExtension.swift
//  KandArbete
//
//  Created by Albin Bååw on 2018-02-04.
//  Copyright © 2018 Albin Bååw. All rights reserved.
//

import UIKit

extension String {
	var localized: String {
		return NSLocalizedString(self, tableName: nil, bundle: Bundle.main, value: "", comment: "")
	}
	
	var urlFriendly: String{
		return self.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)!
	}
	
	func size(font: UIFont) -> CGSize {
		return self.size(withAttributes: [NSAttributedStringKey.font: font])
	}
}
