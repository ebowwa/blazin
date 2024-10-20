//
//  UploadImageView.swift
//  blazin
//
//  Created by Elijah Arbee on 10/19/24.
//

import SwiftUI

struct UploadImageView: View {
    @ObservedObject var viewModel: PhoneNumberViewModel
    @State private var selectedImage: UIImage?
    @State private var isUploading = false
    @State private var uploadSuccess: Bool?
    @State private var extractedNumbers: [String] = []
    @State private var isReviewing = false
    @State private var confirmationMessage: String?
    
    var body: some View {
        VStack {
            if let selectedImage = selectedImage {
                Image(uiImage: selectedImage)
                    .resizable()
                    .scaledToFit()
                    .frame(height: 250)
                    .cornerRadius(10)
                    .shadow(radius: 5)
            } else {
                Text("Select an image to upload")
                    .font(.headline)
                    .padding()
            }
            
            if isUploading {
                ProgressView("Uploading...") // Show progress while uploading
            } else if isReviewing {
                ProgressView("Fetching extracted numbers...") // Show progress while reviewing numbers
            } else if uploadSuccess == true && !extractedNumbers.isEmpty {
                List(extractedNumbers, id: \.self) { number in
                    Text(number)
                }
                
                Button(action: {
                    confirmNumbers() // Confirm the extracted numbers
                }) {
                    Text("Confirm Numbers")
                        .font(.title2)
                        .frame(minWidth: 0, maxWidth: .infinity)
                        .padding()
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .padding()
                
                if let message = confirmationMessage {
                    Text(message)
                        .font(.headline)
                        .foregroundColor(.blue)
                        .padding()
                }
            } else {
                Button(action: {
                    showImagePicker() // Trigger image picker
                }) {
                    Text("Choose Image")
                        .font(.title2)
                        .frame(minWidth: 0, maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .padding()
                
                if let selectedImage = selectedImage {
                    Button(action: {
                        uploadImage(image: selectedImage) // Trigger image upload
                    }) {
                        Text("Upload Image")
                            .font(.title2)
                            .frame(minWidth: 0, maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .padding()
                }
            }
        }
        .sheet(isPresented: $showingImagePicker) {
            ImagePickerView(selectedImage: $selectedImage)
        }
    }
    
    @State private var showingImagePicker = false
    
    private func showImagePicker() {
        showingImagePicker = true
    }
    
    // Function to upload the image
    func uploadImage(image: UIImage) {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            return
        }
        
        let base64String = imageData.base64EncodedString()
        
        let url = URL(string: "https://e626-2600-387-f-771b-00-4.ngrok-free.app/gemini_flash8b/upload_base64_image/")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let payload: [String: Any] = [
            "image_base64": base64String,
            "file_name": "uploaded_image.jpeg"
        ]
        
        guard let httpBody = try? JSONSerialization.data(withJSONObject: payload, options: []) else {
            return
        }
        
        request.httpBody = httpBody
        
        isUploading = true
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isUploading = false
                if let response = response as? HTTPURLResponse, response.statusCode == 200 {
                    uploadSuccess = true
                    fetchExtractedNumbers() // Fetch the extracted numbers after upload
                } else {
                    uploadSuccess = false
                }
            }
        }.resume()
    }
    
    // Function to fetch extracted numbers after upload
    func fetchExtractedNumbers() {
        guard let url = URL(string: "https://e626-2600-387-f-771b-00-4.ngrok-free.app/gemini_flash8b/review_numbers/") else { return }
        
        isReviewing = true
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isReviewing = false
                if let data = data,
                   let json = try? JSONSerialization.jsonObject(with: data) as? [String: [String]],
                   let numbers = json.values.first {
                    extractedNumbers = numbers
                } else {
                    extractedNumbers = []
                }
            }
        }.resume()
    }
    
    // Function to confirm numbers after review
    func confirmNumbers() {
        guard let url = URL(string: "https://e626-2600-387-f-771b-00-4.ngrok-free.app/gemini_flash8b/confirm_numbers/") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let response = response as? HTTPURLResponse, response.statusCode == 200 {
                    // Confirmation successful
                    confirmationMessage = "Phone numbers confirmed and added."
                    
                    // Fetch the updated list from the server
                    viewModel.fetchFromServer()  // Add this to ensure the client-side list is updated
                    
                    extractedNumbers = [] // Clear the numbers after confirmation
                    selectedImage = nil    // Optionally reset the selected image
                } else {
                    confirmationMessage = "Failed to confirm numbers. Please try again."
                }
            }
        }.resume()
    }
}
