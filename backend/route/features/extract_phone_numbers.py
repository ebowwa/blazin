# routes/gemini_flash8b.py

# **WARNING: DO NOT OMIT ANYTHING FROM THE FOLLOWING**,
# if changing add notes be concise to what was done and why

from fastapi import APIRouter, HTTPException, Request
from models.index import Base64ImageInput, PhoneNumberCreate, PhoneNumber  # Import PhoneNumberCreate and PhoneNumber
from database import gemini_flash8b_temp_db, save_gemini_temp_to_file, phone_numbers_db, save_phone_numbers_to_file
from gemini_utils import gemini_flash8b_upload_file, gemini_flash8b_validate_phone_number, gemini_flash8b_model, logger
import base64
import os
import json
from uuid import uuid4
from typing import List

router = APIRouter()

# ------------------------------------------------------
# Gemini Flash-8B Integration for Image Upload and Phone Extraction
# ------------------------------------------------------

@router.post("/upload_base64_image/", response_model=dict)
async def gemini_flash8b_upload_base64_image(data: Base64ImageInput, request: Request):
    client_ip = request.client.host  # Get client's IP address
    logger.info(f"Request received from IP: {client_ip}")

    # Decode the Base64 image data
    try:
        logger.info("Attempting to decode base64 image data...")
        image_data = base64.b64decode(data.image_base64)
        logger.info("Base64 image data successfully decoded.")
    except Exception as e:
        logger.error(f"Failed to decode base64 image data: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid Base64 image data: {e}")

    # Generate a temporary file path
    temp_image_path = f"/tmp/{uuid4()}_{data.file_name or 'uploaded_image.jpeg'}"
    logger.info(f"Temporary image path generated: {temp_image_path}")
    
    # Save the decoded image to the temporary location
    try:
        with open(temp_image_path, "wb") as image_file:
            image_file.write(image_data)
        logger.info(f"Image saved to temporary location: {temp_image_path}")
    except Exception as e:
        logger.error(f"Failed to save image to temp file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")

    # Upload the image to Gemini Flash-8B
    try:
        logger.info("Uploading image to Gemini Flash-8B...")
        uploaded_file = gemini_flash8b_upload_file(temp_image_path, mime_type="image/jpeg")
        logger.info(f"Image successfully uploaded to Gemini Flash-8B. File ID: {uploaded_file}")
    except Exception as e:
        logger.error(f"Failed to upload image to Gemini Flash-8B: {e}")
        os.remove(temp_image_path)
        raise HTTPException(status_code=500, detail=f"Failed to upload image to Gemini Flash-8B: {e}")
    
    # Start a chat session to extract the phone numbers using the correct prompt
    try:
        logger.info("Starting chat session with Gemini Flash-8B for phone number extraction...")
        chat_session = gemini_flash8b_model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        uploaded_file,
                        "You are a software component, to extract phone number(s) from images to add to an internal db. From the image provided, identify and extract all valid US phone numbers. A valid US phone number must:\n\n1. Contain exactly 10 digits.\n2. Follow the format XXX-XXX-XXXX, where each 'X' is a digit from 0 to 9.\n\n**Instructions:**\n1. **Extract:** Scan the image and identify all sequences of digits that could represent US phone numbers.\n2. **Validate:**\n   - Ensure each identified sequence has exactly 10 digits.\n   - Format each valid number as XXX-XXX-XXXX.\n3. **Output:**\n   - Return only a single JSON array containing the valid, formatted phone numbers.\n   - **Do not include** any additional text, comments, explanations, or code block delimiters.\n\n**Example Output:**\n[\"555-123-4567\", \"800-555-0199\"]\n\n**Note:** Ensure that only legitimate and properly formatted US phone numbers are included in the output array.\n- Ensure the chain of thought for the prompt generation prevents stray characters (like Invalid USA phone number.) from being intermingled with the phone numbers.\n - **Do not include** any additional text, comments, explanations, or code block delimiters. If nothing say nothing",
                    ],
                }
            ]
        )
        
        response = chat_session.send_message("Extract phone numbers")
        logger.info(f"Raw response from Gemini Flash-8B: {response.text}")
        
        # Parse the response to extract the JSON array
        # Remove code block delimiters if present
        response_text = response.text.strip()
        if response_text.startswith("```"):
            # Assuming the format is ```json\n[...]\n```
            try:
                first_newline = response_text.find('\n')
                last_backticks = response_text.rfind('```')
                json_content = response_text[first_newline+1:last_backticks].strip()
                phone_numbers = json.loads(json_content)
            except Exception as e:
                logger.error(f"Failed to parse JSON from response with code block delimiters: {e}")
                raise HTTPException(status_code=500, detail="Failed to parse phone numbers from response.")
        else:
            # Attempt to parse directly
            try:
                phone_numbers = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from response: {e}")
                raise HTTPException(status_code=500, detail="Failed to parse phone numbers from response.")
        
        logger.info(f"Phone numbers extracted: {phone_numbers}")
    except Exception as e:
        logger.error(f"Failed to extract phone numbers from image: {e}")
        os.remove(temp_image_path)
        raise HTTPException(status_code=500, detail=f"Failed to extract phone numbers: {e}")
    
    # Validate and temporarily store the phone numbers under the user's IP
    validated_numbers = []
    for number in phone_numbers:
        try:
            formatted_number = gemini_flash8b_validate_phone_number(number)
            validated_numbers.append(formatted_number)
            logger.info(f"Validated phone number: {formatted_number}")
        except ValueError as e:
            logger.warning(f"Failed to validate number {number}: {e}")
    
    # Store extracted numbers temporarily under the user's IP
    if client_ip in gemini_flash8b_temp_db:
        gemini_flash8b_temp_db[client_ip].extend(validated_numbers)
        logger.info(f"Appended validated numbers for IP {client_ip}: {validated_numbers}")
    else:
        gemini_flash8b_temp_db[client_ip] = validated_numbers
        logger.info(f"Stored validated numbers for IP {client_ip}: {validated_numbers}")
    
    # Save the temporary data
    try:
        save_gemini_temp_to_file(gemini_flash8b_temp_db)
        logger.info("Temporary phone number data saved.")
    except Exception as e:
        logger.error(f"Failed to save temporary data: {e}")
        raise HTTPException(status_code=500, detail="Failed to save temporary data.")
    
    # Clean up the temporary image file
    try:
        os.remove(temp_image_path)
        logger.info(f"Temporary image file deleted: {temp_image_path}")
    except Exception as e:
        logger.warning(f"Failed to delete temporary image file {temp_image_path}: {e}")
    
    return {
        "detail": "Phone numbers extracted for review.",
        "numbers": validated_numbers
    }

