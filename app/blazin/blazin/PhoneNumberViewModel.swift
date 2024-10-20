//
//  PhoneNumberViewModel.swift
//  blazin
//
//  Created by Elijah Arbee on 10/19/24.
//


import Foundation
import Combine

class PhoneNumberViewModel: ObservableObject {
    @Published var phoneNumbers: [PhoneNumber] = []
    
    private let localStorageKey = "phoneNumbers"
    private var cancellables = Set<AnyCancellable>()
    
    // Server URL
    private let serverURL = URL(string: "https://e626-2600-387-f-771b-00-4.ngrok-free.app")! // Update if server is hosted elsewhere
    
    init() {
        loadFromLocal()
        fetchFromServer()
        scheduleDailyReset()
    }
    
    // Load from UserDefaults
    func loadFromLocal() {
        if let data = UserDefaults.standard.data(forKey: localStorageKey),
           let decoded = try? JSONDecoder().decode([PhoneNumber].self, from: data) {
            self.phoneNumbers = decoded
        }
    }
    
    // Save to UserDefaults
    func saveToLocal() {
        if let encoded = try? JSONEncoder().encode(phoneNumbers) {
            UserDefaults.standard.set(encoded, forKey: localStorageKey)
        }
    }
    
    // Fetch from Server
    func fetchFromServer() {
        let url = serverURL.appendingPathComponent("/phone_numbers/")
        URLSession.shared.dataTaskPublisher(for: url)
            .map { $0.data }
            .decode(type: [PhoneNumber].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .sink(receiveCompletion: { completion in
                switch completion {
                case .failure(let error):
                    print("Fetch error: \(error)")
                case .finished:
                    break
                }
            }, receiveValue: { [weak self] phones in
                self?.phoneNumbers = phones
                self?.saveToLocal()
            })
            .store(in: &cancellables)
    }
    
    // Add Phone Number to Server
    func addPhoneNumber(number: String, hasRedeemValue: Bool, name: String? = nil, completion: @escaping (String?) -> Void) {
        guard !phoneNumbers.contains(where: { $0.number == number }) else {
            completion("This phone number is already added.")
            return
        }
        
        let url = serverURL.appendingPathComponent("/phone_numbers/")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let newPhone = PhoneNumber(id: UUID(), number: number, hasRedeemValue: hasRedeemValue, lastUsed: nil, lastTried: nil, name: name, amountSpent: 0.0, numberOfPoints: 0)
        
        guard let data = try? JSONEncoder().encode(newPhone) else {
            completion("Error encoding phone number data.")
            return
        }
        request.httpBody = data
        
        URLSession.shared.dataTaskPublisher(for: request)
            .map { $0.data }
            .decode(type: PhoneNumber.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .sink(receiveCompletion: { completionResult in
                switch completionResult {
                case .failure(let error):
                    if let urlError = error as? URLError, urlError.code == .badServerResponse {
                        // Specific error handling for invalid phone number
                        completion("Invalid USA phone number. Please enter a valid 10-digit number.")
                    } else {
                        completion("An error occurred: \(error.localizedDescription)")
                    }
                case .finished:
                    break
                }
            }, receiveValue: { [weak self] phone in
                self?.phoneNumbers.append(phone)
                self?.saveToLocal()
                completion(nil) // No error
            })
            .store(in: &cancellables)
    }

    
    // Update Phone Number on Server
    func updatePhoneNumber(_ phone: PhoneNumber) {
        guard let index = phoneNumbers.firstIndex(where: { $0.id == phone.id }) else { return }
        
        let url = serverURL.appendingPathComponent("/phone_numbers/\(phone.id.uuidString)")
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Create a PhoneNumberUpdate object
        let update = PhoneNumberUpdate(
            has_redeem_value: phone.hasRedeemValue,
            last_used: phone.lastUsed,
            last_tried: phone.lastTried,
            name: phone.name,
            amount_spent: phone.amountSpent,
            number_of_points: phone.numberOfPoints
        )
        
        guard let data = try? JSONEncoder().encode(update) else { return }
        request.httpBody = data
        
        URLSession.shared.dataTaskPublisher(for: request)
            .map { $0.data }
            .decode(type: PhoneNumber.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .sink(receiveCompletion: { completion in
                switch completion {
                case .failure(let error):
                    print("Update error: \(error)")
                case .finished:
                    break
                }
            }, receiveValue: { [weak self] updatedPhone in
                self?.phoneNumbers[index] = updatedPhone
                self?.saveToLocal()
            })
            .store(in: &cancellables)
    }
    
    // Delete Phone Number from Server
    func deletePhoneNumber(at offsets: IndexSet) {
        offsets.forEach { index in
            let phone = phoneNumbers[index]
            
            // Create URL components to build the URL with query parameters
            var components = URLComponents(string: "\(serverURL)/delete_number/")!
            components.queryItems = [
                URLQueryItem(name: "number_to_delete", value: phone.number)
            ]
            
            guard let url = components.url else {
                print("Failed to construct URL")
                return
            }
            
            print("Attempting to delete phone number: \(phone.number)")  // Log the phone number being used
            
            var request = URLRequest(url: url)
            request.httpMethod = "DELETE"
            
            URLSession.shared.dataTaskPublisher(for: request)
                .map { $0.data }
                .decode(type: DeleteResponse.self, decoder: JSONDecoder())
                .receive(on: DispatchQueue.main)
                .sink(receiveCompletion: { completion in
                    switch completion {
                    case .failure(let error):
                        print("Delete error: \(error)")
                    case .finished:
                        break
                    }
                }, receiveValue: { [weak self] response in
                    if response.detail == "Phone number deleted." {
                        self?.phoneNumbers.remove(at: index)
                        self?.saveToLocal()
                    }
                })
                .store(in: &cancellables)
        }
    }
    
    // Reset daily usage at 3 AM
    private func scheduleDailyReset() {
        let now = Date()
        var dateComponents = Calendar.current.dateComponents([.year, .month, .day], from: now)
        dateComponents.hour = 3
        dateComponents.minute = 0
        dateComponents.second = 0
        
        var nextReset = Calendar.current.date(from: dateComponents) ?? now
        if nextReset <= now {
            nextReset = Calendar.current.date(byAdding: .day, value: 1, to: nextReset) ?? now
        }
        
//        let timer = Timer(fireAt: nextReset, interval: 0, target: self, selector: #selector(resetDailyUsage), userInfo: nil, repeats: false)
//        RunLoop.main.add(timer, forMode: .common)
    }
    

// Helper Models
struct PhoneNumberUpdate: Codable {
    let has_redeem_value: Bool?
    let last_used: Date?
    let last_tried: Date?
    let name: String?
    let amount_spent: Double?
    let number_of_points: Int?
}

struct DeleteResponse: Codable {
    let detail: String
}


//
//   @objc func resetDailyUsage() {
        // Reset daily usage logic
        // For this MVP, we'll reset the used recently

        }
//       scheduleDailyReset()

