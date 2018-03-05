//
//  DXServerManager.swift
//  KandArbete
//
//  Created by Albin Bååw on 2018-02-05.
//  Copyright © 2018 Albin Bååw. All rights reserved.
//

import UIKit

class DXServerManager: NSObject {
	internal static let baseURL = "http://81.232.180.10/"
	internal static let userDataURL = baseURL + "userdata/"
	
	class func sendUserData(userId:String, trackId:String, heartRate:Int, time:String, rating:Double){
		guard let url:URL = URL(string: userDataURL) else{
			return
		}
		
		let userData = UserData(userid: userId, songid: trackId, heartrate: heartRate, rating: rating)
		let jsonData:Data!
		do{
			let encoder = JSONEncoder()
			jsonData = try encoder.encode(userData)
		} catch{
			print(error)
			return
		}
		
		print(jsonData)
		
		var urlRequest = URLRequest(url: url)
		urlRequest.httpMethod = "POST"
		urlRequest.httpBody = jsonData
		
		let task = URLSession.shared.dataTask(with: urlRequest, completionHandler: {(data, response, error) in
			if error != nil{
				print(error!)
			}
			
			//print(response)
			//print(data)
		})
		
		task.resume()
	}
	
	struct UserData: Codable{
		let userid:String
		let songid:String
		let heartrate:Int
		let rating:Double
	}
	
	class func retrieveNextTrackId(userId:String, heartRate:Int, callback:@escaping (String) -> Void){
		guard let url:URL = URL(string: userDataURL + "\(userId.urlFriendly)/?heartrate=\(heartRate)") else{
			return
		}
		
		let urlRequest = URLRequest(url: url)
		let task = URLSession.shared.dataTask(with: urlRequest, completionHandler: {(data, response, error) in
			if error != nil{
				print(error!)
			}
			
			do{
				let decoder = JSONDecoder()
				let song = try decoder.decode(Song.self, from: data!)
				
				callback(song.songid)
			} catch{
				print(error)
			}
			
			
		})
		
		task.resume()
	}
	
	struct Song: Codable{
		let songid:String
	}
}