@router.get("/review_numbers/", response_model=dict)
async def gemini_flash8b_review_numbers(request: Request):
    client_ip = request.client.host  # Get client's IP address
    
    # Check if there are any numbers stored for this IP in the temp database
    numbers_to_review = gemini_flash8b_temp_db.get(client_ip, None)
    
    if not numbers_to_review:
        raise HTTPException(status_code=404, detail="No phone numbers found for review.")
    
    # Return the numbers stored for this IP address
    return {client_ip: numbers_to_review}

# Endpoint to confirm and save the reviewed phone numbers
@router.post("/confirm_numbers/", response_model=dict)
async def gemini_flash8b_confirm_numbers(request: Request):
    client_ip = request.client.host
    numbers_to_confirm = gemini_flash8b_temp_db.get(client_ip, [])
    
    if not numbers_to_confirm:
        raise HTTPException(status_code=404, detail="No phone numbers found for confirmation.")
    
    # Now store confirmed numbers in the main phone numbers DB
    for number in numbers_to_confirm:
        # Check for duplicates before adding
        if any(pn.number == number for pn in phone_numbers_db.values()):
            print(f"Duplicate phone number {number} skipped.")
            continue
        try:
            new_phone_create = PhoneNumberCreate(number=number, has_redeem_value=False)  # Adjust redeem value as needed
            new_phone = PhoneNumber(**new_phone_create.dict(), created_ip=client_ip)
            phone_numbers_db[new_phone.id] = new_phone
        except Exception as e:
            print(f"Failed to process number {number}: {e}")
    
    # Save the updated main database
    save_phone_numbers_to_file(phone_numbers_db)
    
    # Clear the temporary storage after confirmation
    del gemini_flash8b_temp_db[client_ip]
    save_gemini_temp_to_file(gemini_flash8b_temp_db)
    
    return {"detail": "Phone numbers confirmed and saved."}

# Endpoint to edit numbers before saving
@router.put("/edit_numbers/", response_model=dict)
async def gemini_flash8b_edit_numbers(new_numbers: List[str], request: Request):
    client_ip = request.client.host
    if client_ip not in gemini_flash8b_temp_db:
        raise HTTPException(status_code=404, detail="No phone numbers found to edit.")
    
    validated_numbers = []
    for number in new_numbers:
        try:
            formatted_number = gemini_flash8b_validate_phone_number(number)
            validated_numbers.append(formatted_number)
        except ValueError as e:
            print(f"Failed to validate number {number}: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid number {number}")
    
    # Update the temporary storage with the new validated numbers
    gemini_flash8b_temp_db[client_ip] = validated_numbers
    save_gemini_temp_to_file(gemini_flash8b_temp_db)
    
    return {
        "detail": "Phone numbers updated for review.",
        "numbers": validated_numbers
    }

# Endpoint to delete specific numbers before saving
@router.delete("/delete_number/", response_model=dict)
async def gemini_flash8b_delete_number(number_to_delete: str, request: Request):
    client_ip = request.client.host
    if client_ip not in gemini_flash8b_temp_db:
        raise HTTPException(status_code=404, detail="No phone numbers found to delete.")
    
    updated_numbers = [
        number for number in gemini_flash8b_temp_db[client_ip]
        if number != number_to_delete
    ]
    
    gemini_flash8b_temp_db[client_ip] = updated_numbers
    save_gemini_temp_to_file(gemini_flash8b_temp_db)
    
    return {
        "detail": f"Phone number {number_to_delete} deleted from review.",
        "numbers": gemini_flash8b_temp_db[client_ip]
    }
