//
//  DXPulseTracker.swift
//  KandArbete
//
//  Created by Albin Bååw on 2018-01-30.
//  Copyright © 2018 Albin Bååw. All rights reserved.
//

import UIKit
import HealthKit

protocol DXPulseTrackerDelegate {
	func updateLatestHeartRate(heartRate:Int, date:Date)
}

class DXPulseTracker: NSObject {
	
	internal let health: HKHealthStore = HKHealthStore()
	internal let heartRateUnit:HKUnit = HKUnit(from: "count/min")
	internal let heartRateType:HKQuantityType = HKQuantityType.quantityType(forIdentifier: .heartRate)!
	internal var heartRateQuery:HKSampleQuery?
	
	var delegate:DXPulseTrackerDelegate?
	
	/*Method to get todays heart rate - this only reads data from health kit. */
	func getTodaysHeartRates() -> Int{
		//predicate
		let calendar = Calendar.current
		let now = Date()
		let components = calendar.dateComponents([.year, .month, .day], from: now)
		guard let startDate:Date = calendar.date(from: components) else{
			return 0
		}
		
		let endDate:Date? = calendar.date(byAdding: .day, value: 1, to: startDate)
		let predicate = HKQuery.predicateForSamples(withStart: startDate, end: endDate, options: .strictStartDate) //options should be "none"
		
		//descriptor
		let sortDescriptors = [
			NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)
		]
		
		heartRateQuery = HKSampleQuery(sampleType: heartRateType, predicate: predicate, limit: 0, sortDescriptors: sortDescriptors, resultsHandler: { (query:HKSampleQuery, results:[HKSample]?, error:Error?) -> Void in
			
			if error != nil{
				print(error)
			}
			
			self.printHeartRateInfo(results: results)
			
			})
		
		health.execute(heartRateQuery!)
		
		return 0
	}
	
	func getLatestHeartRate(callback:@escaping (Int, Date) -> Void){
		
		let calendar = Calendar.current
		
		let date:Date? = calendar.date(byAdding: .hour, value: -1, to: Date())
		
		let predicate = HKQuery.predicateForSamples(withStart: date, end: nil, options: []) //options should be "none"
		
		//descriptor
		let sortDescriptors = [
			NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)
		]
		
		heartRateQuery = HKSampleQuery(sampleType: heartRateType, predicate: predicate, limit: 0, sortDescriptors: sortDescriptors, resultsHandler: { (query:HKSampleQuery, results:[HKSample]?, error:Error?) -> Void in
			
			if error != nil{
				print(error)
			}
			
			if results != nil{
				if results!.count > 0{
					if let data:HKQuantitySample = results![0] as! HKQuantitySample{
						callback(Int(data.quantity.doubleValue(for: self.heartRateUnit)), data.endDate)
					}
				}
			}
		})
		
		health.execute(heartRateQuery!)
	}
	
	private func printHeartRateInfo(results:[HKSample]?){
		for i in 0..<results!.count {
			guard let data:HKQuantitySample = results![i] as? HKQuantitySample else{
				return
			}
			
			print("------------")
			print("Heart Rate: \(data.quantity.doubleValue(for: heartRateUnit))")
			print("Start Date: \(data.startDate)")
			print("End Date: \(data.endDate)")
		}
	}
	
	
	/*private func printHeartRateInfo(results:[HKSample]?)
	{
		for(var iter = 0 ; iter < results!.count; iter++)
		{
			guard let currData:HKQuantitySample = results![iter] as? HKQuantitySample else { return }
			
			print("[\(iter)]")
			print("Heart Rate: \(currData.quantity.doubleValueForUnit(heartRateUnit))")
			print("quantityType: \(currData.quantityType)")
			print("Start Date: \(currData.startDate)")
			print("End Date: \(currData.endDate)")
			print("Metadata: \(currData.metadata)")
			print("UUID: \(currData.UUID)")
			print("Source: \(currData.sourceRevision)")
			print("Device: \(currData.device)")
			print("---------------------------------\n")
		}
	}*/
	
	
	internal var workout:HKWorkoutConfiguration!
	func startStreamingHeartRate(){
		DispatchQueue.main.async{
			print("Starting Watch app\n----------")
			self.workout = HKWorkoutConfiguration()
			self.workout.activityType = .running
			self.workout.locationType = .unknown
			
			self.health.startWatchApp(with: self.workout, completion: {(flag, error) -> Void in
				print("--- Start ----")
				print(flag)
				print(error?.localizedDescription)
				
				if (flag){
					let datePredicate = HKQuery.predicateForSamples(withStart: Date(), end: nil, options: .strictEndDate )
					//let devicePredicate = HKQuery.predicateForObjects(from: [HKDevice.local()])
					let predicate = NSCompoundPredicate(andPredicateWithSubpredicates:[datePredicate])
					
					
					let heartRateQuery = HKAnchoredObjectQuery(type: self.heartRateType, predicate: predicate, anchor: nil, limit: Int(HKObjectQueryNoLimit)) { (query, sampleObjects, deletedObjects, newAnchor, error) -> Void in
						//guard let newAnchor = newAnchor else {return}
						//self.anchor = newAnchor
						self.printHeartRateInfo(results: sampleObjects)
					}
					
					heartRateQuery.updateHandler = {(query, samples, deleteObjects, newAnchor, error) -> Void in
						//self.anchor = newAnchor!
						self.printHeartRateInfo(results: samples)
					}
					self.health.execute(heartRateQuery)
				}
			})
		}
	}
	
	func requestAuthorization(){
		let readingTypes:Set = Set([heartRateType])
		
		let writingTypes:Set = Set([heartRateType])
		
		health.requestAuthorization(toShare: writingTypes, read: readingTypes) { (success, error) -> Void in
			
			if error != nil{
				print("error \(error?.localizedDescription)")
			}
			else if success{
				
			}
		}
	}
	
	//static internal var currentHRValues:[Double] = []
	static internal var currHR:Double = 0
	class func setLatestHR(hr:Double){
		//currentHRValues.append(hr)
		//print(hr)
		currHR = hr
	}
	
	func getAverageHeartRate() -> Double{
		/*var a:Double = 0
		
		if DXPulseTracker.currentHRValues.count > 0{
			for value in DXPulseTracker.currentHRValues{
				a += value
			}
			
			a /= Double(DXPulseTracker.currentHRValues.count)
		}*/
		
		return DXPulseTracker.currHR
	}
	
	func clearAverageHeartRate(){
		//DXPulseTracker.currentHRValues.removeAll()
	}
	
}
