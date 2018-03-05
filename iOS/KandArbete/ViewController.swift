//
//  ViewController.swift
//  KandArbete
//
//  Created by Albin Bååw on 2018-01-30.
//  Copyright © 2018 Albin Bååw. All rights reserved.
//

import UIKit

class ViewController: UIViewController, DXPulseTrackerDelegate, DXSpotifyAdapterDelegate {
	
	internal var pulse = DXPulseTracker()
	internal var sa:DXSpotifyAdapter!
	
	var hrLabel:DXBeatingHeartView!
	var songLabel:DXSongLabelView!
	var playBtn:UIButton!
	var skipBtn:UIButton!
	var stopBtn:UIButton!
	
	override func viewDidLoad() {
		super.viewDidLoad()
		pulse.delegate = self
		
		pulse.requestAuthorization()
		
		sa = DXSpotifyAdapter(container: self)
		sa.delegate = self
		
		hrLabel = DXBeatingHeartView(frame: CGRect(x: self.view.frame.width - 30 - 50, y: 30, width: 50, height: 50))
		self.view.addSubview(hrLabel)
		
		songLabel = DXSongLabelView(frame: CGRect(x: 20, y: self.view.frame.height/2 - 50/2, width: self.view.frame.width - 2*20, height: 50))
		self.view.addSubview(songLabel)
		
		playBtn = UIButton(frame: CGRect(x: self.view.frame.width/2 - 100/2, y: self.view.frame.height - 20 - 100, width: 100, height: 100))
		playBtn.setImage(#imageLiteral(resourceName: "play-btn"), for: .normal)
		
		self.view.addSubview(playBtn)
		
		skipBtn = UIButton(frame: CGRect(x: playBtn.frame.origin.x + playBtn.frame.width + 20, y: playBtn.frame.origin.y + (playBtn.frame.height-75)/2, width: 75, height: 75))
		skipBtn.setImage(#imageLiteral(resourceName: "skip-btn"), for: .normal)
		
		self.view.addSubview(skipBtn)
		
		stopBtn = UIButton(frame: CGRect(x: playBtn.frame.origin.x - 20 - 75, y: playBtn.frame.origin.y + (playBtn.frame.height-75)/2, width: 75, height: 75))
		stopBtn.setImage(#imageLiteral(resourceName: "stop-btn"), for: .normal)
		
		self.view.addSubview(stopBtn)
		
		playBtn.addTarget(self, action: #selector(getSongFromServer), for: .touchUpInside)
		skipBtn.addTarget(self, action: #selector(skip), for: .touchUpInside)
		stopBtn.addTarget(self, action: #selector(stop), for: .touchUpInside)
	}

	override func didReceiveMemoryWarning() {
		super.didReceiveMemoryWarning()
		// Dispose of any resources that can be recreated.
	}
	
	@objc func start(){
		self.sa.playSong(trackid: "6nsLzJfvp5OLd4mgqUJkpq")
		self.pulse.startStreamingHeartRate()
	}
	
	@objc func stop(){
		DispatchQueue.main.async {
			self.sa.stopSong()
		}
	}
	
	@objc func skip(){
		DispatchQueue.main.async {
			self.sa.stopSong()
			self.getSongFromServer()
		}
	}
	
	@objc func getSongFromServer(){
		pulse.getLatestHeartRate(callback: {(heartRate, date) in
			self.requestNewSong(heartRate: heartRate)
			self.pulse.startStreamingHeartRate()
		})
		
		Timer.scheduledTimer(withTimeInterval: 1, repeats: true, block: { (timer) in
			self.updateLabels(heartRate: self.pulse.getAverageHeartRate(), date: Date())
		})
	}
	
	func updateLabels(heartRate:Double, date:Date){
		DispatchQueue.main.async {
			self.hrLabel.setText(text: "\(Int(heartRate))")
			//self.dateLabel.text = "\(date)"
		}
	}
	
	func updateLatestHeartRate(heartRate:Int, date: Date) {
		updateLabels(heartRate: Double(heartRate), date: date)
	}
	
	func songFinished(rating:Double) {
		let heartRate = pulse.getAverageHeartRate()
		let date = Date()
		self.sendUserData(heartRate: Int(heartRate), date: date, rating: rating)
		//self.requestNewSong(heartRate: Int(heartRate))
		self.updateLabels(heartRate: heartRate, date: date)
		
		pulse.clearAverageHeartRate()
		/*pulse.getLatestHeartRate(callback:{(heartRate, date) in
			self.sendUserData(heartRate: heartRate, date: date)
			self.requestNewSong(heartRate: heartRate)
			self.updateLabels(heartRate: heartRate, date: date)
		})*/
	}
	
	internal func sendUserData(heartRate: Int, date: Date, rating: Double){
		DXServerManager.sendUserData(userId: "testuser", trackId: self.sa.currentTrackId, heartRate: heartRate, time: "\(date)", rating: rating)
	}
	
	func requestNewSong(heartRate:Int){
		DXServerManager.retrieveNextTrackId(userId: "testuser", heartRate: heartRate, callback: {(trackId) in
			self.play(trackId: trackId)
		})
	}
	
	internal func play(trackId:String){
		self.sa.playSong(trackid: trackId)
	}
	
	func songStarted() {
		setSongLabels()
	}
	
	internal func setSongLabels(){
		DispatchQueue.main.async {
			self.songLabel.setArtist(artist: self.sa.getSongArtist())
			self.songLabel.setSong(song: self.sa.getSongName())
		}
	}

}

