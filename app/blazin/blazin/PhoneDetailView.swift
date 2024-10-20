//
//  PhoneDetailView.swift
//  blazin
//
//  Created by Elijah Arbee on 10/19/24.
//
import SwiftUI

struct PhoneDetailView: View {
    @Environment(\.presentationMode) var presentationMode
    var phone: PhoneNumber
    @ObservedObject var viewModel: PhoneNumberViewModel
    
    @State private var amountSpent: String
    @State private var numberOfPoints: String
    @State private var showDeleteConfirmation = false // State for showing confirmation dialog
    
    init(phone: PhoneNumber, viewModel: PhoneNumberViewModel) {
        self.phone = phone
        self.viewModel = viewModel
        _amountSpent = State(initialValue: String(phone.amountSpent))
        _numberOfPoints = State(initialValue: String(phone.numberOfPoints))
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Phone Info")) {
                    Text("Number: \(phone.number)")
                    if let name = phone.name {
                        Text("Name: \(name)")
                    }
                    Toggle(isOn: Binding(
                        get: { phone.hasRedeemValue },
                        set: { newValue in
                            var updatedPhone = phone
                            updatedPhone.hasRedeemValue = newValue
                            viewModel.updatePhoneNumber(updatedPhone)
                        }
                    )) {
                        Text("Has Redeem Value")
                    }
                }
                
                Section(header: Text("Usage")) {
                    Text("Last Used: \(phone.lastUsed?.formatted() ?? "Never")")
                    Text("Last Tried: \(phone.lastTried?.formatted() ?? "Never")")
                }
                
                Section(header: Text("Financials")) {
                    TextField("Amount Spent", text: $amountSpent)
                        .keyboardType(.decimalPad)
                        .onSubmit {
                            if let amount = Double(amountSpent) {
                                var updatedPhone = phone
                                updatedPhone.amountSpent = amount
                                updatedPhone.numberOfPoints = viewModel.calculatePoints(for: updatedPhone)
                                viewModel.updatePhoneNumber(updatedPhone)
                            }
                        }
                    
                    TextField("Number of Points", text: $numberOfPoints)
                        .keyboardType(.numberPad)
                        .onSubmit {
                            if let points = Int(numberOfPoints) {
                                var updatedPhone = phone
                                updatedPhone.numberOfPoints = points
                                viewModel.updatePhoneNumber(updatedPhone)
                            }
                        }
                }
            }
            .navigationTitle("Details")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
                ToolbarItem(placement: .destructiveAction) {
                    Button("Delete") {
                        showDeleteConfirmation = true // Show the confirmation dialog
                    }
                }
            }
            .alert(isPresented: $showDeleteConfirmation) {
                Alert(
                    title: Text("Delete Phone"),
                    message: Text("Are you sure you want to delete this phone number?"),
                    primaryButton: .destructive(Text("Delete")) {
                        if let index = viewModel.phoneNumbers.firstIndex(where: { $0.id == phone.id }) {
                            viewModel.deletePhoneNumber(at: IndexSet(integer: index))
                            presentationMode.wrappedValue.dismiss() // Close the view after deletion
                        }
                    },
                    secondaryButton: .cancel()
                )
            }
        }
    }
}

extension PhoneNumberViewModel {
    func calculatePoints(for phone: PhoneNumber) -> Int {
        // Example: 1 point per $1 spent
        return Int(phone.amountSpent)
    }
}
