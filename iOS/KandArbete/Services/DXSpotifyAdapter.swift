//
//  DXSpotifyAdapter.swift
//  KandArbete
//
//  Created by Albin Bååw on 2018-02-04.
//  Copyright © 2018 Albin Bååw. All rights reserved.
//

import UIKit
import SafariServices

protocol DXSpotifyAdapterDelegate {
	func songFinished(rating:Double)
	func songStarted()
}

class DXSpotifyAdapter: NSObject, SPTAudioStreamingDelegate, SPTAudioStreamingPlaybackDelegate {
	internal let clientId:String = "c68865ecf9cd42c6b7eea8100ee83dc9"
	internal let clientSecret:String = "be0b1cc741864d15a11a24d12ed02306"
	
	internal var auth:SPTAuth!
	internal var player:SPTAudioStreamingController!
	internal var authVC:UIViewController!
	
	internal var container:UIViewController!
	
	var delegate:DXSpotifyAdapterDelegate?
	
	init(container:UIViewController) {
		super.init()
		
		self.container = container
		
		self.auth = SPTAuth.defaultInstance()
		
		self.player = SPTAudioStreamingController.sharedInstance()
		
		self.player.playbackDelegate = self
		
		self.auth.clientID = clientId
		
		self.auth.redirectURL = URL(string: "datx02kandarbete://callback")
		
		self.auth.sessionUserDefaultsKey = "current session"
		
		self.auth.requestedScopes = [SPTAuthStreamingScope];
		
		self.player.delegate = self
		
		
		do {
			try self.player.start(withClientId: self.auth.clientID)
		} catch {
			print(error)
		}
		
		DispatchQueue.main.async {
			self.startAuthenticationFlow()
		}
	}
	
	func startAuthenticationFlow(){
		if self.auth.session != nil{
			if self.auth.session.isValid(){
				self.player.login(withAccessToken: self.auth.session.accessToken)
			} else{
				webAuth()
			}
		} else{
			print("in")
			webAuth()
		}
		
	}
	
	internal func webAuth(){
		let authURL:URL = self.auth.spotifyWebAuthenticationURL()
		
		authVC = SFSafariViewController(url: authURL)
		self.container.present(authVC, animated: true, completion: nil)
	}
	
	func spotifyURL(url:URL) -> Bool{
		if self.auth.canHandle(url){
			self.authVC.presentingViewController?.dismiss(animated: true, completion: nil)
			self.authVC = nil
			
			self.auth.handleAuthCallback(withTriggeredAuthURL: url, callback: {(error, session) -> Void in
				if session != nil{
					self.player.login(withAccessToken: self.auth.session.accessToken)
				}
			})
			
			return true
		}
		return false
	}
	
	func audioStreamingDidLogin(_ audioStreaming: SPTAudioStreamingController!) {
		/*self.player.playSpotifyURI("spotify:track:6nsLzJfvp5OLd4mgqUJkpq", startingWith: 0, startingWithPosition: 0, callback: {(error) -> Void in
			if error != nil{
				print(error)
				return
			}
		})*/
	}
	
	var currentTrackId:String = ""
	func playSong(trackid:String){
		self.player.playSpotifyURI("spotify:track:\(trackid)", startingWith: 0, startingWithPosition: 0, callback: {(error) -> Void in
			if error != nil{
				print(error)
				return
			}
		})
		
		self.currentTrackId = trackid
	}
	
	var position:TimeInterval = 0
	var length:TimeInterval = 0
	func stopSong(){
		position = self.player.playbackState.position
		if let l = self.player.metadata.currentTrack?.duration{
			length = l
		}
		self.player.setIsPlaying(false, callback: {_ in })
		
		finishSong()
	}
	
	internal func finishSong(){
		var rating:Double = 1
		if self.position > 0 && self.length > 0{
			rating = position/length
			position = 0
			length = 0
		}
		delegate?.songFinished(rating: rating)
	}
	
	func audioStreaming(_ audioStreaming: SPTAudioStreamingController!, didStopPlayingTrack trackUri: String!) {
		finishSong()
	}
	
	func audioStreaming(_ audioStreaming: SPTAudioStreamingController!, didStartPlayingTrack trackUri: String!) {
		delegate?.songStarted()
	}
	
	func getSongArtist() -> String?{
		return self.player.metadata.currentTrack?.artistName
	}
	
	func getSongName() -> String?{
		return self.player.metadata.currentTrack?.name
	}
	
}

