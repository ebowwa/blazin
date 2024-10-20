//
//  PhoneNumber.swift
//  blazin
//
//  Created by Elijah Arbee on 10/19/24.
//


import Foundation

struct PhoneNumber: Identifiable, Codable, Equatable {
    let id: UUID
    let number: String
    var hasRedeemValue: Bool
    var lastUsed: Date?
    var lastTried: Date?
    var name: String?
    var amountSpent: Double
    var numberOfPoints: Int
    
    enum CodingKeys: String, CodingKey {
        case id
        case number
        case hasRedeemValue = "has_redeem_value"
        case lastUsed = "last_used"
        case lastTried = "last_tried"
        case name
        case amountSpent = "amount_spent"
        case numberOfPoints = "number_of_points"
    }
}
