# database.py

from typing import Dict, List
from uuid import UUID
import os
import json
from models.index import PhoneNumber

# ------------------------------------------------------
# Filepaths for the JSON storage files
# ------------------------------------------------------
PHONE_NUMBERS_JSON_FILE = "phone_numbers_db.json"
GEMINI_TEMP_JSON_FILE = "gemini_flash8b_temp_db.json"

# ------------------------------------------------------
# Load data from JSON files if they exist
# ------------------------------------------------------
def load_phone_numbers_from_file() -> Dict[UUID, PhoneNumber]:
    if os.path.exists(PHONE_NUMBERS_JSON_FILE):
        with open(PHONE_NUMBERS_JSON_FILE, "r") as file:
            try:
                data = json.load(file)
                # Convert back into proper UUID and datetime objects
                return {UUID(k): PhoneNumber(**v) for k, v in data.items()}
            except json.JSONDecodeError:
                return {}
    return {}

def load_gemini_temp_from_file() -> Dict[str, List[str]]:
    if os.path.exists(GEMINI_TEMP_JSON_FILE):
        with open(GEMINI_TEMP_JSON_FILE, "r") as file:
            try:
                data = json.load(file)
                return data  # {ip_address: [phone_numbers]}
            except json.JSONDecodeError:
                return {}
    return {}

# ------------------------------------------------------
# Save data to JSON files
# ------------------------------------------------------
def save_phone_numbers_to_file(phone_db: Dict[UUID, PhoneNumber]):
    with open(PHONE_NUMBERS_JSON_FILE, "w") as file:
        # Convert UUID keys to strings for JSON compatibility
        json.dump({str(k): {**v.dict(), "id": str(v.id)} for k, v in phone_db.items()}, file, indent=4)

def save_gemini_temp_to_file(gemini_temp_db: Dict[str, List[str]]):
    with open(GEMINI_TEMP_JSON_FILE, "w") as file:
        json.dump(gemini_temp_db, file, indent=4)

# ------------------------------------------------------
# In-memory storage, backed by JSON files
# ------------------------------------------------------
phone_numbers_db = load_phone_numbers_from_file()
gemini_flash8b_temp_db = load_gemini_temp_from_file()
