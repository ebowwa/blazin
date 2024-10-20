# routes/phone_numbers.py

# **WARNING: DO NOT OMIT ANYTHING FROM THE FOLLOWING**,
# if changing add notes be concise to what was done and why

from fastapi import APIRouter, HTTPException, Request
from models.index import PhoneNumber, PhoneNumberCreate, PhoneNumberUpdate
from database import phone_numbers_db, save_phone_numbers_to_file
from typing import List
from uuid import UUID

router = APIRouter()

# ------------------------------------------------------
# CRUD Routes (Create, Read, Update, Delete operations)
# ------------------------------------------------------

# Create a new phone number entry
@router.post("/", response_model=PhoneNumber)
async def create_phone_number(phone: PhoneNumberCreate, request: Request):
    client_ip = request.client.host  # Get client's IP address
    
    # Check for duplicate number in the database
    for pn in phone_numbers_db.values():
        if pn.number == phone.number:
            raise HTTPException(status_code=400, detail="Phone number already exists.")
    
    # Create new PhoneNumber object and store it in the in-memory database
    new_phone = PhoneNumber(**phone.dict(), created_ip=client_ip)  # Use dict() to unpack the data
    phone_numbers_db[new_phone.id] = new_phone  # Add the new phone to the database
    
    # Save updated data to JSON file
    save_phone_numbers_to_file(phone_numbers_db)

    return new_phone

# Retrieve all phone numbers in the database
@router.get("/", response_model=List[PhoneNumber])
async def get_phone_numbers(request: Request):
    client_ip = request.client.host  # Get client's IP address
    print(f"Phone numbers requested from IP: {client_ip}")
    return list(phone_numbers_db.values())

# Retrieve a single phone number by its ID
@router.get("/{phone_id}", response_model=PhoneNumber)
async def get_phone_number(phone_id: UUID, request: Request):
    client_ip = request.client.host  # Get client's IP address
    phone = phone_numbers_db.get(phone_id)  # Fetch phone by ID
    if not phone:
        raise HTTPException(status_code=404, detail="Phone number not found.")
    print(f"Phone number {phone_id} accessed from IP: {client_ip}")
    return phone

# Route: Search for phone number and retrieve its UUID
@router.get("/search_phone_number/{phone_number}")
async def search_phone_number(phone_number: str, request: Request):
    client_ip = request.client.host  # Get client's IP address
    # Search the database for the phone number
    for phone in phone_numbers_db.values():
        if phone.number == phone_number:
            print(f"Phone number {phone_number} found, accessed from IP: {client_ip}")
            return {"id": str(phone.id), "client_ip": client_ip}
    raise HTTPException(status_code=404, detail="Phone number not found.")

# Update a phone number's details
@router.put("/{phone_id}", response_model=PhoneNumber)
async def update_phone_number(phone_id: UUID, phone_update: PhoneNumberUpdate, request: Request):
    client_ip = request.client.host  # Get client's IP address
    phone = phone_numbers_db.get(phone_id)  # Fetch phone by ID
    if not phone:
        raise HTTPException(status_code=404, detail="Phone number not found.")
    
    # Update fields of the phone number with the provided values
    updated_data = phone_update.dict(exclude_unset=True)  # Only update provided fields
    
    # Add to the immutable history if last_used is being updated
    if 'last_used' in updated_data:
        phone.last_used_history.append({
            "timestamp": updated_data['last_used'],
            "ip": client_ip,
            "action": "used"
        })
    
    # Add to the immutable history if last_tried is being updated
    if 'last_tried' in updated_data:
        phone.last_tried_history.append({
            "timestamp": updated_data['last_tried'],
            "ip": client_ip,
            "action": "tried"
        })
    
    updated_phone = phone.copy(update={**updated_data, "updated_ip": client_ip})  # Create updated phone object
    phone_numbers_db[phone_id] = updated_phone  # Save updated phone to the database
    
    # Save updated data to JSON file
    save_phone_numbers_to_file(phone_numbers_db)

    print(f"Phone number {phone_id} updated from IP: {client_ip}")
    return updated_phone

# Delete a phone number entry
@router.delete("/{phone_id}", response_model=dict)
async def delete_phone_number(phone_id: UUID, request: Request):
    client_ip = request.client.host  # Get client's IP address
    if phone_id in phone_numbers_db:
        del phone_numbers_db[phone_id]  # Remove the phone number from the database
        save_phone_numbers_to_file(phone_numbers_db)  # Save updated data to JSON file
        print(f"Phone number {phone_id} deleted from IP: {client_ip}")
        return {"detail": "Phone number deleted."}
    else:
        raise HTTPException(status_code=404, detail="Phone number not found.")

# ------------------------------------------------------
# Optional: Endpoint for Bulk User Upload (e.g., updating multiple phone numbers)
# ------------------------------------------------------

@router.post("/upload_calculations/")
async def upload_calculations(has_redeem_value: bool, number_of_points: int, request: Request):
    client_ip = request.client.host  # Get client's IP address
    # Bulk update all phone numbers with the provided redeem value and points
    for phone in phone_numbers_db.values():
        phone.has_redeem_value = has_redeem_value
        phone.number_of_points = number_of_points
    save_phone_numbers_to_file(phone_numbers_db)  # Save updated data to JSON file
    print(f"Bulk calculations uploaded from IP: {client_ip}")
    return {"detail": "Calculations updated for all phone numbers."}
