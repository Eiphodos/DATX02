//
//  DXSongLabelView.swift
//  KandArbete
//
//  Created by Albin Bååw on 2018-02-26.
//  Copyright © 2018 Albin Bååw. All rights reserved.
//

import UIKit

class DXSongLabelView: UIView {
	
	internal var song:UILabel!
	internal var artist:UILabel!
	
	override init(frame: CGRect) {
		super.init(frame: frame)
		
		var font = UIFont.systemFont(ofSize: 36, weight: .semibold)
		
		var size = "000".size(font: font)
		
		song = UILabel(frame: CGRect(x: 0, y: 0, width: frame.width, height: size.height))
		song.textAlignment = .center
		song.font = font
		
		self.addSubview(song)
		
		font = UIFont.systemFont(ofSize: 18, weight: .medium)
		
		size = "000".size(font: font)
		
		artist = UILabel(frame: CGRect(x: 0, y: song.frame.height, width: frame.width, height: size.height))
		artist.textAlignment = .center
		artist.font = font
		
		self.addSubview(artist)
	}
	
	required init?(coder aDecoder: NSCoder) {
		fatalError("init(coder:) has not been implemented")
	}
	
	func setSong(song:String?){
		self.song.text = song
	}
	
	func setArtist(artist:String?){
		self.artist.text = artist
	}

}
