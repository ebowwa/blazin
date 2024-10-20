//
//  ContentView.swift
//  blazin
//
//  Created by Elijah Arbee on 10/19/24.
//
import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = PhoneNumberViewModel()
    @State private var showingAddSheet = false
    @State private var showingUploadSheet = false
    @State private var selectedPhone: PhoneNumber?
    @State private var showingDetail = false
    @State private var isMenuVisible = false

    var body: some View {
        ZStack {
            NavigationView {
                List {
                    ForEach(viewModel.phoneNumbers) { phone in
                        Button(action: {
                            selectedPhone = phone
                            showingDetail = true
                        }) {
                            HStack {
                                VStack(alignment: .leading) {
                                    Text(phone.number)
                                        .font(.headline)
                                    if let name = phone.name {
                                        Text(name)
                                            .font(.subheadline)
                                            .foregroundColor(.gray)
                                    }
                                }
                                Spacer()
                                if phone.hasRedeemValue {
                                    Image(systemName: "gift.fill")
                                        .foregroundColor(.green)
                                }
                            }
                        }
                    }
                    .onDelete(perform: viewModel.deletePhoneNumber)
                }
                .navigationTitle("Phone Numbers")
                .toolbar {
                    ToolbarItem(placement: .navigationBarLeading) {
                        Button(action: {
                            withAnimation {
                                isMenuVisible.toggle()
                            }
                        }) {
                            Image(systemName: "line.horizontal.3")
                        }
                    }
                    ToolbarItem(placement: .navigationBarTrailing) {
                        HStack {
                            Button(action: { showingAddSheet = true }) {
                                Image(systemName: "plus")
                            }
                            Button(action: { showingUploadSheet = true }) {
                                Image(systemName: "camera.circle")
                                    .symbolEffect(.scale)
                            }
                        }
                    }
                }
                .sheet(isPresented: $showingAddSheet) {
                    AddPhoneNumberView(viewModel: viewModel)
                }
                .sheet(isPresented: $showingUploadSheet) {
                    UploadImageView(viewModel: viewModel) // Open the upload view
                }
                .sheet(isPresented: $showingDetail) {
                    if let phone = selectedPhone {
                        PhoneDetailView(phone: phone, viewModel: viewModel)
                    }
                }
            }
            if isMenuVisible {

                    }
            }
        }
    }

