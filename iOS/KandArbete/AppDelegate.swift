//
//  AppDelegate.swift
//  KandArbete
//
//  Created by Albin Bååw on 2018-01-30.
//  Copyright © 2018 Albin Bååw. All rights reserved.
//

import UIKit
import HealthKit
import WatchConnectivity

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate, WCSessionDelegate {

	var window: UIWindow?
	
	var spotifyAdapter:DXSpotifyAdapter!


	func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplicationLaunchOptionsKey: Any]?) -> Bool {
		// Override point for customization after application launch.
		
		spotifyAdapter = DXSpotifyAdapter(container: (self.window?.rootViewController)!)
		
		if WCSession.isSupported() {
			let session = WCSession.default
			session.delegate = self
			session.activate()
		}
		
		return true
	}

	func applicationWillResignActive(_ application: UIApplication) {
		// Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
		// Use this method to pause ongoing tasks, disable timers, and invalidate graphics rendering callbacks. Games should use this method to pause the game.
	}

	func applicationDidEnterBackground(_ application: UIApplication) {
		// Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later.
		// If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
	}

	func applicationWillEnterForeground(_ application: UIApplication) {
		// Called as part of the transition from the background to the active state; here you can undo many of the changes made on entering the background.
	}

	func applicationDidBecomeActive(_ application: UIApplication) {
		// Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
	}

	func applicationWillTerminate(_ application: UIApplication) {
		// Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.
	}
	
	func application(_ app: UIApplication, open url: URL, options: [UIApplicationOpenURLOptionsKey : Any] = [:]) -> Bool {
		return spotifyAdapter.spotifyURL(url: url)
	}
	
	let healthStore = HKHealthStore()
	// authorization from watch
	func applicationShouldRequestHealthAuthorization(_ application: UIApplication) {
		
		self.healthStore.handleAuthorizationForExtension { success, error in
			
		}
	}
	
	func session(_ session: WCSession,
				 didReceiveMessage message: [String : AnyObject],
				 replyHandler replyHandler: ([String : AnyObject]) -> Void){
		DXPulseTracker.setLatestHR(hr: message["heartrate"] as! Double)
		//do something according to the message dictionary
		//responseMessage = ["key" : "value"] //values for the replyHandler
		//replyHandler(responseMessage)
	}
	
	func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
		//
	}
	
	func sessionDidBecomeInactive(_ session: WCSession) {
		//
	}
	
	func sessionDidDeactivate(_ session: WCSession) {
		//
	}
	
	func session(_ session: WCSession, didReceiveMessage message: [String : Any]) {
		DXPulseTracker.setLatestHR(hr: message["heartrate"] as! Double)
	}
	
	func session(_ session: WCSession, didReceiveMessage message: [String : Any], replyHandler: @escaping ([String : Any]) -> Void) {
		DXPulseTracker.setLatestHR(hr: message["heartrate"] as! Double)
	}


}

