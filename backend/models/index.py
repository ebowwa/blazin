# models.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
import re

# ------------------------------------------------------
# Pydantic Models for Request and Response validation
# ------------------------------------------------------

# Model for Phone Number with all details
class PhoneNumber(BaseModel):
    id: UUID = Field(default_factory=uuid4)  # Unique identifier for the phone number
    number: str                              # Phone number string
    has_redeem_value: bool                   # Indicates if the number has a redeemable value
    last_used: Optional[datetime] = None     # Last time the number was used
    last_used_history: List[dict] = []       # History of all 'last_used' updates
    last_tried: Optional[datetime] = None    # Last time redeem was tried
    last_tried_history: List[dict] = []      # History of all 'last_tried' updates
    name: Optional[str] = None               # Name associated with the phone number
    amount_spent: float = 0.0                # Total amount spent
    number_of_points: int = 0                # Points accrued by the phone number
    notes: Optional[str] = None              # Optional notes about the phone number
    is_deleted: bool = False                 # Indicates if the phone number is deleted
    created_ip: Optional[str] = None         # IP address where the number was created
    updated_ip: Optional[str] = None         # IP address of last update

    # TODO: Add weekly limit

# Model for creating a new PhoneNumber (limited fields
class PhoneNumberCreate(BaseModel):
    number: str                              # Phone number string
    has_redeem_value: bool                   # Redeemable status
    name: Optional[str] = None               # Optional name to associate with the phone number
    notes: Optional[str] = None              # Optional notes about the phone number

    @validator('number')
    def validate_phone_number(cls, value):
        # Strip spaces, dashes, or parentheses
        clean_number = re.sub(r'\D', '', value)

        # Validate that the number is a valid USA number (10 digits, can start with optional +1)
        if len(clean_number) == 11 and clean_number.startswith("1"):
            clean_number = clean_number[1:]  # Strip the country code if present
        if len(clean_number) != 10:
            raise ValueError("Invalid USA phone number. Please enter a valid 10-digit number.")
        
        # Format the phone number to XXX-XXX-XXXX
        formatted_number = f"{clean_number[:3]}-{clean_number[3:6]}-{clean_number[6:]}"
        return formatted_number

# Model for updating an existing PhoneNumber
class PhoneNumberUpdate(BaseModel):
    has_redeem_value: Optional[bool] = None  # Optionally update redeemable status
    last_used: Optional[datetime] = None     # Optionally update last used timestamp
    last_tried: Optional[datetime] = None    # Optionally update last tried timestamp
    name: Optional[str] = None               # Optionally update associated name
    amount_spent: Optional[float] = None     # Optionally update total amount spent
    number_of_points: Optional[int] = None   # Optionally update accrued points
    notes: Optional[str] = None              # Optionally update notes about the phone number
    is_deleted: Optional[bool] = None        # Optionally update deletion status

    # TODO: add weekly limit; use 2x/week only

# Pydantic Model for Base64 Image Input
class Base64ImageInput(BaseModel):
    image_base64: str  # The base64-encoded image string
    file_name: Optional[str] = None  # Optional original filename
