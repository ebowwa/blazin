//
//  AddPhoneNumberView.swift
//  blazin
//
//  Created by Elijah Arbee on 10/19/24.
//
import SwiftUI

struct AddPhoneNumberView: View {
    @Environment(\.presentationMode) var presentationMode
    @ObservedObject var viewModel: PhoneNumberViewModel
    @State private var number: String = ""
    @State private var hasRedeemValue: Bool = false
    @State private var name: String = ""
    @State private var showAlert: Bool = false
    @State private var alertMessage: String = ""

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Phone Number")) {
                    TextField("Enter phone number", text: $number)
                        .keyboardType(.phonePad)
                }
                
                Section {
                    Toggle(isOn: $hasRedeemValue) {
                        Text("Has Redeem Value")
                    }
                }
                
                Section(header: Text("Optional")) {
                    TextField("Name", text: $name)
                }
            }
            .navigationTitle("Add Phone")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        viewModel.addPhoneNumber(number: number, hasRedeemValue: hasRedeemValue, name: name.isEmpty ? nil : name) { error in
                            if let error = error {
                                alertMessage = error
                                showAlert = true
                            } else {
                                presentationMode.wrappedValue.dismiss()
                            }
                        }
                    }
                    .disabled(number.isEmpty)
                }
                
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
            }
            .alert(isPresented: $showAlert) {
                Alert(
                    title: Text("Invalid Number"),
                    message: Text(alertMessage),
                    dismissButton: .default(Text("Got it!"))
                )
            }
        }
    }
}
